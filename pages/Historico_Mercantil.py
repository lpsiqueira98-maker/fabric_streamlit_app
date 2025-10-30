import streamlit as st
import pandas as pd
from utils.db import fetch_sales_by_month, fetch_sales_by_dept

# Função helper para converter DataFrame para CSV em memória
@st.cache_data
def convert_df_to_csv(df):
    """Converte um DataFrame para CSV (UTF-8) em memória para download."""
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

# --- Configuração da Página ---
st.set_page_config(
    page_title="Histórico Mercantil",
    page_icon="📊",
    layout="wide"
)

# CSS para diminuir a fonte dos st.metric
st.markdown("""
<style>
/* Diminui a fonte do Título (ex: "Receita Total") */
[data-testid="stMetricLabel"] {
    font-size: 1.1rem;
}
/* Diminui a fonte do Valor (ex: "R$ 100,00") */
[data-testid="stMetricValue"] {
    font-size: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- Verificação de Segurança ---
# Verifica se um cliente foi selecionado na página Menu
if 'selected_customer' not in st.session_state or st.session_state['selected_customer'] is None:
    st.warning("⬅️ Por favor, selecione um cliente na página 'Menu' primeiro.")
    st.stop() # Para a execução da página

# --- Carregamento de Dados ---
customer = st.session_state['selected_customer']
customer_name = customer.get('nome', 'N/A')
customer_cta = customer.get('conta', None) # Pega a 'conta' (ID) do cliente

st.title(f"Histórico Mercantil: {customer_name}")

if not customer_cta:
    st.error("Erro: Cliente selecionado não possui uma 'conta' (ID) válida.")
    st.stop()

# Busca os dados do banco
try:
    with st.spinner(f"Buscando histórico de {customer_name}..."):
        df_month = fetch_sales_by_month(customer_cta)
        df_dept = fetch_sales_by_dept(customer_cta)

    # --- NOVO: Seção de Total ---
    st.subheader("Resumo Total do Cliente")
    if not df_dept.empty:
        total_receita_dept = df_dept['receita'].sum()
        total_lucro_dept = df_dept['lucro_bruto'].sum()
        if total_receita_dept != 0:
            total_margem_dept = (total_lucro_dept / total_receita_dept) * 100
        else:
            total_margem_dept = 0

        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.metric("Receita Total", f"R$ {total_receita_dept:,.2f}")
        col_d2.metric("Lucro Total", f"R$ {total_lucro_dept:,.2f}")
        col_d3.metric("Margem Média", f"{total_margem_dept:.2f}%")
    else:
        st.info("Nenhum dado agregado encontrado para este cliente.")
    
    st.divider()

    # --- Seção: Análise Mensal ---
    st.subheader("Análise Mensal")
    if not df_month.empty:
        
        # Preenche valores NaN (nulos) com 0 para evitar erros
        df_month = df_month.fillna(0)
        
        st.dataframe(
            df_month,
            use_container_width=True,
            column_config={
                "anomes": "Período",
                "receita": st.column_config.NumberColumn(
                    "Valor (R$)",
                    format="R$ %.2f"
                ),
                "lucro_bruto": st.column_config.NumberColumn(
                    "Lucro (R$)",
                    format="R$ %.2f"
                ),
                "margem_contribuicao": st.column_config.NumberColumn(
                    "Margem (%)",
                    format="%.2f%%"
                )
            }
        )
        
        # Botão de Download
        csv_month = convert_df_to_csv(df_month)
        st.download_button(
            label="Exportar CSV Mensal",
            data=csv_month,
            file_name=f"historico_mensal_{customer_cta}.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum dado mensal encontrado para este cliente.")

    st.divider()

    # --- Seção: Análise por Departamento ---
    st.subheader("Análise por Departamento")
    if not df_dept.empty:
        
        # Preenche valores NaN (nulos) com 0 para evitar erros
        df_dept = df_dept.fillna(0)
        
        st.dataframe(
            df_dept,
            use_container_width=True,
            column_config={
                "departamento": "Departamento",
                "receita": st.column_config.NumberColumn(
                    "Valor (R$)",
                    format="R$ %.2f"
                ),
                "lucro_bruto": st.column_config.NumberColumn(
                    "Lucro (R$)",
                    format="R$ %.2f"
                ),
                "margem_contribuicao": st.column_config.NumberColumn(
                    "Margem (%)",
                    format="%.2f%%"
                )
            }
        )
        
        # Botão de Download
        csv_dept = convert_df_to_csv(df_dept)
        st.download_button(
            label="Exportar CSV por Departamento",
            data=csv_dept,
            file_name=f"historico_depto_{customer_cta}.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum dado por departamento encontrado para este cliente.")

except Exception as e:
    st.error(f"Erro ao buscar dados do histórico: {e}")