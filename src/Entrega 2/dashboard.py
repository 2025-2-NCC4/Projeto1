import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime # Precisaremos para o filtro de data

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="PicMoney Dashboard")

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    try:
        cadastro_df = pd.read_csv(os.path.join(data_path, 'base_de_cadastro_limpa.csv'), sep=';')
        massa_df = pd.read_csv(os.path.join(data_path, 'base_de_massa_de_teste_limpa.csv'), sep=';')
        pedestre_df = pd.read_csv(os.path.join(data_path, 'base_de_pedestre_simulada_limpa.csv'), sep=';')
        transacoes_df = pd.read_csv(os.path.join(data_path, 'base_de_transacoes_limpa.csv'), sep=';')
        
        # --- Conversão de Dados ---
        transacoes_df['data'] = pd.to_datetime(transacoes_df['data'], format='%d/%m/%Y')
        
        try:
            massa_df['data_captura'] = pd.to_datetime(massa_df['data_captura'], format='%d/%m/%Y %H:%M:%S')
        except ValueError:
            massa_df['data_captura'] = pd.to_datetime(massa_df['data_captura'], format='%d/%m/%Y')

        # --- Tratamento de colunas numéricas (CORREÇÃO) ---
        # 1. Converte a coluna para string (para garantir que .str funcione)
        # 2. Substitui vírgula por ponto
        # 3. Converte para float
        transacoes_df['valor_cupom'] = transacoes_df['valor_cupom'].astype(str).str.replace(',', '.').astype(float)
        transacoes_df['repasse_picmoney'] = transacoes_df['repasse_picmoney'].astype(str).str.replace(',', '.').astype(float)
        massa_df['valor_compra'] = massa_df['valor_compra'].astype(str).str.replace(',', '.').astype(float)
        
        return cadastro_df, massa_df, pedestre_df, transacoes_df
    
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar os dados: Arquivo não encontrado.")
        st.error(e)
        return None, None, None, None
    except Exception as e:
        st.error(f"Erro inesperado ao carregar os dados: {e}")
        return None, None, None, None

# Carrega os dados
cadastro_df, massa_df, pedestre_df, transacoes_df = load_data()

if cadastro_df is None:
    st.stop()
    
# --- CSS Customizado para o Sidebar ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] .st-emotion-cache-17lntkn {
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-root"] > div {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Barra Lateral (Sidebar) de Navegação ---
with st.sidebar:
    st.title("Executive")
    st.write("Geo Dashboard")
    st.write("") 

    pagina_selecionada = st.radio(
        "Visões",
        ["Visão Estratégica (CEO)", "Visão Financeira (CFO)"],
        label_visibility="collapsed"
    )
    
    st.write("---")
    st.link_button("Sair (Logout)", "http://localhost:5000", type="secondary")

# --- Conteúdo Principal do Dashboard ---

st.title("Dashboard Interativo - PicMoney")
st.write("Visão estratégica e análise de desempenho em tempo real")

