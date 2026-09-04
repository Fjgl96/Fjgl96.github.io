# FP&A Monthly Pack — Distribuidora Andina del Sur S.A.C. (caso sintético)

Corte junio 2026 (H1). Todas las cifras son **inventadas**; ninguna corresponde a una empresa real.
Moneda: soles (PEN). Escala: ventas ppto FY S/ 60.2M (~US$ 16M).

## Archivos

| Archivo | Qué es |
|---|---|
| `fpa_pack_jun2026.xlsx` | Modelo abierto, 13 hojas con fórmulas: LEEME · PARAM · PPTO_REAL · PyG_H1 · BAL · KPIs · BRIDGE · COMP_LY · PUENTE_VENTAS · DRILL_CLIENTES · DRILL_SKUS · FX_FORECAST · DICC |
| `fpa_1pager_jun2026.pdf` | 1-pager de directorio: titular, PyG, puente EBITDA, caja y decisión A1–A5 |
| `data.json` | Números canónicos del caso (lo que la ficha declara es lo que el Excel devuelve) |
| `gen_data.py` | Define el caso y verifica invariantes (patrimonio ata con resultado H1) |
| `gen_modelo.py` | Escribe el Excel con fórmulas + gráficos PNG |
| `gen_pdf.py` | Genera el 1-pager (ReportLab) |

## Números canónicos (verificables)

- Ventas H1: real S/ 28.40M vs ppto S/ 30.10M (−5.6%, −S/ 1.70M) y +5.6% vs H1-2025 (S/ 26.90M)
- Puente PVM: volumen −1.10M · precio +250k · mix −450k · descuento −400k
- Utilidad bruta: S/ 6.28M (22.1%) vs S/ 7.22M (24.0%); LY 23.2%
- EBITDA: S/ 2.35M (8.3%) vs S/ 3.30M (11.0%) → desvío −S/ 950k
- Puente EBITDA: volumen −410k · precio/mix −120k · costo FX −300k · descuento −120k · fletes/personal −180k · ahorro mkt +180k
- Drill-down cobranza: CxC institucional S/ 2.00M en 8 clientes, mora 60+ S/ 330k, DSO del canal 70 días
- Drill-down inventarios: Hogar S/ 3.35M en 8 SKUs, 3 con +6 meses de cobertura (S/ 702k)
- Utilidad neta: S/ 0.66M vs S/ 1.55M
- Balance jun-26: activo S/ 25.31M = pasivo + patrimonio S/ 25.31M (cuadra)
- Capital de trabajo: DSO 52 · DIO 61 · DPO 34 · CCC 79 días (dic-25: 64)
- FX: exposición neta pasiva USD 1.10M; 10 céntimos = S/ 110k (≈17% de la neta H1)
- Forecast FY base: ventas S/ 58.5M, EBITDA S/ 5.4M, pico de deuda en octubre S/ 11.2M → línea +S/ 2.5M

## Reglas del modelo

- Ningún total se escribe a mano: todo desvío es `=REAL−PPTO` y todo margen es `=CUENTA/VENTAS`.
- El balance trae su check `Activo − (Pas+Pat) = 0` y el patrimonio de jun-26 ata con la utilidad neta del H1.
- Reproducible: `python gen_data.py && python gen_modelo.py && python gen_pdf.py` (requiere `openpyxl`, `matplotlib`, `reportlab`).

## Licencia de uso

Material demostrativo del portafolio de Francisco Guerrero. Puede descargarse y reutilizarse como plantilla
citando la fuente. No constituye asesoría ni recomendación de inversión.
