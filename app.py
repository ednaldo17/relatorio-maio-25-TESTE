import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Inserções de Rádio",
    page_icon="📻",
    layout="wide",
)

# --- Carregamento dos dados ---
# Carrega os dados do arquivo CSV local.
# Certifique-se de que o arquivo 'relatorio_mai.csv' está na mesma pasta.
try:
    df = pd.read_csv("relatorio MAI.csv")
except FileNotFoundError:
    st.error("Erro: O arquivo 'relatorio_mai.csv' não foi encontrado. Por favor, certifique-se de que ele está na mesma pasta que o script.")
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🤝 Filtros")

# Filtro de Cliente
clientes_disponiveis = sorted(df['Cliente'].unique())
clientes_selecionados = st.sidebar.multiselect("Cliente", clientes_disponiveis, default=clientes_disponiveis)

# NOVO: Filtro de Agência
# .dropna() remove valores vazios (NaN) da lista de opções do filtro.
agencias_disponiveis = sorted(df['Agência'].dropna().unique())
agencias_selecionadas = st.sidebar.multiselect("Agência", agencias_disponiveis, default=agencias_disponiveis)


# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
# A lógica de filtro para agência inclui os valores nulos (NaN) para que
# os clientes sem agência continuem aparecendo quando nenhuma agência for selecionada.
df_filtrado = df[
    (df['Cliente'].isin(clientes_selecionados)) &
    (df['Agência'].isin(agencias_selecionadas) | df['Agência'].isna())
]


# --- Conteúdo Principal ---
st.title("📊 Dashboard de Análise de Inserções")
st.markdown("Explore os dados de inserções de comerciais. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

# Calcula as métricas apenas se o dataframe filtrado não estiver vazio
if not df_filtrado.empty:
    media_insercoes = df_filtrado['Inserções'].mean()
    total_insercoes = df_filtrado['Inserções'].sum()
    total_clientes = df_filtrado['Cliente'].nunique()
    cliente_mais_frequente = df_filtrado.loc[df_filtrado['Inserções'].idxmax()]['Cliente']
else:
    media_insercoes, total_insercoes, total_clientes, cliente_mais_frequente = 0, 0, 0, "Nenhum"

# MUDANÇA: Formatação de número para o padrão brasileiro (ponto como separador)
def formatar_numero(num):
    return f"{num:,.0f}".replace(',', '.')

col1, col2, col3, col4 = st.columns(4)
col1.metric("Média de Inserções", formatar_numero(media_insercoes))
col2.metric("Total de Inserções", formatar_numero(total_insercoes))
col3.metric("Total de Clientes", formatar_numero(total_clientes))
col4.metric("Cliente Destaque", cliente_mais_frequente)


st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_clientes = df_filtrado.groupby('Cliente')['Inserções'].sum().nlargest(15).sort_values(ascending=True).reset_index()
        grafico_clientes = px.bar(
            top_clientes,
            x='Inserções',
            y='Cliente',
            orientation='h',
            title="Top 15 Clientes por Nº de Inserções",
            labels={'Inserções': 'Quantidade de Inserções', 'Cliente': ''}

