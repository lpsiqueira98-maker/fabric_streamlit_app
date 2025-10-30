import pyodbc
import streamlit as st
import platform
import pandas as pd

# Importa as *funções* que constroem as strings de SQL
from queries.predefined_queries import (
    get_customer_search_query,
    get_sales_by_month_query,
    get_sales_by_dept_query
)

# --- CONFIGURAÇÃO E CONEXÃO ---

@st.cache_resource
def get_db_connection():
    """
    Estabelece uma conexão com o banco de dados e a retorna.
    Usa @st.cache_resource para manter a conexão viva.
    """
    try:
        server = st.secrets["fabric"]["server"]
        database = st.secrets["fabric"]["database"]
        username = st.secrets["fabric"]["username"]
        password = st.secrets["fabric"]["password"]
    except KeyError:
        st.error("Credenciais do Fabric não encontradas! Verifique seus segredos.")
        st.stop()

    # Detecção automática do driver
    if platform.system() == "Linux":
        DRIVER = '{ODBC Driver 17 for SQL Server}'
    else:
        DRIVER = '{ODBC Driver 18 for SQL Server}'

    conn_string = f'DRIVER={DRIVER};SERVER={server};DATABASE={database};UID={username};PWD={password};Authentication=ActiveDirectoryPassword;TrustServerCertificate=yes'
    
    try:
        conn = pyodbc.connect(conn_string, timeout=30)
        return conn
    except pyodbc.Error as e:
        st.error(f"Erro ao conectar no Fabric: {e}")
        st.stop()

def run_query(query, params=None):
    """
    Executa uma query SQL com parâmetros seguros e retorna uma lista de dicionários.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Converte o resultado para lista de dicionários
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
            
    except pyodbc.Error as e:
        st.error(f"Erro inesperado em run_query: {e}")
        return [] # Retorna lista vazia em caso de erro

# --- FUNÇÕES DE BUSCA DE CUSTOMER (Página Menu) ---

def find_customer(nome=None, cpf=None, conta=None):
    """
    Busca clientes no banco de dados usando os critérios fornecidos.
    """
    query, params = get_customer_search_query(nome, cpf, conta)
    
    if query:
        return run_query(query, params)
    return []

# --- FUNÇÕES DE BUSCA DO HISTÓRICO (Página Histórico) ---

@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_sales_by_month(customer_cta):
    """
    Busca o histórico de vendas mensais para um cliente específico (por 'conta').
    Retorna um DataFrame.
    """
    query, params = get_sales_by_month_query(customer_cta)
    
    if query:
        data = run_query(query, params)
        return pd.DataFrame(data)
    return pd.DataFrame()

@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_sales_by_dept(customer_cta):
    """
    Busca o histórico de vendas por departamento para um cliente (por 'conta').
    Retorna um DataFrame.
    """
    query, params = get_sales_by_dept_query(customer_cta)
    
    if query:
        data = run_query(query, params)
        return pd.DataFrame(data)
    return pd.DataFrame()