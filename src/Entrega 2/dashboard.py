import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime
from datetime import timedelta
# --- (REMOVIDO) imports do Pareto (go e make_subplots) ---

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="PicMoney Dashboard")

# --- 1. LER O PERFIL DA URL ---
try:
    perfil_logado = st.query_params.get("profile")
    if perfil_logado is None:
        perfil_logado = "CEO"
except:
    perfil_logado = "CEO" 

# --- 2. VERIFICAR SE O ACESSO É VÁLIDO ---
if perfil_logado not in ["CEO", "CFO"]:
    st.error("Acesso inválido ou perfil não reconhecido.")
    st.info("Por favor, faça o login através do portal para acessar o dashboard.")
    st.link_button("Ir para o Login", "http://localhost:5000")
    st.stop() 

# --- (REMOVIDO) ---
# O 'st.session_state.theme' foi removido.
# O 'if st.session_state.theme == 'dark':'... foi removido.

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
    try:
        data_path = os.path.join(os.path.dirname(__file__), 'data')
    except NameError:
        data_path = 'data'
        
    try:
        cadastro_df = pd.read_csv(os.path.join(data_path, 'base_de_cadastro_limpa.csv'), sep=';')
        massa_df = pd.read_csv(os.path.join(data_path, 'base_de_massa_de_teste_limpa.csv'), sep=';')
        pedestre_df = pd.read_csv(os.path.join(data_path, 'base_de_pedestre_simulada_limpa.csv'), sep=';')
        transacoes_df = pd.read_csv(os.path.join(data_path, 'base_de_transacoes_limpa.csv'), sep=';')
        
        transacoes_df['data'] = pd.to_datetime(transacoes_df['data'], format='%d/%m/%Y')
        
        transacoes_df['hora_str'] = transacoes_df['hora'].astype(str)
        transacoes_df['hora_limpa'] = transacoes_df['hora_str'].str.extract(r'(\d+)').fillna('0')
        transacoes_df['hora'] = pd.to_numeric(transacoes_df['hora_limpa'])
        transacoes_df = transacoes_df.drop(columns=['hora_str', 'hora_limpa'])
        
        try:
            massa_df['data_captura'] = pd.to_datetime(massa_df['data_captura'], format='%d/%m/%Y %H:%M:%S')
        except ValueError:
            massa_df['data_captura'] = pd.to_datetime(massa_df['data_captura'], format='%d/%m/%Y')

        transacoes_df['valor_cupom'] = transacoes_df['valor_cupom'].astype(str).str.replace(',', '.').astype(float)
        transacoes_df['repasse_picmoney'] = transacoes_df['repasse_picmoney'].astype(str).str.replace(',', '.').astype(float)
        massa_df['valor_compra'] = massa_df['valor_compra'].astype(str).str.replace(',', '.').astype(float)
        
        return cadastro_df, massa_df, pedestre_df, transacoes_df
    
    except Exception as e:
        st.error(f"Erro inesperado ao carregar os dados: {e}")
        st.error("Verifique se a pasta 'data' e os arquivos CSV estão no mesmo diretório do script.")
        return None, None, None, None

# Carrega os dados
cadastro_df, massa_df, pedestre_df, transacoes_df = load_data()

if cadastro_df is None:
    st.stop()
    
# --- 4. BARRA LATERAL (Simplificada) ---
with st.sidebar:
    st.title("Executive")
    st.write("Geo Dashboard")
    st.write("") 
    
    default_index = 0 if perfil_logado == "CEO" else 1
    opcoes = ["Visão Geral (CEO)", "Financeiro (CFO)", "Alertas"]
    
    pagina_selecionada = st.radio(
        "Navegação",
        opcoes,
        index=default_index,
        label_visibility="collapsed"
    )
    
    st.write("---")

    # --- (REMOVIDO) ---
    # O 'st.toggle' do Modo Escuro foi removido.

    st.link_button("Sair (Logout)", "http://localhost:5000", type="secondary")

# --- 5. INJEÇÃO DO CSS (Sidebar + Novos Cards) ---
st.markdown(f"""
<style>
    /* Sidebar (fixa no escuro) */
    [data-testid="stSidebar"] {{
        background-color: #0F172A;
        color: #FFFFFF;
    }}
    
    /* Texto do Rádio na Sidebar (MAIÚSCULO, NEGRITO, BRANCO) */
    [data-testid="stSidebar"] div[role="radiogroup"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {{
         color: #FFFFFF !important;
         font-weight: 700 !important;
         text-transform: uppercase !important;
    }}
    
    /* --- CSS para Cards de KPI --- */
    
    /* Remove o padding de cima do st.metric para grudar no título */
    [data-testid="stMetric"] {{
        padding-top: 0px !important;
    }}
    
    /* Estiliza o container (o "card") */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border: 1px solid #E0E0E0;
    }}
    
    /* Alinha o ícone e o título */
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {{
        align-items: center;
    }}

</style>
""", unsafe_allow_html=True)


