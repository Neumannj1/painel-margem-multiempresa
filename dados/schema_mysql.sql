-- Base fictícia: grupo varejista multiempresa
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
