import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime
from datetime import timedelta
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu # <-- IMPORTAÇÃO DA NOVA BIBLIOTECA

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

# --- MUDANÇA (Voltamos ao particles.js original) ---
# Partículas de fundo (o seu código original)
particles_background = """
<style>
    #particles-js {
        position: fixed;
        width: 100%;
        height: 100%;
        z-index: -1;
        top: 0;
        left: 0;
    }
</style>
<div id="particles-js"></div>
<script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
<script>
particlesJS("particles-js", {
    "particles": {
        "number": {
            "value": 150,
            "density": {
                "enable": true,
                "value_area": 800
            }
        },
        "color": {
            "value": "#18B50A"
        },
        "shape": {
            "type": "triangle" /* --- MUDANÇA (Forma Diferente) --- */
        },
        "opacity": {
            "value": 0.9,
            "random": false
        },
        "size": {
            "value": 3,
            "random": true
        },
        "line_linked": {
            "enable": true,
            "distance": 150,
            "color": "#0DA2E7",
            "opacity": 1,
            "width": 1
        },
        "move": {
            "enable": true,
            "speed": 1,
            "direction": "none",
            "out_mode": "out"
        }
    },
    "interactivity": {
        "events": {
            "onhover": {
                "enable": true,
                "mode": "repulse"
            },
            "onclick": {
                "enable": true,
                "mode": "push"
            }
        },
        "modes": {
            "repulse": {
                "distance": 100
            },
            "push": {
                "particles_nb": 4
            }
        }
    },
    "retina_detect": true
});
</script>
"""

# --- MUDANÇA (Voltamos para a altura original) ---
# Usando o seu height=150 original, que funcionava
components.html(particles_background, height=150, width=2000, scrolling=False)


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
    # 1. Títulos no topo
    st.title("DashUP")
    st.write("Executive Dashboard")
    
    st.markdown("---") # Separador

    # 3. NAVEGAÇÃO (COM O NOVO COMPONENTE)
    default_index = 0 if perfil_logado == "CEO" else 1
    
    pagina_selecionada = option_menu(
        menu_title=None, # Esconde o título "Navegação"
        options=["Visão Geral (CEO)", "Financeiro (CFO)", "Alertas"],
        icons=["house", "bar-chart-fill", "bell"], # Ícones do Bootstrap
        default_index=default_index,
        styles={
            "container": {"padding": "0!important", "background-color": "#030C59"}, # Fundo do container
            "icon": {"color": "white", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "12px",
                "text-align": "left",
                "margin":"0px",
                "color": "#FFFFFF", # Cor do texto não selecionado
                "text-transform": "uppercase",
                "font-weight": "1000",
                "--hover-color": "rgba(255, 255, 255, 0.1)" # Cor do hover
            },
            "nav-link-selected": {
                "background-color": "#4B5563", # Cor do item selecionado
                "color": "#FFFFFF", # Cor do texto selecionado
            },
        }
    )
    
    # 4. Separador
    st.write("---")

    # 5. Botão de Sair (como texto)
    st.markdown(
        '<a href="http://localhost:5000" target="_self" style="color: #CCCCCC; text-decoration: none; font-size: 14px; padding-left: 15px;">Sair (Logout)</a>',
        unsafe_allow_html=True
    )

