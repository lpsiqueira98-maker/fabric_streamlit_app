# --- Função de Busca de Cliente (Página Menu) ---

def get_customer_search_query(nome=None, cpf=None, conta=None):
    """
    Constrói uma query SQL dinâmica para buscar o customer.
    Retorna a string da query e uma tupla de parâmetros.
    """
    
    base_query = "SELECT nomerazao as nome, cpfcnjp as cpf, cta as conta FROM st_bd_resumida WHERE "
    
    params = []
    conditions = []
    
    if nome:
        # Busca case-insensitive no nome
        conditions.append("UPPER(nomerazao) LIKE UPPER(?)") 
        params.append(f"%{nome}%")
    
    if cpf:
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        # Busca LIKE para tratar zeros à esquerda e formatação
        conditions.append("cpfcnjp LIKE ?") 
        params.append(f"%{cpf_limpo}%")
    
    if conta:
        conditions.append("cta = ?")
        params.append(conta)

    if not conditions:
        return None, None 

    query = base_query + " AND ".join(conditions)
    
    return query, tuple(params)

# --- Funções de Query de Histórico (Página Histórico) ---

def get_sales_by_month_query(customer_cta):
    """
    Constrói a query para buscar Valor, Lucro e Margem por Mês para um cliente.
    """
    
    query = """
        SELECT 
            FORMAT(dt_origem, 'yyyy-MM') AS anomes,
            
            -- CORREÇÃO: Converter (CAST) para FLOAT para evitar erro de serialização do Decimal
            CAST(SUM(valor) AS FLOAT) AS receita,
            CAST(SUM(valor_lb) AS FLOAT) AS lucro_bruto,
            
            -- A divisão de floats também resultará em float
            (CAST(SUM(valor_lb) AS FLOAT) / NULLIF(CAST(SUM(valor) AS FLOAT), 0)) * 100 AS margem_contribuicao
        FROM 
            st_producao_merc prod
        JOIN
            es_map_material mara
            ON prod.id_ipr = mara.material
        WHERE 
            conta = ?
        GROUP BY 
            FORMAT(dt_origem, 'yyyy-MM')
        ORDER BY 
            anomes DESC
    """
    
    params = (customer_cta,)
    
    return query, params

def get_sales_by_dept_query(customer_cta):
    """
    Constrói a query para buscar Valor, Lucro e Margem por Departamento.
    """
   
    query = """
        SELECT 
            departamento,
            
            -- CORREÇÃO: Converter (CAST) para FLOAT para evitar erro de serialização do Decimal
            CAST(SUM(valor) AS FLOAT) AS receita,
            CAST(SUM(valor_lb) AS FLOAT) AS lucro_bruto,

            -- A divisão de floats também resultará em float
            (CAST(SUM(valor_lb) AS FLOAT) / NULLIF(CAST(SUM(valor) AS FLOAT), 0)) * 100 AS margem_contribuicao
        FROM 
            st_producao_merc prod
        JOIN
            es_map_material mara
            ON prod.id_ipr = mara.material
        WHERE 
            conta = ?
        GROUP BY 
            departamento
        ORDER BY 
            departamento DESC
    """
    
    params = (customer_cta,)
    
    return query, params