# --- Conteúdo Principal do Dashboard ---
st.title("Dashboard Interativo - PicMoney")
st.write("Visão estratégica e análise de desempenho em tempo real")

# --- Container dos Filtros ---
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1]) 
with col_f1:
    data_min_original = transacoes_df['data'].min().date()
    data_max_original = transacoes_df['data'].max().date()
    data_selecionada = st.date_input(
        "Período", (data_min_original, data_max_original), 
        min_value=data_min_original, max_value=data_max_original, 
        format="DD/MM/YYYY"
    )
with col_f2:
    bairros_unicos = ['Todos'] + sorted(transacoes_df['bairro_estabelecimento'].unique().tolist())
    bairro_selecionado = st.selectbox("Região (Bairro)", bairros_unicos)
with col_f3:
    parceiros_unicos = ['Todos'] + sorted(transacoes_df['nome_estabelecimento'].unique().tolist())
    parceiro_selecionado = st.selectbox("Parceiro", parceiros_unicos)

with col_f4:
    st.write("‎") # Espaço invisível para alinhar
    st.button("Aplicar Filtros")

# --- LÓGICA DE FILTRAGEM ---
if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    data_inicio = data_selecionada[0]
    data_fim = data_selecionada[1]
else:
    data_inicio = data_min_original
    data_fim = data_max_original

df_transacoes_filtrado = transacoes_df[
    (transacoes_df['data'].dt.date >= data_inicio) & (transacoes_df['data'].dt.date <= data_fim)
]
df_massa_filtrado = massa_df[
    (massa_df['data_captura'].dt.date >= data_inicio) & (massa_df['data_captura'].dt.date <= data_fim)
]
if bairro_selecionado != 'Todos':
    df_transacoes_filtrado = df_transacoes_filtrado[
        df_transacoes_filtrado['bairro_estabelecimento'] == bairro_selecionado
    ]
if parceiro_selecionado != 'Todos':
    df_transacoes_filtrado = df_transacoes_filtrado[
        df_transacoes_filtrado['nome_estabelecimento'] == parceiro_selecionado
    ]
    df_massa_filtrado = df_massa_filtrado[
        df_massa_filtrado['nome_loja'] == parceiro_selecionado
    ]

# --- LÓGICA DE PERÍODO (MANHÃ/TARDE/NOITE) ---
bins = [-1, 5, 11, 17, 23] # Madrugada (0-5), Manhã (6-11), Tarde (12-17), Noite (18-23)
labels = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
df_transacoes_filtrado['periodo_dia'] = pd.cut(df_transacoes_filtrado['hora'], bins=bins, labels=labels, right=True)

st.write("---") # Linha separadora

# --- 7. CONTEÚDO BASEADO NA SELEÇÃO DO SIDEBAR (COM TEMA) ---

