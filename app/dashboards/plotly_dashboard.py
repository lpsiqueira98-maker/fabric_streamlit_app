# app/dashboards/plotly_dashboard.py
# exemplo de gráfico plotly com dados agregados

import streamlit as st
import plotly.express as px
from utils.db import query_to_df
from queries.predefined_queries import SAMPLE_AGG_QUERY

def show():
    st.header("gráfico: carga mensal (plotly)")
    st.write("exemplo de agregação mensal — 6 meses.")

    if st.button("gerar gráfico"):
        with st.spinner("consultando banco..."):
            try:
                df = query_to_df(SAMPLE_AGG_QUERY)
                # espera colunas: data_carga, total
                df['data_carga'] = df['data_carga'].astype('datetime64[ns]')
                fig = px.line(df, x='data_carga', y='total', markers=True,
                              title="cargas por data")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("erro ao gerar gráfico:")
                st.exception(e)
