# queries/predefined_queries.py
# centraliza queries SQL pré-definidas usadas pela UI.
# manter simples e testável.

SAMPLE_TABLE_QUERY = """
SELECT TOP 200
    id_conta,
    nome,
    email,
    data_carga
FROM dbo.clientes
ORDER BY data_carga DESC
"""

SAMPLE_AGG_QUERY = """
SELECT data_carga, COUNT(*) as total
FROM dbo.clientes
WHERE data_carga >= DATEADD(month, -6, GETDATE())
GROUP BY data_carga
ORDER BY data_carga
"""