# --- FILTROS ---
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    data_min = transacoes_df['data'].min().date()
    data_max = transacoes_df['data'].max().date()
    
    # Corrigindo o widget de data para aceitar tupla de datas
    data_selecionada = st.date_input(
        "Período",
        (data_min, data_max), # Valor inicial (tupla com min e max)
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

with col_f2:
    bairros_unicos = ['Todos'] + sorted(transacoes_df['bairro_estabelecimento'].unique().tolist())
    bairro_selecionado = st.selectbox("Região (Bairro)", bairros_unicos)

with col_f3:
    parceiros_unicos = ['Todos'] + sorted(transacoes_df['nome_estabelecimento'].unique().tolist())
    parceiro_selecionado = st.selectbox("Parceiro", parceiros_unicos)

# --- LÓGICA DE FILTRAGEM ---
# O dashboard vai re-rodar e filtrar automaticamente toda vez que um filtro for alterado

# 1. Tratar o filtro de data (garantir que temos um início e fim)
if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    data_inicio = data_selecionada[0]
    data_fim = data_selecionada[1]
else:
    # Caso padrão se o filtro de data não retornar uma tupla (ex: usuário só selecionou 1 dia)
    data_inicio = data_min
    data_fim = data_max

# 2. Aplicar os filtros aos DataFrames
# Usaremos principalmente 'transacoes_df' e 'massa_df' para os KPIs

df_transacoes_filtrado = transacoes_df[
    (transacoes_df['data'].dt.date >= data_inicio) &
    (transacoes_df['data'].dt.date <= data_fim)
]

df_massa_filtrado = massa_df[
    (massa_df['data_captura'].dt.date >= data_inicio) &
    (massa_df['data_captura'].dt.date <= data_fim)
]

if bairro_selecionado != 'Todos':
    df_transacoes_filtrado = df_transacoes_filtrado[
        df_transacoes_filtrado['bairro_estabelecimento'] == bairro_selecionado
    ]
    # (Você pode adicionar filtro de bairro para df_massa_filtrado se a coluna existir)
    
if parceiro_selecionado != 'Todos':
    df_transacoes_filtrado = df_transacoes_filtrado[
        df_transacoes_filtrado['nome_estabelecimento'] == parceiro_selecionado
    ]
    df_massa_filtrado = df_massa_filtrado[
        df_massa_filtrado['nome_loja'] == parceiro_selecionado
    ]
    
st.write("---") # Linha divisória

# --- Conteúdo baseado na seleção do Sidebar ---

if pagina_selecionada == "Visão Estratégica (CEO)":
    st.subheader("Visão Estratégica (CEO)")
    
    # --- CÁLCULO DOS KPIs REAIS (CEO) ---
    # Usamos df_transacoes_filtrado
    
    # Participação diária (DAU) - Contagem de celulares únicos nas transações
    usuarios_ativos_diarios = df_transacoes_filtrado.groupby(
        df_transacoes_filtrado['data'].dt.date
    )['celular'].nunique().mean()
    
    # Total de transações (sessões)
    total_sessoes = len(df_transacoes_filtrado)
    
    # Usuários únicos no período
    total_usuarios_unicos = df_transacoes_filtrado['celular'].nunique()
    
    # Sessões por Usuário
    sessoes_por_usuario = total_sessoes / total_usuarios_unicos if total_usuarios_unicos > 0 else 0
    
    # Top Categoria
    top_categoria = df_transacoes_filtrado['categoria_estabelecimento'].mode().iloc[0] if not df_transacoes_filtrado.empty else "N/A"

    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Usuários Ativos (Média Diária)", f"{usuarios_ativos_diarios:,.0f}")
    with col_kpi2:
        st.metric("Taxa de Retenção", "N/A") # Cálculo complexo, deixamos para depois
    with col_kpi3:
        st.metric("Sessões por Usuário", f"{sessoes_por_usuario:,.2f}")
    with col_kpi4:
        st.metric("Top Categoria", top_categoria)

    # --- GRÁFICOS REAIS (CEO) ---
    col_g1, col_g2 = st.columns([2, 1])
    
    with col_g1:
        st.subheader("Evolução de Transações por Dia")
        # Agrupa por data e conta o número de transações (linhas)
        evolucao_transacoes = df_transacoes_filtrado.groupby(
            df_transacoes_filtrado['data'].dt.date
        ).size().reset_index(name='Total de Transações')
        
        fig_evolucao = px.line(evolucao_transacoes, x='data', y='Total de Transações')
        st.plotly_chart(fig_evolucao, use_container_width=True)

    with col_g2:
        st.subheader("Distribuição por Categoria")
        # Agrupa por categoria e conta o número de transações
        dist_categoria = df_transacoes_filtrado['categoria_estabelecimento'].value_counts().reset_index(name='Total')
        
        fig_pie = px.pie(dist_categoria, names='categoria_estabelecimento', values='Total', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
elif pagina_selecionada == "Visão Financeira (CFO)":
    st.subheader("Visão Financeira (CFO)")
    
    # --- CÁLCULO DOS KPIs REAIS (CFO) ---
    
    # Receita Líquida (Repasse)
    receita_liquida = df_transacoes_filtrado['repasse_picmoney'].sum()
    
    # Valor Total dos Cupons (Custo)
    valor_total_cupons = df_transacoes_filtrado['valor_cupom'].sum()
    
    # Margem Operacional (Exemplo: Repasse / Custo Cupons)
    margem_op = (receita_liquida / valor_total_cupons) * 100 if valor_total_cupons > 0 else 0
    
    # Ticket Médio (das compras na base_massa_de_teste)
    ticket_medio = df_massa_filtrado['valor_compra'].mean()
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Receita Líquida (Repasse)", f"R$ {receita_liquida:,.2f}")
    with col_kpi2:
        st.metric("Margem (Repasse/Cupons)", f"{margem_op:,.2f}%")
    with col_kpi3:
        st.metric("Ticket Médio (Compras)", f"R$ {ticket_medio:,.2f}")
    with col_kpi4:
        st.metric("Valor Total Cupons (Custo)", f"R$ {valor_total_cupons:,.2f}")
        
    # --- GRÁFICOS REAIS (CFO) ---
    st.write("---")
    st.subheader("Análises Financeiras")
    
    col_g_cfo1, col_g_cfo2 = st.columns(2)
    
    with col_g_cfo1:
        st.subheader("Receita (Repasse) por Categoria")
        receita_categoria = df_transacoes_filtrado.groupby(
            'categoria_estabelecimento'
        )['repasse_picmoney'].sum().sort_values(ascending=False).reset_index()
        
        fig_bar_receita = px.bar(receita_categoria, x='categoria_estabelecimento', y='repasse_picmoney', title="Receita por Categoria")
        st.plotly_chart(fig_bar_receita, use_container_width=True)
        
    with col_g_cfo2:
        st.subheader("Receita (Repasse) por Tipo de Cupom")
        receita_tipo_cupom = df_transacoes_filtrado.groupby(
            'tipo_cupom'
        )['repasse_picmoney'].sum().sort_values(ascending=False).reset_index()
        
        fig_bar_cupom = px.bar(receita_tipo_cupom, x='tipo_cupom', y='repasse_picmoney', title="Receita por Tipo de Cupom")
        st.plotly_chart(fig_bar_cupom, use_container_width=True)