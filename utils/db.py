import streamlit as st
import pyodbc
import pandas as pd
import platform
from queries.predefined_queries import (
    get_customer_search_query,
    get_sales_by_month_query,
    get_sales_by_dept_query
)

# --- Configurações de Conexão ---
# Pega as credenciais dos Segredos do Streamlit (funciona local e no deploy)
try:
    server = st.secrets["fabric"]["server"]
    database = st.secrets["fabric"]["database"]
    username = st.secrets["fabric"]["username"]
    password = st.secrets["fabric"]["password"]
except KeyError:
    st.error("Credenciais do Fabric não encontradas! Verifique seu .streamlit/secrets.toml")
    st.stop()

# --- DETECÇÃO AUTOMÁTICA DO DRIVER ---
if platform.system() == "Linux":
    DRIVER = '{ODBC Driver 17 for SQL Server}'
else:
    DRIVER = '{ODBC Driver 18 for SQL Server}'

def get_db_connection_string():
    """Retorna a string de conexão completa, agora com Pooling=false."""
    
    conn_string = (
        f'DRIVER={DRIVER};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'Authentication=ActiveDirectoryPassword;'
        f'TrustServerCertificate=yes;'
        f'Pooling=false' # Evita erros de "link quebrado"
    )
    return conn_string

# --- NOVA FUNÇÃO DE EXECUÇÃO (INTERNA E CACHEADA) ---
@st.cache_data(ttl=600) # Cache de 10 minutos
def _run_query_cached(query, params=None):
    """
    Função "burra" que APENAS executa a query e retorna o DF.
    Se falhar, ela levanta a exceção (que não será cacheada).'
    Soluciona o problema de conexões quebradas no cache.
    """
    conn_string = get_db_connection_string()
    
    with pyodbc.connect(conn_string, timeout=30) as conn:
        df = pd.read_sql(query, conn, params=params)

    # Converte para tipos nativos para evitar erro de serialização do Decimal
    return df.astype(object)

# --- FUNÇÃO PÚBLICA (NÃO CACHEADA) COM TRATAMENTO DE ERRO ---
def run_query(query, params=None):
    """
    Função "inteligente" que chama a versão cacheada
    e trata os erros de conexão.
    """
    try:
        # Tenta executar a função cacheada
        return _run_query_cached(query, params)

    except pyodbc.Error as e:
        # Se a query falhar (ex: "Communication link failure"),
        # o st.cache_data *não* salvará o erro.
        # Nós pegamos o erro aqui e mostramos na tela.
        st.error(f"Erro de Conexão/Query (run_query): {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio
    except Exception as e:
        # Pega outros erros inesperados (ex: UnboundLocalError)
        st.error(f"Erro inesperado em run_query: {e}")
        return pd.DataFrame()

# --- Funções de Busca Específicas (sem alteração) ---

def find_customer(nome=None, cpf=None, conta=None):
    """
    Busca clientes no banco de dados com base nos filtros.
    Retorna uma lista de dicionários (clientes).
    """
    query, params = get_customer_search_query(nome, cpf, conta)
    
    if query is None:
        return []
        
    df = run_query(query, params)
    
    if df.empty:
        return []
        
    # Converte o DataFrame em uma lista de dicionários
    return df.to_dict('records')

def fetch_sales_by_month(customer_cta):
    """
    Busca o histórico de vendas mensais para um cliente.
    """
    query, params = get_sales_by_month_query(customer_cta)
    df = run_query(query, params)
    return df

def fetch_sales_by_dept(customer_cta):
    """
    Busca o histórico de vendas por departamento para um cliente.
    """
    query, params = get_sales_by_dept_query(customer_cta)
    df = run_query(query, params)
    return df
