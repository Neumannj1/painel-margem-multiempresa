"""
Gera a base fictícia de um grupo varejista multiempresa.

Saída (pasta ./dados):
  empresas.csv, lojas.csv, produtos.csv, vendas.csv, itens_venda.csv
  schema_mysql.sql  -> cria as tabelas e carrega os CSVs com LOAD DATA

Todos os nomes, lojas e valores são inventados. Semente fixa para
que a base seja sempre a mesma.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
INICIO, FIM = "2025-10-01", "2026-09-30"
rng = np.random.default_rng(SEED)
OUT = Path(__file__).parent / "dados"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- empresas
empresas = pd.DataFrame([
    # id, nome, segmento, uf, markup alvo
    (1, "Aquaforte Hidráulica",   "Hidráulica",          "PR", 1.62),
    (2, "Voltare Elétrica",       "Elétrica",            "SC", 1.55),
    (3, "Ferrabrás Ferramentas",  "Ferramentas",         "RS", 1.70),
    (4, "Revesta Acabamentos",    "Acabamentos",         "SP", 1.58),
    (5, "Verdejar Jardim e Lazer", "Jardim e Lazer",     "MG", 1.75),
], columns=["empresa_id", "nome", "segmento", "uf", "markup_alvo"])

# ------------------------------------------------------------------- lojas
cidades = {
    1: ["Curitiba Centro", "Curitiba Boqueirão", "Londrina"],
    2: ["Florianópolis", "Joinville", "Blumenau"],
    3: ["Porto Alegre", "Caxias do Sul", "Pelotas"],
    4: ["Campinas", "Sorocaba", "Ribeirão Preto"],
    5: ["Belo Horizonte", "Uberlândia", "Juiz de Fora"],
}
lojas = []
lid = 1
for eid, nomes in cidades.items():
    for i, cidade in enumerate(nomes):
        porte = ["Grande", "Média", "Pequena"][i]
        lojas.append((lid, eid, f"{empresas.loc[eid-1,'nome'].split()[0]} {cidade}",
                      cidade, porte))
        lid += 1
lojas = pd.DataFrame(lojas, columns=["loja_id", "empresa_id", "nome_loja", "cidade", "porte"])
fluxo_porte = {"Grande": 34, "Média": 22, "Pequena": 13}  # notas/dia médias

# ---------------------------------------------------------------- produtos
catalogo = {
    1: {"Tubos e conexões": (8, 60), "Registros e válvulas": (25, 180), "Caixas d'água": (180, 900),
        "Bombas": (250, 1400), "Louças sanitárias": (90, 700)},
    2: {"Fios e cabos": (40, 400), "Disjuntores": (15, 120), "Iluminação": (12, 250),
        "Tomadas e interruptores": (6, 60), "Quadros elétricos": (60, 450)},
    3: {"Ferramentas manuais": (15, 180), "Ferramentas elétricas": (180, 1600), "Fixação": (3, 40),
        "Medição": (25, 350), "EPI": (10, 120)},
    4: {"Tintas": (60, 480), "Pisos e revestimentos": (35, 160), "Argamassas": (18, 70),
        "Acessórios de pintura": (5, 80), "Metais sanitários": (70, 650)},
    5: {"Ferramentas de jardim": (20, 250), "Irrigação": (10, 300), "Piscina": (25, 900),
        "Móveis externos": (180, 1800), "Vasos e decoração": (15, 200)},
}
produtos = []
pid = 1
for eid, cats in catalogo.items():
    for cat, (cmin, cmax) in cats.items():
        for k in range(1, 7):  # 6 SKUs por categoria
            custo = round(float(rng.uniform(cmin, cmax)), 2)
            # markup por produto varia em torno do alvo da empresa
            mk = empresas.loc[eid-1, "markup_alvo"] * rng.uniform(0.9, 1.12)
            produtos.append((pid, f"SKU{pid:04d}", f"{cat} modelo {k}", cat, eid,
                             custo, round(custo * mk, 2), round(float(rng.uniform(0.5, 2.0)), 2)))
            pid += 1
produtos = pd.DataFrame(produtos, columns=["produto_id", "sku", "descricao", "categoria",
                                           "empresa_id", "custo_base", "preco_base", "giro"])

# ----------------------------------------------------------------- vendas
datas = pd.date_range(INICIO, FIM, freq="D")
# sazonalidade mensal (construção: forte no fim do ano, fraco em jan/fev)
saz_mes = {10: 1.00, 11: 1.08, 12: 1.22, 1: 0.82, 2: 0.86, 3: 0.98,
           4: 0.96, 5: 1.00, 6: 0.92, 7: 0.95, 8: 1.02, 9: 1.04}
# jardim e lazer: pico no verão
saz_jardim = {10: 1.05, 11: 1.20, 12: 1.40, 1: 1.25, 2: 1.05, 3: 0.90,
              4: 0.78, 5: 0.70, 6: 0.62, 7: 0.65, 8: 0.80, 9: 0.95}
dia_semana = {0: 1.05, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.08, 5: 0.75, 6: 0.0}  # domingo fechado

prods_por_emp = {e: g.reset_index(drop=True) for e, g in produtos.groupby("empresa_id")}

vendas, itens = [], []
vid = 1
for d in datas:
    mes_idx = (d.year - 2025) * 12 + d.month - 10  # 0..11
    inflacao_custo = 1.004 ** mes_idx               # custo sobe ~0,4% ao mês
    for _, lj in lojas.iterrows():
        eid = lj.empresa_id
        saz = (saz_jardim if eid == 5 else saz_mes)[d.month]
        lam = fluxo_porte[lj.porte] * saz * dia_semana[d.dayofweek]
        if lam == 0:
            continue
        n_notas = rng.poisson(lam)
        cat_prod = prods_por_emp[eid]
        pesos = cat_prod.giro / cat_prod.giro.sum()

        # história do case: a Voltare passa a dar desconto agressivo a partir de mar/26
        desc_base = 0.02
        if eid == 2 and d >= pd.Timestamp("2026-03-01"):
            desc_base = 0.02 + 0.012 * (mes_idx - 5)   # cresce até ~10%
        # a loja pequena da Revesta repassa pouco o aumento de custo
        repasse = 0.35 if lj.loja_id == 12 else 1.0

        for _ in range(n_notas):
            vendas.append((vid, d.date(), lj.loja_id))
            n_itens = 1 + rng.poisson(1.4)
            escolhidos = rng.choice(len(cat_prod), size=n_itens, replace=False, p=pesos)
            for j in escolhidos:
                p = cat_prod.iloc[j]
                custo_u = round(p.custo_base * inflacao_custo, 2)
                preco_u = round(p.preco_base * (1 + (inflacao_custo - 1) * repasse), 2)
                qtd = int(1 + rng.poisson(0.8 if p.custo_base > 150 else 2.5))
                desc = max(0.0, rng.normal(desc_base, 0.015))
                desconto = round(preco_u * qtd * desc, 2)
                itens.append((vid, int(p.produto_id), qtd, preco_u, desconto, custo_u))
            vid += 1

vendas = pd.DataFrame(vendas, columns=["venda_id", "data", "loja_id"])
itens = pd.DataFrame(itens, columns=["venda_id", "produto_id", "quantidade",
                                     "preco_unitario", "desconto", "custo_unitario"])
itens.insert(0, "item_id", range(1, len(itens) + 1))

# ------------------------------------------------------------------ export
empresas.drop(columns="markup_alvo").to_csv(OUT / "empresas.csv", index=False)
lojas.to_csv(OUT / "lojas.csv", index=False)
produtos.drop(columns=["giro", "preco_base", "custo_base"]).to_csv(OUT / "produtos.csv", index=False)
vendas.to_csv(OUT / "vendas.csv", index=False)
itens.to_csv(OUT / "itens_venda.csv", index=False)

(OUT / "schema_mysql.sql").write_text("""-- Base fictícia: grupo varejista multiempresa
CREATE DATABASE IF NOT EXISTS grupo_varejo CHARACTER SET utf8mb4;
USE grupo_varejo;

