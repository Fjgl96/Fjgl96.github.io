# FP&A Monthly Pack — Comercial Los Álamos S.A.C. (caso sintético)

Distribuidora de materiales de construcción, 40% de compras en USD.
Corte junio 2026 (H1). Todas las cifras son **inventadas**; ninguna corresponde a una empresa real.
Moneda: soles (PEN). Escala: ventas ppto FY S/ 24.0M.

## Archivos

| Archivo | Qué es |
|---|---|
| `fpa_pack_jun2026.xlsx` | Modelo abierto, 15 hojas con fórmulas: LEEME · PARAM · PPTO_REAL · PyG_H1 · BAL · KPIs · BRIDGE · FLUJO · FORECAST_H2 · COMP_LY · PUENTE_VENTAS · DRILL_CLIENTES · DRILL_SKUS · FX_FORECAST · DICC |
| `fpa_1pager_jun2026.pdf` | 1-pager de directorio: titular, PyG, puentes, drill-down, caja y decisión A1–A5 |
| `data.json` | Números canónicos del caso (lo que la ficha declara es lo que el Excel devuelve) |
| `gen_data.py` | Define el caso y verifica invariantes (patrimonio ata con resultado H1, flujo ata a caja) |
| `gen_modelo.py` | Escribe el Excel con fórmulas + gráficos PNG |
| `gen_pdf.py` | Genera el 1-pager (ReportLab) |
| `gen_supabase.py` | Genera `fpa_schema.sql` desde `data.json` (estrella mes×canal×línea×versión) |
| `fpa_schema.sql` | DDL + RLS + 5 vistas + seed correctivo DO UPDATE (pegar en SQL Editor, re-ejecutable) |

## Números canónicos (verificables)

- Ventas H1: real S/ 11.30M vs ppto S/ 12.00M (−5.8%, −S/ 700k) y +5.6% vs H1-2025 (S/ 10.70M)
- Puente PVM: volumen −450k · precio +110k · mix −180k · descuento −180k
- Utilidad bruta: S/ 2.73M (24.2%) vs S/ 3.12M (26.0%); LY 25.1%
- EBITDA: S/ 1.05M (9.3%) vs S/ 1.44M (12.0%) → desvío −S/ 390k
- Puente EBITDA reconciliado (margen std 26%): volumen −117k · precio/mix/desc −65k · costo FX −120k · otros −83k · opex −5k
- Flujo H1: FCO −S/ 340k + capex −S/ 170k + deuda neta +S/ 410k = caja −S/ 100k (ata al balance)
- Drill-down cobranza: CxC Constructor S/ 800k en 8 clientes, mora 60+ S/ 132k, DSO del canal 37.7 días
- Drill-down inventarios: Acabados S/ 1.39M en 8 SKUs, 3 con +6 meses de cobertura (S/ 209k)
- Utilidad neta: S/ 342k vs S/ 705k
- Balance jun-26: activo S/ 10.04M = pasivo + patrimonio S/ 10.04M (cuadra)
- Capital de trabajo: DSO 52 · DIO 61 · DPO 34 · CCC 79 días (dic-25: 67)
- FX: exposición neta pasiva USD 180k; 10 céntimos = S/ 18k (≈5% de la neta H1)
- Forecast FY base: ventas S/ 23.1M, EBITDA S/ 2.25M, pico de deuda en octubre S/ 4.5M → línea +S/ 1.0M

## Reglas del modelo

- Ningún total se escribe a mano: todo desvío es `=REAL−PPTO` y todo margen es `=CUENTA/VENTAS`.
- El balance trae su check `Activo − (Pas+Pat) = 0` y el patrimonio de jun-26 ata con la utilidad neta del H1.
- Reproducible: `python gen_data.py && python gen_modelo.py && python gen_pdf.py` (requiere `openpyxl`, `matplotlib`, `reportlab`).

## Licencia de uso

Material demostrativo del portafolio de Francisco Guerrero. Puede descargarse y reutilizarse como plantilla
citando la fuente. No constituye asesoría ni recomendación de inversión.