# --- 5. INJEÇÃO DO CSS (Sidebar + Novos Cards) ---
st.markdown(f"""
<style>

/* --- REGRAS PARA O TOPO DA SIDEBAR (MAIS AGRESSIVO) --- */
[data-testid="stSidebar"] > div:nth-child(1) > div:nth-child(1) {{
    padding-top: 0px !important; 
}}
[data-testid="stSidebar"] [data-testid="stHeading"] h1 {{
     margin-top: 0px !important;
     padding-top: 0px !important; 
}}
[data-testid="stSidebar"] [data-testid="stHeading"] {{
    margin-bottom: 0px !important; 
}}
/* ------------------------------------ */


/* --- Títulos Principais --- */
    h1 {{ /* "Dashboard Interativo - PicMoney" */
        color: #FF0000;
        font-size: 70px !important; 
    }}
    h3 {{ /* "Visão Estratégica (CEO)", "Top 5 Categorias", etc. */
        color: #334155;
        font-size: 24px !important; 
    }}
    h2 {{ /* st.header, como em "Alerta de Transações Diárias" */
        color: #FFD700; 
        font-size: 28px !important; 
    }}


/* --- Texto st.write() e st.info() --- */
p {{
    font-size: 30px !important; 
    color: #E0E0E0 !important; 
}}


 

/* --- Rótulos de Filtros (st.selectbox, st.date_input) --- */
.st-emotion-cache-nahz7x, .st-emotion-cache-f1g6gs {{ 
    font-size: 16px !important; 
    color: #E0E0E0 !important; 
    font-weight: bold !important; 
}}


/* --- Cards de KPI (st.metric) --- */

/* Rótulos dos KPIs: "Usuários Ativos (Média Diária)", "Taxa de Ativação", etc. */
[data-testid="stMetric"] label, [data-testid="stMetricLabel"] p {{
    color: #CCCCCC !important; 
    font-size: 12px !important; 
    font-weight: 500 !important; 
}}

/* Números grandes dos KPIs (o valor) */
[data-testid="stMetric"] [data-testid="stMetricValue"] div {{
    color: #FFFFFF !important; 
    font-size: 40px !important; 
    font-weight: bold !important;
}}


/* Sidebar (fixa no escuro) */
[data-testid="stSidebar"] {{
    background-color: #030C59;
    color: #FFFFFF;
}}

/* Títulos "DashUP" e "Executive Dashboard" na sidebar */
[data-testid="stSidebar"] [data-testid="stHeading"] h1 {{
    font-size: 28px !important; 
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] p:nth-of-type(1) {{ /* Para o "Executive Dashboard" logo abaixo do title */
    font-size: 16px !important;
    color: #DDDDDD !important;
}}


/* --- CSS para Cards de KPI (borda e sombra) --- */
[data-testid="stMetric"] {{
    padding-top: 0px !important;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    border: 1px solid #333333; 
    background-color: #1A202C; 
}}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {{
    align-items: center;
}}

</style>
""", unsafe_allow_html=True)


