# Cambios · V4.2.1

Correcciones encontradas corriendo el flujo de punta a punta sobre un juego de
estados financieros peruano completo (dos ejercicios, cuatro hojas). Ninguna
cambia el contrato del skill: mismos comandos, mismos JSON, mismas salidas.

---

## `scripts/extract_data.py`

**Descubrimiento de hojas por contenido.** `discover_sheets()` clasificaba sólo
por el NOMBRE de la pestaña contra una lista corta de palabras clave. `BG` y
`ERF` —las dos abreviaturas más usadas en Perú— no estaban, así que un libro
normal no encontraba nada. Ahora se lee el título que la hoja lleva adentro
("ESTADO DE SITUACIÓN FINANCIERA") y el nombre queda como respaldo.

**Multiperiodo.** `periods = 1` estaba fijo, con un comentario que anunciaba un
chequeo que nunca se escribió, y sólo se guardaba UNA hoja por tipo de estado:
un libro con una hoja por año perdía todos los ejercicios menos el último. Ahora
las hojas se agrupan por ejercicio y `periods_found` refleja lo que hay.

**Un solo `data.json` para las dos etapas.** `calculate_ratios.py` lee
`{periodos, balance, estado_resultados}` y `scan_router.py` con
`generate_minuta.js` leen `{esf, egp}`. El archivo ahora sale con las dos
vistas, así que ninguna etapa tiene que adivinar.

**Balance a dos columnas.** El activo va a la izquierda y el pasivo con el
patrimonio a la derecha, avanzando en paralelo sobre las mismas filas. Leyendo
fila por fila la secuencia queda intercalada y el seguimiento de sección —que
se apoya en las filas de total— archivaba el pasivo dentro del activo. Ahora se
lee cada bloque de columnas por separado, en orden de documento.

**Encabezados de sección.** La comparación era exacta contra una lista, y
"PASIVO Y PATRIMONIO" contiene las dos palabras: no activaba ninguna rama y el
puntero se quedaba en el activo.

**Estado de resultados de dos columnas.** `parse_egp()` asumía una planilla de
gestión: etiqueta fija en la columna B, una columna por mes y una columna
"TOTAL <año>". Un estado de cierre no tiene nada de eso y devolvía cero líneas.
Se agregó un modo simple: primera celda de texto como etiqueta, primera
numérica que la siga como valor.

**Plan de cuentas.** Faltaban términos estándar del PCGE: `existencias`
(inventarios), impuesto a la renta, utilidad antes de impuestos, "cuentas por
cobrar AL personal", "gastos CONTRATADOS por anticipado", "otros activos",
"gastos de venta" en singular. El matching además pliega acentos.

**Subtotal contado dos veces.** "OTROS INGRESOS Y GASTOS" es el encabezado que
carga la suma del bloque —diferencia de cambio más otros ingresos— y contiene la
cadena "otros ingresos", así que se lo llevaba `otros_ingresos` y la partida
quedaba contada dos veces. Tiene clave propia.

## `scripts/scan_router.py`

**El clasificador de severidad era código muerto.** `classify_severity()` leía
claves planas (`ratios.get("margen_operativo")`) contra el `ratios.json`
ANIDADO, así que sus seis umbrales devolvían siempre el default: cualquier
empresa con patrimonio holgado salía "sano", aunque el resultado operativo se
hubiera desplomado. Se agregaron lectores (`rat`, `var_pct`, `var_monto`) y dos
umbrales de deterioro entre periodos: caída del operativo y cobertura de
intereses.

**Regla nueva: `puente_no_operativo`, severidad crítica.** El caso que ninguna
regla de una sola foto puede ver: el resultado neto MEJORA mientras el operativo
CAE, y lo que cierra la brecha es una partida ajena al negocio. La regla
`no_recurrente_material` que ya existía mide el PESO de lo no recurrente en un
año suelto —dispararía igual en un año donde ambos suben— y lo archivaba como
comentario al pie. La nueva mide la DIRECCIÓN de los dos resultados y el tamaño
del puente. Una distorsión crítica además levanta la severidad general.

## `scripts/generate_minuta.js`

**Falsos positivos por nombres de cuenta.** Se leía un solo nombre (`capital`,
`total_ac`) y si el `data.json` traía otro (`capital_social`,
`total_activo_corriente`) la cuenta valía 0 y la minuta reportaba un descuadre
inexistente. Un falso positivo en un documento que va a contabilidad cuesta más
que un hallazgo omitido. Ahora hay lectura tolerante de alias (`pick`) y el
control de subtotales suma TODAS las partidas de la sección en vez de una lista
fija de nombres.

**Detectores estructurales.** Los controles eran todos aritméticos. Se agregaron
tres que miran si el archivo DICE lo que los números son: encabezado de periodo
que no coincide entre estados, rótulo de columna que no coincide con el título
de la hoja, y plan de cuentas que cambia entre ejercicios (una categoría nueva
puede ser reclasificación, y la comparación necesita la salvedad).

**Verificaciones que pasaron.** El renderer ya sabía pintar hallazgos de tipo
`ok` pero nadie los producía. Ahora la minuta deja constancia de la ecuación
patrimonial y del calce del resultado entre estados, por ejercicio.

## `scripts/generate_html.py` — nuevo

El flujo declaraba salida HTML pero no traía generador: lo escribía el modelo a
mano en cada corrida, así que dos corridas sobre el mismo archivo daban dos
reportes distintos. Ahora sale de los mismos JSON que el PPTX. Single-file, CSS
y JS embebidos, waterfall en SVG en línea. Trae reglas `@media print` con salto
de página por lámina, así que el PDF sale imprimiendo.

**Reconciliación obligatoria:** si los tramos del puente no suman el total
declarado, el gráfico NO se dibuja y en su lugar aparece qué falta mapear. Un
waterfall que no cierra significa una partida sin capturar o un subtotal contado
dos veces, y dibujarlo igual produce un gráfico que miente con confianza.

## `templates/slide_kpi_distribution.js` — nuevo

Sólo existía `slide_kpi_restaurants.js`, así que los otros ocho sectores caían
al fallback y la lámina salía con el texto `[Template: slide_kpi_XXX]` impreso
encima. El motor ya calculaba los KPIs sectoriales de distribución con sus
benchmarks; nadie los dibujaba.

---

## Dependencias

Los generadores JS necesitan, en el entorno donde corren:

    npm install docx pptxgenjs

`extract_data.py` necesita `openpyxl`.
