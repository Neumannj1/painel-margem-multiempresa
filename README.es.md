# Panel de Margen Multiempresa

[Português](README.md) · **Español**

Caso de análisis de datos de principio a fin: generación de una base ficticia de un grupo minorista con 5 empresas, modelado en MySQL, consulta SQL de margen consolidado, validación cruzada de los resultados y un dashboard HTML interactivo para explorar las cifras.

**Demo:** https://neumannj1.github.io/painel-margem-multiempresa/ (el panel está en portugués)

## Contexto

El caso simula un grupo minorista multiempresa (hidráulica, eléctrica, herramientas, acabados y jardín y ocio), cada una con 3 tiendas en estados distintos, que venden a lo largo de 12 meses. La base es ficticia, pero se construyó con estacionalidad por segmento, variación del coste en el tiempo y dos "casos" escondidos a propósito en los datos:

- una de las empresas (Voltare Elétrica) empieza a dar descuentos crecientes a partir de marzo de 2026, lo que erosiona el margen mes a mes;
- una tienda pequeña de otra empresa traslada poco el aumento de coste al precio de venta, lo que también reduce su margen.

El objetivo del panel es permitir ver esas dos señales filtrando por empresa, tienda, categoría y mes.

## Qué resuelve para un negocio

En un grupo con varias empresas y tiendas, el margen rara vez cae de golpe: se escurre poco a poco y desaparece dentro de la facturación total, que sigue creciendo. El panel responde, sin abrir una hoja de cálculo, a las preguntas que un propietario o gestor se hace de verdad:

- **¿Estamos ganando o perdiendo margen?** El grupo cierra el año con R$ 224,6 M de ingresos netos y un 38,3 % de margen bruto, y el panel muestra la evolución mes a mes por empresa.
- **¿Dónde está el problema?** Las alertas señalan a Voltare Elétrica: el margen pasó del 35,2 % al 31,0 % (−4,2 p. p.) porque los descuentos subieron del 2,0 % al 8,0 % de los ingresos brutos.
- **¿Es descuento o es coste?** El caso de Revesta Ribeirão Preto es distinto: el coste subió y el precio no lo acompañó, con el markup cayendo de 1,59 a 1,55 y el margen del 35,6 % al 34,0 %. Mismo síntoma, causa opuesta, acción distinta.
- **¿Qué tiendas y categorías sostienen el resultado?** El ranking de tiendas y el de categorías muestran quién empuja el margen hacia arriba y quién hacia abajo.

Dos cuidados de método que importan en cualquier proyecto de datos para un cliente:

- **Las cifras se comprueban.** El total de la consulta SQL se valida contra un cálculo independiente en pandas antes de convertirse en gráfico.
- **Las alertas se calculan, no se escriben a mano.** Si cambia la base, cambian también los textos y los estados de las tiendas, sin trabajo manual.

Todos los valores anteriores proceden de la base ficticia; lo que demuestra el proyecto es el método, no un resultado real de mercado.

## Stack

- **Python (pandas, numpy)**: generación de la base sintética y montaje de los datos del dashboard
- **MySQL (SQL puro, CTE)**: consulta de margen consolidado por empresa, tienda, categoría y mes
- **SQLite + pandas**: validación cruzada independiente de la consulta (sin depender de un servidor MySQL en marcha)
- **HTML/CSS/JS vanilla**: dashboard estático, sin framework, con los datos incrustados como JSON

## Estructura

```
gerar_base.py            genera la base ficticia (dados/*.csv + schema_mysql.sql)
dados/
  schema_mysql.sql        DDL de las tablas + LOAD DATA de los CSV
  empresas.csv, lojas.csv, produtos.csv, vendas.csv, itens_venda.csv
margem_consolidada.sql    consulta principal: margen bruto por mes/empresa/tienda/categoría
validar_query.py          ejecuta la consulta en SQLite en memoria y la contrasta con un cálculo directo en pandas
resultado_query.csv       salida de la consulta (entrada del dashboard)
gerar_dashboard.py        une resultado_query.csv + template.html -> painel_margem.html
template.html             diseño y estilo del dashboard (sin datos)
painel_margem.html        dashboard final, archivo único
docs/index.html           copia del dashboard publicada con GitHub Pages
```

## Pipeline

1. `gerar_base.py` crea los datos ficticios y el esquema MySQL.
2. `margem_consolidada.sql` se ejecuta contra la base (o, en local, `validar_query.py` lo traduce a SQLite) y calcula ingresos netos, CMV (coste de la mercancía vendida), margen bruto y margen % agrupados por mes/empresa/tienda/categoría.
3. `validar_query.py` contrasta el total de la consulta con un cálculo directo en pandas, como comprobación de cordura antes de fiarse de la cifra.
4. `gerar_dashboard.py` agrega el resultado validado y genera el HTML final, sin dependencias externas salvo la fuente tipográfica.

## Ejecución en local

```bash
pip install pandas numpy
python gerar_base.py
python validar_query.py
python gerar_dashboard.py
```

Esto recrea `dados/`, `resultado_query.csv` y `painel_margem.html` desde cero.

## Autor

Jean Neumann: análisis de datos / BI.

LinkedIn: https://www.linkedin.com/in/jean-neumann/
