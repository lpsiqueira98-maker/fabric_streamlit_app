# app/dashboards/table_dashboard.py
# dashboard simples que executa uma query e mostra tabela paginada

import streamlit as st
from utils.db import query_to_df
from queries.predefined_queries import SAMPLE_TABLE_QUERY

def show():
    st.header("tabela: clientes (exemplo)")
    st.write("executando query — resultado limitado a 200 linhas (exemplo).")

    # botão pra rodar a query (evita chamada automática)
    if st.button("carregar tabela"):
        with st.spinner("consultando banco..."):
            try:
                df = query_to_df(SAMPLE_TABLE_QUERY)
                st.success(f"carregadas {len(df)} linhas")
                st.dataframe(df)  # streamlit data table interativa
            except Exception as e:
                st.error("erro ao consultar o banco:")
                st.exception(e)