# --- Conteúdo Principal do Dashboard ---
st.title("Dashboard Interativo - PicMoney")
st.write("Visão estratégica e análise de desempenho em tempo real")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")

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
    st.write("")
    
    # --- MUDANÇA: Lógica de Cálculo de KPI e Delta ---
    
    # 1. Definir Período B (Atual - dos filtros) e A (Anterior)
    periodo_B_inicio = data_inicio
    periodo_B_fim = data_fim
    periodo_duracao = (periodo_B_fim - periodo_B_inicio).days
    
    if periodo_duracao == 0:
        periodo_duracao = 1 
    
    periodo_A_fim = periodo_B_inicio - timedelta(days=1)
    periodo_A_inicio = periodo_A_fim - timedelta(days=periodo_duracao - 1) 

    # 2. DataFrame do Período Anterior (usando o DF *completo*)
    df_periodo_A = transacoes_df[
        (transacoes_df['data'].dt.date >= periodo_A_inicio) &
        (transacoes_df['data'].dt.date <= periodo_A_fim)
    ]
    
    # --- Cálculos de KPI (Período B - Atual) ---
    usuarios_ativos_diarios_B = df_transacoes_filtrado.groupby(
        df_transacoes_filtrado['data'].dt.date
    )['celular'].nunique().mean()
    if pd.isna(usuarios_ativos_diarios_B): usuarios_ativos_diarios_B = 0
    
    total_sessoes_B = len(df_transacoes_filtrado)
    total_usuarios_unicos_B = df_transacoes_filtrado['celular'].nunique()
    sessoes_por_usuario_B = total_sessoes_B / total_usuarios_unicos_B if total_usuarios_unicos_B > 0 else 0
    total_transacoes_B = len(df_transacoes_filtrado)
    
    total_usuarios_cadastrados = len(cadastro_df)
    taxa_de_ativacao_B = (total_usuarios_unicos_B / total_usuarios_cadastrados) * 100 if total_usuarios_cadastrados > 0 else 0

    # --- Cálculos de KPI (Período A - Anterior) ---
    usuarios_ativos_diarios_A = df_periodo_A.groupby(
        df_periodo_A['data'].dt.date
    )['celular'].nunique().mean()
    if pd.isna(usuarios_ativos_diarios_A): usuarios_ativos_diarios_A = 0
    
    total_sessoes_A = len(df_periodo_A)
    total_usuarios_unicos_A = df_periodo_A['celular'].nunique()
    sessoes_por_usuario_A = total_sessoes_A / total_usuarios_unicos_A if total_usuarios_unicos_A > 0 else 0
    total_transacoes_A = len(df_periodo_A)

    # --- Calcular Deltas ---
    
    # Delta DAU
    if usuarios_ativos_diarios_A > 0:
        delta_dau = ((usuarios_ativos_diarios_B - usuarios_ativos_diarios_A) / usuarios_ativos_diarios_A) * 100
        delta_dau_str = f"{delta_dau:,.1f}%"
    else:
        delta_dau_str = None # Não mostra delta se não houver dados anteriores

    # Delta Sessões por Usuário
    if sessoes_por_usuario_A > 0:
        delta_sessoes = ((sessoes_por_usuario_B - sessoes_por_usuario_A) / sessoes_por_usuario_A) * 100
        delta_sessoes_str = f"{delta_sessoes:,.1f}%"
    else:
        delta_sessoes_str = None

    # Delta Total de Transações
    if total_transacoes_A > 0:
        delta_transacoes = ((total_transacoes_B - total_transacoes_A) / total_transacoes_A) * 100
        delta_transacoes_str = f"{delta_transacoes:,.1f}%"
    else:
        delta_transacoes_str = None
    
    
    # --- MUDANÇA: KPI Cards (Layout 1x4 com Deltas) ---
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        with st.container(border=True): 
            st.metric(label="DAU (Usuários Ativos Diários)", value=f"{usuarios_ativos_diarios_B:,.0f}", delta=delta_dau_str)
    with col_kpi2:
        with st.container(border=True):
            st.metric(label="Taxa de Ativação (Período)", value=f"{taxa_de_ativacao_B:,.2f}%", help="Usuários ativos no período / Total de usuários cadastrados.")
    with col_kpi3:
        with st.container(border=True):
            st.metric(label="Sessões por Usuário (Período)", value=f"{sessoes_por_usuario_B:,.2f}", delta=delta_sessoes_str)
    with col_kpi4:
        with st.container(border=True):
            st.metric(label="Total de Transações", value=f"{total_transacoes_B:,.0f}", delta=delta_transacoes_str)


    st.write("---") 

    # --- Gráfico de Evolução de Usuários Ativos (DAU/WAU/MAU) ---
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        with st.container(border=True):
            st.subheader("Evolução de Usuários Ativos") 
            
            agrupamento = st.radio(
                "Agrupar por:",
                ("Diário", "Semanal", "Mensal"),
                horizontal=True,
                label_visibility="collapsed",
                key="agrupamento_usuarios"
            )
            
            df_plot = df_transacoes_filtrado.copy()
            
            if agrupamento == "Diário":
                df_agg = df_plot.groupby(df_plot['data'].dt.date)['celular'].nunique().reset_index()
                df_agg = df_agg.rename(columns={'data':'Data', 'celular':'Usuários Ativos'})
                x_axis = 'Data'
            elif agrupamento == "Semanal":
                df_agg = df_plot.set_index('data').resample('W-Mon')['celular'].nunique().reset_index()
                df_agg = df_agg.rename(columns={'data':'Semana', 'celular':'Usuários Ativos'})
                x_axis = 'Semana'
            else: # Mensal
                df_agg = df_plot.set_index('data').resample('MS')['celular'].nunique().reset_index()
                df_agg = df_agg.rename(columns={'data':'Mês', 'celular':'Usuários Ativos'})
                x_axis = 'Mês'
            
            fig_evolucao = px.line(df_agg, x=x_axis, y='Usuários Ativos', title=f"Usuários Ativos ({agrupamento})")
            fig_evolucao.update_layout(legend_font_size=12)
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
    with col_g2:
        with st.container(border=True):
            st.subheader("Top 5 Categorias")
            dist_categoria = df_transacoes_filtrado['categoria_estabelecimento'].value_counts()
            top_5_df = dist_categoria.nlargest(5).reset_index()
            top_5_df.columns = ['Categoria', 'Total']
            cores_vibrantes = ['#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
            fig_pie = px.pie(top_5_df, names='Categoria', values='Total', hole=0.4, 
                             title="Categorias com Mais Transações",
                             color_discrete_sequence=cores_vibrantes)
            
            fig_pie.update_layout(legend_font_size=14)
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
            
            fig_periodo.update_layout(legend_font_size=16)
            
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
            
            fig_pie_cupom.update_layout(legend_font_size=16)
            
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
        
        fig_hora.update_layout(legend_font_size=16)
        
        st.plotly_chart(fig_hora, use_container_width=True)
        
elif pagina_selecionada == "Financeiro (CFO)":
    st.subheader("Visão Financeira (CFO)")
    
    # --- MUDANÇA: Adicionando Deltas na Visão do CFO ---
    
    # 1. Definir Período B (Atual - dos filtros) e A (Anterior)
    periodo_B_inicio = data_inicio
    periodo_B_fim = data_fim
    periodo_duracao = (periodo_B_fim - periodo_B_inicio).days
    
    if periodo_duracao == 0:
        periodo_duracao = 1 
    
    periodo_A_fim = periodo_B_inicio - timedelta(days=1)
    periodo_A_inicio = periodo_A_fim - timedelta(days=periodo_duracao - 1) 

    # 2. DataFrame do Período Anterior (usando o DF *completo*)
    df_periodo_A_trans = transacoes_df[
        (transacoes_df['data'].dt.date >= periodo_A_inicio) &
        (transacoes_df['data'].dt.date <= periodo_A_fim)
    ]
    df_periodo_A_massa = massa_df[
        (massa_df['data_captura'].dt.date >= periodo_A_inicio) &
        (massa_df['data_captura'].dt.date <= periodo_A_fim)
    ]
    
    # Cálculos de KPI (Período B - Atual)
    receita_liquida_B = df_transacoes_filtrado['repasse_picmoney'].sum()
    valor_total_cupons_B = df_transacoes_filtrado['valor_cupom'].sum()
    margem_op_B = (receita_liquida_B / valor_total_cupons_B) * 100 if valor_total_cupons_B > 0 else 0
    ticket_medio_B = df_massa_filtrado['valor_compra'].mean() if not df_massa_filtrado.empty else 0
    
    # Cálculos de KPI (Período A - Anterior)
    receita_liquida_A = df_periodo_A_trans['repasse_picmoney'].sum()
    valor_total_cupons_A = df_periodo_A_trans['valor_cupom'].sum()
    margem_op_A = (receita_liquida_A / valor_total_cupons_A) * 100 if valor_total_cupons_A > 0 else 0
    ticket_medio_A = df_periodo_A_massa['valor_compra'].mean() if not df_periodo_A_massa.empty else 0

    # Calcular Deltas
    delta_receita_str = f"{(receita_liquida_B - receita_liquida_A):,.2f}" if receita_liquida_A > 0 else None
    delta_margem_str = f"{(margem_op_B - margem_op_A):,.1f}%" if margem_op_A > 0 else None
    delta_ticket_str = f"{(ticket_medio_B - ticket_medio_A):,.2f}" if ticket_medio_A > 0 else None
    delta_cupons_str = f"{(valor_total_cupons_B - valor_total_cupons_A):,.2f}" if valor_total_cupons_A > 0 else None
    
    # KPI Cards (Com estilo de 'card')
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        with st.container(border=True):
            st.metric("Receita Líquida (Repasse)", f"R$ {receita_liquida_B:,.2f}", delta=delta_receita_str)
    with col_kpi2:
        with st.container(border=True):
            st.metric("Margem (Repasse/Cupons)", f"{margem_op_B:,.2f}%", delta=delta_margem_str)
    with col_kpi3:
        with st.container(border=True):
            st.metric("Ticket Médio (Compras)", f"R$ {ticket_medio_B:,.2f}", delta=delta_ticket_str)
    with col_kpi4:
        with st.container(border=True):
            st.metric("Valor Total Cupons (Custo)", f"R$ {valor_total_cupons_B:,.2f}", delta=delta_cupons_str, delta_color="inverse")
            
    st.write("---")
    st.subheader("Análises Financeiras")
    col_g_cfo1, col_g_cfo2 = st.columns(2)
    
    # --- (MUDANÇA) Gráfico de Barras Top 10 ---
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
            
            fig_bar_receita.update_layout(legend_font_size=16)
            
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
            
            fig_bar_cupom.update_layout(legend_font_size=16)
            
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