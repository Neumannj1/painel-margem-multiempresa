# Painel de Margem Multiempresa

Case de análise de dados ponta a ponta: geração de uma base fictícia de um grupo varejista com 5 empresas, modelagem em MySQL, consulta SQL de margem consolidada, validação cruzada dos resultados e um dashboard HTML interativo para explorar os números.

**Demo:** https://neumannj1.github.io/painel-margem-multiempresa/

## Contexto

O case simula um grupo varejista multiempresa (hidráulica, elétrica, ferramentas, acabamentos, jardim e lazer), cada uma com 3 lojas em estados diferentes, vendendo ao longo de 12 meses. A base é fictícia, mas foi construída com sazonalidade por segmento, variação de custo ao longo do tempo e dois "casos" propositais escondidos nos dados:

- uma das empresas (Voltare Elétrica) passa a dar desconto crescente a partir de março/2026, corroendo a margem mês a mês;
- uma loja pequena de outra empresa repassa pouco o aumento de custo ao preço de venda, também reduzindo a margem.

O objetivo do painel é permitir enxergar esses dois sinais filtrando por empresa, loja, categoria e mês.

## O que isso resolve para um negócio

Em um grupo com várias empresas e lojas, a margem raramente cai de uma vez: ela escorre aos poucos e some dentro do faturamento total, que continua crescendo. O painel responde, sem abrir planilha, às perguntas que um dono ou gestor realmente faz:

- **Estamos ganhando ou perdendo margem?** O grupo fecha o ano com R$ 224,6 mi de receita líquida e 38,3% de margem bruta, e o painel mostra a evolução mês a mês por empresa.
- **Onde está o problema?** Os alertas apontam a Voltare Elétrica: a margem foi de 35,2% para 31,0% (−4,2 p.p.) porque os descontos subiram de 2,0% para 8,0% da receita bruta.
- **É desconto ou é custo?** O caso da Revesta Ribeirão Preto é diferente: o custo subiu e o preço não acompanhou, com o markup caindo de 1,59 para 1,55 e a margem de 35,6% para 34,0%. Mesmo sintoma, causa oposta, ação diferente.
- **Quais lojas e categorias sustentam o resultado?** O ranking de lojas e o ranking de categorias mostram quem puxa a margem para cima e quem puxa para baixo.

Dois cuidados de método que importam em qualquer projeto de dados para cliente:

- **Os números são conferidos.** O total da query SQL é validado contra um cálculo independente em pandas antes de virar gráfico.
- **Os alertas são calculados, não escritos à mão.** Se a base mudar, os textos e os status das lojas mudam junto, sem retrabalho manual.

Todos os valores acima vêm da base fictícia; o que o projeto demonstra é o método, não um resultado real de mercado.

## Stack

- **Python (pandas, numpy)** — geração da base sintética e montagem dos dados do dashboard
- **MySQL (SQL puro, CTE)** — query de margem consolidada por empresa, loja, categoria e mês
- **SQLite + pandas** — validação cruzada independente da query (sem depender de um servidor MySQL rodando)
- **HTML/CSS/JS vanilla** — dashboard estático, sem framework, dados embutidos como JSON

## Estrutura

```
gerar_base.py            gera a base fictícia (dados/*.csv + schema_mysql.sql)
dados/
  schema_mysql.sql        DDL das tabelas + LOAD DATA dos CSVs
  empresas.csv, lojas.csv, produtos.csv, vendas.csv, itens_venda.csv
margem_consolidada.sql    query principal: margem bruta por mês/empresa/loja/categoria
validar_query.py          roda a query num SQLite em memória e confere contra cálculo direto em pandas
resultado_query.csv       saída da query (entrada do dashboard)
gerar_dashboard.py        junta resultado_query.csv + template.html -> painel_margem.html
template.html             layout/estilo do dashboard (sem dados)
painel_margem.html        dashboard final, arquivo único
docs/index.html           cópia do dashboard publicada via GitHub Pages
```

## Pipeline

1. `gerar_base.py` cria os dados fictícios e o schema MySQL.
2. `margem_consolidada.sql` roda contra o banco (ou, localmente, é traduzido para SQLite por `validar_query.py`) e calcula receita líquida, CMV, margem bruta e margem % agrupados por mês/empresa/loja/categoria.
3. `validar_query.py` confere o total da query contra um cálculo direto em pandas, como checagem de sanidade antes de confiar no número.
4. `gerar_dashboard.py` agrega o resultado validado e gera o HTML final, sem dependências externas além da fonte.

## Rodando localmente

```bash
pip install pandas numpy
python gerar_base.py
python validar_query.py
python gerar_dashboard.py
```

Isso recria `dados/`, `resultado_query.csv` e `painel_margem.html` do zero.

## Autor

Jean Neumann — análise de dados / BI.
