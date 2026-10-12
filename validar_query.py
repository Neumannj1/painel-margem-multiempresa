"""
Roda a query de margem num SQLite em memória (tradução mínima do
DATE_FORMAT do MySQL) e confere os totais contra um cálculo direto em pandas.
"""
from pathlib import Path
import sqlite3
import pandas as pd

BASE = Path(__file__).parent
D = BASE / "dados"
con = sqlite3.connect(":memory:")
for t in ["empresas", "lojas", "produtos", "vendas", "itens_venda"]:
    pd.read_csv(D / f"{t}.csv").to_sql(t, con, index=False)

sql = (BASE / "margem_consolidada.sql").read_text(encoding="utf-8")
sql = sql.replace("DATE_FORMAT(v.data, '%Y-%m')", "strftime('%Y-%m', v.data)")
res = pd.read_sql(sql, con)
res.to_csv(BASE / "resultado_query.csv", index=False)

# conferência independente
iv = pd.read_csv(D / "itens_venda.csv")
receita = (iv.preco_unitario * iv.quantidade - iv.desconto).sum()
cmv = (iv.custo_unitario * iv.quantidade).sum()

print(f"linhas da query: {len(res):,}")
print(f"receita líquida  query {res.receita_liquida.sum():>16,.2f} | pandas {receita:>16,.2f}")
print(f"CMV              query {res.cmv.sum():>16,.2f} | pandas {cmv:>16,.2f}")
print(f"margem %         query {100*res.margem_bruta.sum()/res.receita_liquida.sum():.2f} | "
      f"pandas {100*(receita-cmv)/receita:.2f}")
print()
emp = res.groupby("empresa")[["receita_liquida", "margem_bruta"]].sum()
emp["margem_pct"] = 100 * emp.margem_bruta / emp.receita_liquida
print(emp.round(1))
print()
mes = res[res.empresa_id == 2].groupby("mes")[["receita_liquida", "margem_bruta"]].sum()
print("Voltare margem % por mês:", (100 * mes.margem_bruta / mes.receita_liquida).round(1).to_dict())
lj = res[res.loja_id.isin([10, 11, 12])].groupby(["nome_loja", "mes"])[["receita_liquida", "margem_bruta"]].sum()
lj["pct"] = 100 * lj.margem_bruta / lj.receita_liquida
print(lj.pct.unstack().round(1).iloc[:, [0, 5, 11]])
