"""
Agrega o resultado da query de margem e gera o dashboard HTML
(um arquivo único, sem dependências externas além da fonte).

Entrada: resultado_query.csv (saída de validar_query.py) e dados/*.csv
Saída:   painel_margem.html
"""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).parent
D = BASE / "dados"

res = pd.read_csv(BASE / "resultado_query.csv")
empresas = pd.read_csv(D / "empresas.csv")
lojas = pd.read_csv(D / "lojas.csv")
vendas = pd.read_csv(D / "vendas.csv", parse_dates=["data"])

meses = sorted(res.mes.unique())
cats = sorted(res.categoria.unique())
mi = {m: i for i, m in enumerate(meses)}
ci = {c: i for i, c in enumerate(cats)}

fatos = [[mi[r.mes], int(r.loja_id), ci[r.categoria],
          round(r.receita_bruta, 2), round(r.descontos, 2), round(r.cmv, 2)]
         for r in res.itertuples()]

vendas["mes"] = vendas.data.dt.strftime("%Y-%m")
notas = vendas.groupby(["mes", "loja_id"]).size().reset_index(name="n")
notas = [[mi[r.mes], int(r.loja_id), int(r.n)] for r in notas.itertuples()]

data = {
    "meses": meses,
    "categorias": cats,
    "empresas": empresas.to_dict(orient="records"),
    "lojas": lojas.to_dict(orient="records"),
    "fatos": fatos,
    "notas": notas,
}
tpl = (BASE / "template.html").read_text(encoding="utf-8")
html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
(BASE / "painel_margem.html").write_text(html, encoding="utf-8")
print(f"painel_margem.html gerado: {len(html)/1024:.0f} KB, {len(fatos)} fatos")
