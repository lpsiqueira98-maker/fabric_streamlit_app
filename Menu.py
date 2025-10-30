import streamlit as st
from utils.db import find_customer 

st.set_page_config(
    page_title="Consulta Mercantil", # Este é o título da ABA do navegador
    page_icon="🔍",
    layout="centered"
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'selected_customer' not in st.session_state:
    st.session_state['selected_customer'] = None
if 'customer_list' not in st.session_state:
    st.session_state['customer_list'] = None

# --- TÍTULO ---
st.title("Consulta Mercantil do Cliente")
st.markdown("Insira um dos campos abaixo para buscar o cliente.")

# --- FORMULÁRIO DE BUSCA ---
with st.form(key="customer_search_form"):
    nome = st.text_input("Nome do Cliente")
    cpf = st.text_input("CPF (parcial ou completo)")
    conta = st.text_input("Conta")

    submit_button = st.form_submit_button(label="Buscar Cliente")

# --- LÓGICA DE BUSCA (BOTÃO 1) ---
if submit_button:
    # Limpa estados anteriores
    st.session_state['selected_customer'] = None
    st.session_state['customer_list'] = None
    
    if not nome and not cpf and not conta:
        st.error("Por favor, preencha pelo menos um campo de busca.")
    else:
        with st.spinner("Buscando cliente no Fabric..."):
            customer_results = find_customer(nome=nome, cpf=cpf, conta=conta)
            
            if customer_results:
                
                # CASO 1: Exatamente 1 cliente encontrado
                if len(customer_results) == 1:
                    st.session_state['selected_customer'] = customer_results[0]
                    st.rerun() 
                
                # CASO 2: Múltiplos clientes encontrados
                else:
                    st.session_state['customer_list'] = customer_results
                    st.warning("Múltiplos clientes encontrados. Por favor, selecione o cliente correto abaixo.")
            
            # CASO 3: Nenhum cliente encontrado
            else:
                st.error("Nenhum cliente encontrado com os critérios fornecidos.")

# --- FORMULÁRIO DE SELEÇÃO (APARECE SE HOUVER MÚLTIPLOS CLIENTES) ---
if st.session_state['customer_list']:
    
    try:
        options = [
            f"Nome: {c.get('nome', 'N/A')} | CPF: {c.get('cpf', 'N/A')} | Conta: {c.get('conta', 'N/A')}" 
            for c in st.session_state['customer_list']
        ]
        
        with st.form(key="customer_select_form"):
            st.write("Selecione o cliente desejado:")
            
            with st.container(height=300):
                selected_option = st.radio(
                    label="Clientes encontrados:", 
                    options=options,
                    label_visibility="collapsed" # Esconde o label acima
                )
            
            select_button = st.form_submit_button("Confirmar Seleção")

            # --- LÓGICA DE SELEÇÃO (BOTÃO 2) ---
            if select_button:
                selected_index = options.index(selected_option)
                selected_data = st.session_state['customer_list'][selected_index]
                
                st.session_state['selected_customer'] = selected_data
                st.session_state['customer_list'] = None
                
                # O st.rerun() força o script a recarregar.
                # O bloco abaixo (elif) será executado.
                st.rerun() 
                
    except Exception as e:
        st.error(f"Erro ao formatar lista de clientes. Verifique nomes das colunas. Erro: {e}")
        st.session_state['customer_list'] = None 

# --- BLOCO FINAL DE EXIBIÇÃO ---
# Este bloco é executado após o 'rerun',
# tanto da busca direta (CASO 1) quanto da seleção (CASO 2).
elif st.session_state['selected_customer'] and not submit_button:
    customer = st.session_state['selected_customer']
    customer_name = customer.get('nome', 'N/A')
    
    st.success(f"Cliente **{customer_name}** selecionado!")
    st.info("Navegue pelas páginas no menu ao lado para ver os detalhes.")
    st.json(customer)

