# utils/db.py
# conexões com fabric via pyodbc
# usa st.secrets (ou env vars) — seguro pra deploy no streamlit cloud

import os
import pyodbc
import streamlit as st

def _get_secrets():
    """
    retorna um dict com credenciais: tenta st.secrets['database'] primeiro,
    depois variáveis de ambiente.
    """
    if 'database' in st.secrets:
        return st.secrets['database']
    # fallback para env vars (útil em dev)
    return {
        "driver": os.getenv("DB_DRIVER"),
        "server": os.getenv("DB_SERVER"),
        "database": os.getenv("DB_DATABASE"),
        "username": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "connection_string": os.getenv("DB_CONNECTION_STRING")
    }

@st.cache_resource
def get_pyodbc_connection():
    """
    cria e retorna uma conexão pyodbc.
    usa connection_string se presente, senão monta com driver/server/credenciais.
    cache_resource evita reconexões desnecessárias em sessões streamlit.
    """
    s = _get_secrets()
    conn_str = s.get("connection_string")
    if conn_str:
        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn

    driver = s.get("driver") or "{ODBC Driver 18 for SQL Server}"
    server = s.get("server")
    database = s.get("database")
    uid = s.get("username")
    pwd = s.get("password")
    # auth pode ser 'ActiveDirectoryPassword' ou None, dependendo do setup
    auth = s.get("auth")

    # montar connection string segura
    if auth:
        # exemplo: usar auth quando for AAD
        conn_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};DATABASE={database};"
            f"UID={uid};PWD={pwd};Authentication={auth}"
        )
    else:
        conn_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};DATABASE={database};UID={uid};PWD={pwd}"
        )

    conn = pyodbc.connect(conn_string, autocommit=True)
    return conn

def query_to_df(sql: str, params=None):
    """
    executa query e retorna pandas.DataFrame.
    simples, legível, e com tratamento mínimo de erros.
    """
    import pandas as pd
    conn = get_pyodbc_connection()
    try:
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
    finally:
        # não fechamos a conexão cacheada aqui — streamlit reusa
        pass
    return df

