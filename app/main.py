# app/main.py
# run: streamlit run app/main.py
# app principal: menu lateral com queries pré-definidas e roteamento simples

#import streamlit as st

#st.set_page_config(page_title="fabric dashboards", layout="wide")

#st.markdown("# dashboards fabric — controle interno")
#st.sidebar.title("menu")

import streamlit as st
import pyodbc
import pandas as pd
import platform # Vamos usar isso para checar o sistema

# --- Configurações de Conexão ---
# Pega as credenciais dos Segredos do Streamlit (funciona local e no deploy)
try:
    server = st.secrets["fabric"]["server"]
    database = st.secrets["fabric"]["database"]
    username = st.secrets["fabric"]["username"]
    password = st.secrets["fabric"]["password"]
except KeyError:
    st.error("Credenciais do Fabric não encontradas! Verifique seu arquivo .streamlit/secrets.toml")
    st.stop() # Para a execução se não houver credenciais

# --- DETECÇÃO AUTOMÁTICA DO DRIVER ---
# Determina o driver correto baseado no sistema operacional
# O Streamlit Cloud roda em Linux
if platform.system() == "Linux":
    DRIVER = '{ODBC Driver 17 for SQL Server}'
else:
    # Assumindo Windows para desenvolvimento local
    DRIVER = '{ODBC Driver 18 for SQL Server}' # Verifique se este é o driver que você tem instalado!

st.info(f"Usando Driver: {DRIVER}") # Mostra qual driver está usando


# --- Função para buscar dados (cacheada) ---
@st.cache_data
def get_data_from_fabric(parametro_query):
    
    try:
        conn_string = f'DRIVER={DRIVER};SERVER={server};DATABASE={database};UID={username};PWD={password};Authentication=ActiveDirectoryPassword;TrustServerCertificate=yes'    

        with pyodbc.connect(conn_string, timeout=30) as conn:
            # Query segura com parâmetros
            sql_query = """
                SELECT cta, nomerazao FROM st_bd_resumida
                WHERE cta = ?
            """
                        
            # Passamos o parâmetro de forma segura
            df = pd.read_sql(sql_query, conn, params=[parametro_query])
            return df

    except pyodbc.Error as e:
        # Mostra o erro de forma mais amigável
        st.error(f"Erro de Conexão/Query: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

# --- Interface do App ---
st.title("Consulta ao Microsoft Fabric (Teste Local) 🛢️")

# 1. A caixa de texto para o parâmetro
st.subheader("Digite o número da conta para consulta:")
param_valor = st.text_input("Parâmetro:", 12607854)

# 2. O botão para executar
if st.button("Executar Query"):
    if not param_valor:
        st.warning("Por favor, digite um parâmetro.")
    else:
        with st.spinner("Buscando dados no Fabric..."):
            # 3. Executa a query
            dados = get_data_from_fabric(param_valor)
            
            # 4. Retorna os resultados
            if not dados.empty:
                st.success("Consulta realizada com sucesso!")
                st.dataframe(dados)
            else:
                st.error("Nenhum dado encontrado ou ocorreu um erro na consulta.")