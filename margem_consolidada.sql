-- Margem bruta consolidada por empresa, loja e mês (MySQL 8+)
-- Receita líquida = preço x quantidade - desconto
-- CMV             = custo unitário x quantidade
-- Margem bruta    = receita líquida - CMV

WITH itens AS (
    SELECT
        DATE_FORMAT(v.data, '%Y-%m')                    AS mes,
        e.empresa_id,
        e.nome                                          AS empresa,
        l.loja_id,
        l.nome_loja,
        p.categoria,
        v.venda_id,
        iv.quantidade,
        iv.preco_unitario * iv.quantidade               AS receita_bruta,
        iv.desconto,
        iv.custo_unitario * iv.quantidade               AS cmv
    FROM itens_venda iv
    JOIN vendas   v ON v.venda_id   = iv.venda_id
    JOIN lojas    l ON l.loja_id    = v.loja_id
    JOIN empresas e ON e.empresa_id = l.empresa_id
    JOIN produtos p ON p.produto_id = iv.produto_id
    WHERE v.data BETWEEN '2025-10-01' AND '2026-09-30'
)
SELECT
    mes,
    empresa_id,
    empresa,
    loja_id,
    nome_loja,
    categoria,
    COUNT(DISTINCT venda_id)                            AS notas,
    SUM(quantidade)                                     AS itens,
    ROUND(SUM(receita_bruta), 2)                        AS receita_bruta,
    ROUND(SUM(desconto), 2)                             AS descontos,
    ROUND(SUM(receita_bruta - desconto), 2)             AS receita_liquida,
    ROUND(SUM(cmv), 2)                                  AS cmv,
    ROUND(SUM(receita_bruta - desconto - cmv), 2)       AS margem_bruta,
    ROUND(100 * SUM(receita_bruta - desconto - cmv)
              / NULLIF(SUM(receita_bruta - desconto), 0), 2) AS margem_pct
FROM itens
GROUP BY mes, empresa_id, empresa, loja_id, nome_loja, categoria
ORDER BY mes, empresa_id, loja_id, categoria;