if pagina_selecionada == "Visão Geral (CEO)":
    st.subheader("Visão Estratégica (CEO)")
    st.divider() # Linha que você adicionou
    
    # --- Cálculos de KPI (Taxa de Ativação) ---
    usuarios_ativos_diarios = df_transacoes_filtrado.groupby(
        df_transacoes_filtrado['data'].dt.date
    )['celular'].nunique().mean()
    total_sessoes = len(df_transacoes_filtrado)
    total_usuarios_unicos = df_transacoes_filtrado['celular'].nunique()
    sessoes_por_usuario = total_sessoes / total_usuarios_unicos if total_usuarios_unicos > 0 else 0
    top_categoria = df_transacoes_filtrado['categoria_estabelecimento'].mode().iloc[0] if not df_transacoes_filtrado.empty else "N/A"
    
    total_usuarios_cadastrados = len(cadastro_df)
    total_usuarios_ativos_no_periodo = df_transacoes_filtrado['celular'].nunique()
    taxa_de_ativacao = (total_usuarios_ativos_no_periodo / total_usuarios_cadastrados) * 100 if total_usuarios_cadastrados > 0 else 0
    
    # --- KPI Cards (Com "Taxa de Ativação") ---
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        with st.container(border=True): 
            st.metric(label="Usuários Ativos (Média Diária)", value=f"{usuarios_ativos_diarios:,.0f}")
    with col_kpi2:
        with st.container(border=True):
            st.metric(label="Taxa de Ativação", value=f"{taxa_de_ativacao:,.2f}%")
    with col_kpi3:
        with st.container(border=True):
            st.metric(label="Sessões por Usuário", value=f"{sessoes_por_usuario:,.2f}")
    with col_kpi4:
        with st.container(border=True):
            st.metric(label="Top Categoria", value=top_categoria)

    st.write("---") 

    # --- Linha 1 de Gráficos (Evolução + Top 5 Pizza) ---
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        with st.container(border=True):
            st.subheader("Evolução de Transações por Dia")
            evolucao_transacoes = df_transacoes_filtrado.groupby(
                df_transacoes_filtrado['data'].dt.date
            ).size().reset_index(name='Total de Transações')
            fig_evolucao = px.line(evolucao_transacoes, x='data', y='Total de Transações')
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
    with col_g2:
        with st.container(border=True):
            st.subheader("Top 5 Categorias")
            dist_categoria = df_transacoes_filtrado['categoria_estabelecimento'].value_counts()
            top_5_df = dist_categoria.nlargest(5).reset_index()
            top_5_df.columns = ['Categoria', 'Total']
            cores_vibrantes = ['#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
            fig_pie = px.pie(top_5_df, names='Categoria', values='Total', hole=0.4, 
                             title="TOP 5 CATEGORIAS.",
                             color_discrete_sequence=cores_vibrantes)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    st.write("---") 

    # --- Nova Linha 2 de Gráficos (Período + Tipo de Cupom) ---
    col_g3, col_g4 = st.columns(2) 
    
    with col_g3:
        with st.container(border=True):
            st.subheader("Distribuição por Período do Dia")
            dist_periodo = df_transacoes_filtrado['periodo_dia'].value_counts().reset_index()
            dist_periodo.columns = ['Período', 'Total']
            fig_periodo = px.bar(dist_periodo, y='Período', x='Total', 
                                 title="Total de Transações por Período", 
                                 orientation='h')
            st.plotly_chart(fig_periodo, use_container_width=True)
            
    with col_g4:
        with st.container(border=True):
            st.subheader("Distribuição por Tipo de Cupom")
            dist_cupom = df_transacoes_filtrado['tipo_cupom'].value_counts().reset_index()
            dist_cupom.columns = ['Tipo de Cupom', 'Total']
            cores_vibrantes_cupom = ['#00CC96', '#EF553B', '#AB63FA', '#FFA15A', '#19D3F3']
            fig_pie_cupom = px.pie(dist_cupom, names='Tipo de Cupom', values='Total', 
                                   hole=0.4, title="Transações por Tipo de Cupom",
                                   color_discrete_sequence=cores_vibrantes_cupom)
            st.plotly_chart(fig_pie_cupom, use_container_width=True)

    st.write("---") 

    # --- Nova Linha 3 (Gráfico de Hora como Linha) ---
    with st.container(border=True):
        st.subheader("Análise Temporal (Performance por Hora do Dia)")
        transacoes_por_hora = df_transacoes_filtrado.groupby(
            'hora'
        ).size().reset_index(name='Total de Transações')
        
        fig_hora = px.line(transacoes_por_hora, x='hora', y='Total de Transações', title="Total de Transações por Hora do Dia")
        fig_hora.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig_hora, use_container_width=True)
        
