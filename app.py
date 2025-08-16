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
st.sidebar.header("🔍 Filtros")

# Filtro de Cliente
clientes_disponiveis = sorted(df['Cliente'].unique())
clientes_selecionados = st.sidebar.multiselect("Cliente", clientes_disponiveis, default=clientes_disponiveis)


# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[df['Cliente'].isin(clientes_selecionados)]


# --- Conteúdo Principal ---
st.title("📊 Dashboard de Análise de Inserções")
st.markdown("Explore os dados de inserções de comerciais. Utilize o filtro à esquerda para selecionar clientes específicos.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

# Calcula as métricas apenas se o dataframe filtrado não estiver vazio
if not df_filtrado.empty:
    media_insercoes = df_filtrado['Inserções'].mean()
    total_insercoes = df_filtrado['Inserções'].sum()
    total_clientes = df_filtrado['Cliente'].nunique()
    # Encontra o cliente com o maior número de inserções
    cliente_mais_frequente = df_filtrado.loc[df_filtrado['Inserções'].idxmax()]['Cliente']
else:
    media_insercoes, total_insercoes, total_clientes, cliente_mais_frequente = 0, 0, 0, "Nenhum"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Média de Inserções", f"{media_insercoes:,.0f}")
col2.metric("Total de Inserções", f"{total_insercoes:,}")
col3.metric("Total de Clientes", f"{total_clientes:,}")
col4.metric("Cliente Destaque", cliente_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        # Pega os 15 clientes com mais inserções para o gráfico
        top_clientes = df_filtrado.groupby('Cliente')['Inserções'].sum().nlargest(15).sort_values(ascending=True).reset_index()
        grafico_clientes = px.bar(
            top_clientes,
            x='Inserções',
            y='Cliente',
            orientation='h',
            title="Top 15 Clientes por Nº de Inserções",
            labels={'Inserções': 'Quantidade de Inserções', 'Cliente': ''},
            text='Inserções' # Adiciona o valor no final da barra
        )
        grafico_clientes.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_clientes, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de clientes.")

with col_graf2:
    if not df_filtrado.empty and df_filtrado['Inserções'].sum() > 0:
        grafico_dist = px.pie(
            df_filtrado,
            names='Cliente',
            values='Inserções',
            title='Proporção de Inserções por Cliente',
            hole=0.4
        )
        grafico_dist.update_traces(textinfo='percent+label', textposition='inside')
        grafico_dist.update_layout(showlegend=False, title_x=0.15)
        st.plotly_chart(grafico_dist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de proporção.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
# Exibe o dataframe filtrado, escondendo a coluna de índice
st.dataframe(df_filtrado.style.format({"Inserções": "{:}"}), hide_index=True)