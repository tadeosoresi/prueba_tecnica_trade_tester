# Prueba_tecnica_trade_tester
Prueba técnica: Script que testee 3 estrategias de trading sobre datos via API/CSV/excel

GUIDE:
Para ejecutar programa: python main.py --funds --tickers --start --end --csv --xlsx
- --funds: OBLIGATORIO, fondos totales que se dispone.
- --tickers: OBLIGATORIO, tickers de las acciones a operar, ingresar de forma accion1 accion2 accionN
- --start: NO OBLIGATORIO, toma fecha default (date start), si ingresamos archivo con cotizaciones toma la primera fecha en el indice.
- --end: NO OBLIGATORIO, toma fecha default (date end), si ingresamos archivo con cotizaciones toma la ultima fecha en el indice.
- --csv: NO OBLIGATORIO SALVO QUE SE DESEE INGRESAR COTIZACIONES DESDE CSV, por defecto FALSE.
- --xlsx: NO OBLIGATORIO SALVO QUE SE DESEE INGRESAR COTIZACIONES DESDE XLSX, por defecto FALSE.
- SI INGRESAMOS COTIZACIONES DESDE ARCHIVO, LA COLUMNA DATE DEBE SER LA PRIMERA Y LOS TICKERS CONTENIDOS EN EL ARCHIVO DEBEN SER LOS MISMOS QUE ESPECIFICAMOS VIA CONSOLA (HACE UN MATCH)

LIMITACIONES:
Por temas de API, solamente maximo de 5 tickers (por los calls en el paquete basico), por eso mismo en los resultados totales se redujeron a top 3 (Acciones con más ganancia/menor perdida, top compradas)
Trae unicamente data de los ultimos 3 meses, si no podemos traer historicos de hace 20 años pero es muchisima data por request y agota los calls.

## 🚀 Lista de mejoras
Algunas features que se podrían agregar:

HECHAS:
- [ ] Validador de tickers de acciones que especificamos via consola (si la data se desea descargar desde API). Se hizo esto con la api de AlphaVantage.
- [ ] Guardar todos los movimentos de las tres estrategias en un xlsx.
- [ ] Recibir datos via API/CSV/XLSX.
PENDIENTES:
- [ ] Montos de inversión variables, analisis en base al volumen, verificar si las cotizaciones estan ajustadas por splits/dividendos.
- [ ] Indicadores tecnicos para solventar decisión de compra/venta.
- [ ] Interfaz grafica con TKINTER (por cuestiones de conocimientos y tiempo no se hizo)
- [ ] Sentimental analysis via tweets de twitter en base a periodo de tiempo (para reconocer contexto actual de la empresa)
- [ ] Deployment API con una interfaz via bootstrap en el cual el usuario ingrese tickers y setee unicamente los parametros y la API devuelva resultados

## 😪 Cuestiones que no se pudieron hacer
- [ ] Optimizar codigo de las tres estrategias, mucha repetición/variables repetidas.
- [ ] Unit tests, por cuestiones de tiempo no se llevaron a cabo aunque el codigo tiene gran cantidad de tests internos.

Thanks!


