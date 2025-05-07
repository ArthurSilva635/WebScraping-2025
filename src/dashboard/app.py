import os
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.normpath(os.path.join(BASE_DIR, '../../data/mercadolivre.db'))

# Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data(path):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query("SELECT * FROM notebook", conn)
    conn.close()
    return df

# Carregar dados
df = load_data(db_path)

# Filtros interativos na sidebar
st.sidebar.header("🎛️ Filtros")
marcas = st.sidebar.multiselect("Filtrar por marca:", df['brand'].unique())
if marcas:
    df = df[df['brand'].isin(marcas)]

# Título principal
st.title('📊 Pesquisa de Mercado - Notebooks no Mercado Livre')
st.caption(f"Dados coletados em: `{df['_datetime'].max()}`")

# KPIs principais
with st.container():
    st.subheader('💡 KPIs principais')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🖥️ Total de Notebooks", df.shape[0])
    col2.metric("🏷️ Marcas Únicas", df['brand'].nunique())
    col3.metric("💰 Preço Médio (R$)", f"{df['new_money'].mean():.2f}")
    col4.metric("📦 Produto mais barato (R$)", f"{df['new_money'].min():.2f}")

# Marcas mais frequentes
with st.container():
    st.subheader('🏆 Marcas mais encontradas até a 10ª página')
    top_brands = df['brand'].value_counts().reset_index()
    top_brands.columns = ['brand', 'count']
    chart1 = alt.Chart(top_brands).mark_bar().encode(
        x=alt.X('brand', sort='-y'),
        y='count',
        tooltip=['brand', 'count']
    ).properties(height=300)
    st.altair_chart(chart1, use_container_width=True)

# Preço médio por marca
with st.container():
    st.subheader('💵 Preço médio por marca')
    df_price = df[df['new_money'] > 0]
    avg_price = df_price.groupby('brand')['new_money'].mean().reset_index()
    avg_price = avg_price.sort_values(by='new_money', ascending=False)
    chart2 = alt.Chart(avg_price).mark_bar().encode(
        x=alt.X('brand', sort='-y'),
        y=alt.Y('new_money'),
        tooltip=['brand', 'new_money']
    ).properties(height=300)
    st.altair_chart(chart2, use_container_width=True)

# Satisfação média por marca
with st.container():
    st.subheader('⭐ Satisfação média por marca')
    df_rating = df[df['reviews_rating_number'] > 0]
    satisfaction = df_rating.groupby('brand')['reviews_rating_number'].mean().reset_index()
    satisfaction = satisfaction.sort_values(by='reviews_rating_number', ascending=False)
    chart3 = alt.Chart(satisfaction).mark_bar().encode(
        x=alt.X('brand', sort='-y'),
        y=alt.Y('reviews_rating_number'),
        tooltip=['brand', 'reviews_rating_number']
    ).properties(height=300)
    st.altair_chart(chart3, use_container_width=True)

    # Botão para exportar CSV
st.download_button(
    label="📥 Baixar dados filtrados (CSV)",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='notebooks_filtrados.csv',
    mime='text/csv'
)

# Paginação da tabela
st.subheader("🔍 Resultados da pesquisa")
items_per_page = st.selectbox("Itens por página:", [10, 20, 50], index=1)
page_number = st.number_input("Página:", min_value=1, value=1)

start_idx = (page_number - 1) * items_per_page
end_idx = start_idx + items_per_page
st.dataframe(df.iloc[start_idx:end_idx])

# Faixa de preço
min_price, max_price = int(df['new_money'].min()), int(df['new_money'].max())
price_range = st.sidebar.slider("Faixa de preço (R$):", min_price, max_price, (min_price, max_price))
df = df[(df['new_money'] >= price_range[0]) & (df['new_money'] <= price_range[1])]

# Avaliação mínima
min_rating = st.sidebar.slider("Avaliação mínima:", 0.0, 5.0, 0.0, 0.5)
df = df[df['reviews_rating_number'] >= min_rating]