elif pagina_selecionada == "Financeiro (CFO)":
    st.subheader("Visão Financeira (CFO)")
    
    # Cálculos de KPI
    receita_liquida = df_transacoes_filtrado['repasse_picmoney'].sum()
    valor_total_cupons = df_transacoes_filtrado['valor_cupom'].sum()
    margem_op = (receita_liquida / valor_total_cupons) * 100 if valor_total_cupons > 0 else 0
    ticket_medio = df_massa_filtrado['valor_compra'].mean() if not df_massa_filtrado.empty else 0
    
    # KPI Cards (Com estilo de 'card')
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        with st.container(border=True):
            st.metric("Receita Líquida (Repasse)", f"R$ {receita_liquida:,.2f}")
    with col_kpi2:
        with st.container(border=True):
            st.metric("Margem (Repasse/Cupons)", f"{margem_op:,.2f}%")
    with col_kpi3:
        with st.container(border=True):
            st.metric("Ticket Médio (Compras)", f"R$ {ticket_medio:,.2f}")
    with col_kpi4:
        with st.container(border=True):
            st.metric("Valor Total Cupons (Custo)", f"R$ {valor_total_cupons:,.2f}")
        
    st.write("---")
    st.subheader("Análises Financeiras")
    col_g_cfo1, col_g_cfo2 = st.columns(2)
    
    # --- MUDANÇA (Gráfico de Barras Top 10) ---
    with col_g_cfo1:
        with st.container(border=True):
            st.subheader("Top 10 Receita (Repasse) por Categoria")
            
            # 1. Pega os dados
            receita_categoria = df_transacoes_filtrado.groupby(
                'categoria_estabelecimento'
            )['repasse_picmoney'].sum().sort_values(ascending=False)
            
            # 2. Pega as 10 maiores
            top_10_receita_df = receita_categoria.nlargest(10).reset_index()
            
            # 3. Cria o gráfico de barras (simples)
            fig_bar_receita = px.bar(top_10_receita_df, 
                                     x='categoria_estabelecimento', 
                                     y='repasse_picmoney', 
                                     title="Top 10 Receita por Categoria")
            
            st.plotly_chart(fig_bar_receita, use_container_width=True)
    
    with col_g_cfo2:
        # --- (MANTIDO) Gráfico de Barras Colorido ---
        with st.container(border=True):
            st.subheader("Receita (Repasse) por Tipo de Cupom")
            receita_tipo_cupom = df_transacoes_filtrado.groupby(
                'tipo_cupom'
            )['repasse_picmoney'].sum().sort_values(ascending=False).reset_index()
            # Adicionado color='tipo_cupom' para dar cores
            fig_bar_cupom = px.bar(receita_tipo_cupom, x='tipo_cupom', y='repasse_picmoney', title="Receita por Tipo de Cupom", color='tipo_cupom')
            st.plotly_chart(fig_bar_cupom, use_container_width=True)

# --- 8. PÁGINA DE ALERTAS (COM TEMA) ---
elif pagina_selecionada == "Alertas":
    st.subheader("Alertas Inteligentes")
    st.write("Monitoramento de anomalias e KPIs críticos (baseado no histórico completo).")
    
    hoje = transacoes_df['data'].max()
    ontem = hoje - timedelta(days=1)
    
    st.info(f"Análise de alertas baseada nos dados até: {hoje.strftime('%d/%m/%Y')}")
    st.write("---")
    
    with st.container(border=True):
        st.header("Alerta de Transações Diárias")
        
        data_inicio_media = ontem - timedelta(days=7)
        transacoes_media_semanal_df = transacoes_df[
            (transacoes_df['data'] >= data_inicio_media) & (transacoes_df['data'] < ontem)
        ]
        transacoes_ontem_df = transacoes_df[transacoes_df['data'] == ontem]
        
        media_transacoes = transacoes_media_semanal_df.groupby('data').size().mean()
        total_transacoes_ontem = len(transacoes_ontem_df)
        
        variacao_transacoes = ((total_transacoes_ontem - media_transacoes) / media_transacoes) * 100 if media_transacoes > 0 else 0
        
        st.metric(
            "Transações de Ontem vs. Média 7 Dias",
            f"{total_transacoes_ontem:,.0f} transações",
            f"{variacao_transacoes:,.2f}%"
        )
        
        if variacao_transacoes < -20:
            st.error(
                f"Alerta Crítico: As transações de ontem ({total_transacoes_ontem:,.0f}) caíram {variacao_transacoes:,.2f}% "
                f"em comparação com a média dos 7 dias anteriores ({media_transacoes:,.0f}).",
                icon="🚨"
            )
        else:
            st.success("Performance de transações dentro do esperado.", icon="✅")

    st.write("---")

    with st.container(border=True):
        st.header("Alerta de Receita (Repasse)")
        
        media_repasse = transacoes_media_semanal_df.groupby('data')['repasse_picmoney'].sum().mean()
        repasse_ontem = transacoes_ontem_df['repasse_picmoney'].sum()
        
        variacao_repasse = ((total_transacoes_ontem - media_transacoes) / media_transacoes) * 100 if media_transacoes > 0 else 0
        
        st.metric(
            "Receita de Ontem vs. Média 7 Dias",
            f"R$ {repasse_ontem:,.2f}",
            f"{variacao_repasse:,.2f}%"
        )
        
        if variacao_repasse < -10:
            st.warning(
                f"Alerta de Atenção: A receita (repasse) de ontem (R$ {repasse_ontem:,.2f}) caiu {variacao_repasse:,.2f}% "
                f"em comparação com a média dos 7 dias anteriores (R$ {media_repasse:,.2f}).",
                icon="⚠️"
            )
        else:
            st.success("Performance de receita dentro do esperado.", icon="✅")