CREATE TABLE empresas (
  empresa_id INT PRIMARY KEY,
  nome       VARCHAR(80) NOT NULL,
  segmento   VARCHAR(40) NOT NULL,
  uf         CHAR(2)     NOT NULL
);

CREATE TABLE lojas (
  loja_id    INT PRIMARY KEY,
  empresa_id INT NOT NULL,
  nome_loja  VARCHAR(80) NOT NULL,
  cidade     VARCHAR(60) NOT NULL,
  porte      VARCHAR(10) NOT NULL,
  FOREIGN KEY (empresa_id) REFERENCES empresas(empresa_id)
);

CREATE TABLE produtos (
  produto_id INT PRIMARY KEY,
  sku        VARCHAR(10) NOT NULL,
  descricao  VARCHAR(80) NOT NULL,
  categoria  VARCHAR(40) NOT NULL,
  empresa_id INT NOT NULL,
  FOREIGN KEY (empresa_id) REFERENCES empresas(empresa_id)
);

CREATE TABLE vendas (
  venda_id INT PRIMARY KEY,
  data     DATE NOT NULL,
  loja_id  INT  NOT NULL,
  FOREIGN KEY (loja_id) REFERENCES lojas(loja_id),
  INDEX idx_vendas_data (data)
);

CREATE TABLE itens_venda (
  item_id        INT PRIMARY KEY,
  venda_id       INT NOT NULL,
  produto_id     INT NOT NULL,
  quantidade     INT NOT NULL,
  preco_unitario DECIMAL(10,2) NOT NULL,
  desconto       DECIMAL(10,2) NOT NULL,
  custo_unitario DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (venda_id)   REFERENCES vendas(venda_id),
  FOREIGN KEY (produto_id) REFERENCES produtos(produto_id)
);

-- Carga dos CSVs (ajuste o caminho; exige local_infile=1)
LOAD DATA LOCAL INFILE 'empresas.csv'    INTO TABLE empresas    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'lojas.csv'       INTO TABLE lojas       FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'produtos.csv'    INTO TABLE produtos    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'vendas.csv'      INTO TABLE vendas      FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'itens_venda.csv' INTO TABLE itens_venda FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
""", encoding="utf-8")

print(f"empresas {len(empresas)} | lojas {len(lojas)} | produtos {len(produtos)} | "
      f"vendas {len(vendas):,} | itens {len(itens):,}")
