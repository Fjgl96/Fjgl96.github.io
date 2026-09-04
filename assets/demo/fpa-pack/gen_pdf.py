"""1-pager directorio del FP&A Monthly Pack (numeros 100% desde data.json)."""
import json
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle

BASE = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
d = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
OUT = BASE / "fpa_1pager_jun2026.pdf"

AZUL = HexColor("#0B6D9E"); LINEA = HexColor("#D9E2EC")
t = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=17, textColor=AZUL, spaceAfter=2 * mm)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, textColor=AZUL, spaceBefore=4 * mm, spaceAfter=2 * mm)
p = ParagraphStyle("p", fontName="Helvetica", fontSize=9, leading=12.5)
small = ParagraphStyle("small", fontName="Helvetica-Oblique", fontSize=7.5, textColor=HexColor("#5F7391"))


def M(v):
    return f"S/ {v / 1e6:,.2f}M".replace(",", "_").replace(".", ",").replace("_", ".")


def K(v):
    return ("-" if v < 0 else "") + f"S/ {abs(v) / 1e3:,.0f}k".replace(",", ".")


def pct(x):
    return f"{x:+.1f}%".replace(".", ",")


mg_r = d["ub_real"] / d["real_h1"] * 100
mg_p = d["ub_ppto"] / d["ppto_h1"] * 100
mg_ly = d["ly_ub"] / d["ly_h1"] * 100
yoy = (d["real_h1"] / d["ly_h1"] - 1) * 100

story = [Paragraph(f"{d['empresa']} — Reporte de Directorio", t),
 Paragraph("Corte junio 2026 (H1) · FP&A Monthly Pack · Caso 100% sintético — ninguna cifra corresponde a una empresa real", small),
 Spacer(1, 2 * mm),
 Paragraph("1. Titular del mes", h2),
 Paragraph(
  f"({pct(d['real_h1'] / d['ppto_h1'] * 100 - 100)}) y {pct(yoy)} vs H1-2025: "
  f"crecemos pero ganamos menos. Margen bruto {mg_r:.1f}% (ppto {mg_p:.1f}%; LY {mg_ly:.1f}%) "
  f"por tipo de cambio (S/ {d['tc_ppto']} → {d['tc_real']}) y descuentos defensivos. "
  f"EBITDA H1 {M(d['ebitda_real'])} vs {M(d['ebitda_ppto'])} "
  f"({K(d['ebitda_real'] - d['ebitda_ppto'])}); neta {K(d['net_real'])} vs {K(d['net_ppto'])}. "
  f"CCC de {d['k_dic']['ccc']:.0f} a {d['k_real']['ccc']:.0f} días "
  f"(DSO {d['k_real']['dso']:.0f}, DIO {d['k_real']['dio']:.0f}, DPO {d['k_real']['dpo']:.0f}). "
  f"Año base: ventas {M(d['fy']['ventas_base'])}, EBITDA {M(d['fy']['ebitda_base'])}.", p),
 Paragraph("2. PyG H1 — LY vs ppto vs real (S/ miles)", h2)]
rows = [["Cuenta", "H1-2025", "Ppto", "Real", "Desvío", "YoY"]]
for cta, ly, pp, rr in [("Ventas", d["ly_h1"], d["ppto_h1"], d["real_h1"]),
 ("Utilidad bruta", d["ly_ub"], d["ub_ppto"], d["ub_real"]),
 ("EBITDA", d["ly_ebitda"], d["ebitda_ppto"], d["ebitda_real"]),
 ("Utilidad neta", d["ly_net"], d["net_ppto"], d["net_real"])]:
    rows.append([cta, K(ly), K(pp), K(rr), K(rr - pp), pct(rr / ly * 100 - 100)])
tab = Table(rows, colWidths=[38 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm, 22 * mm])
tab.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
 ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
 ("GRID", (0, 0), (-1, -1), 0.5, LINEA), ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
pvm = " · ".join(f"{b['paso'].split('(')[0].strip()} {K(b['monto'])}" for b in d["pvm"][1:-1])
eb = " · ".join(f"{b['paso'].split('(')[0].strip()} {K(b['monto'])}" for b in d["bridge"][1:-1])
story += [tab, Paragraph(f"Puente de ventas ({K(d['real_h1'] - d['ppto_h1'])}): {pvm}. "
 f"Puente EBITDA ({K(d['ebitda_real'] - d['ebitda_ppto'])}), reconciliado a margen estándar "
 f"{d['ub_ppto'] / d['ppto_h1'] * 100:.1f}%: {eb}.".replace(".", ","), small)]
story += [Image(str(BASE / "pvm_ventas.png"), width=170 * mm, height=71 * mm)]
# top morosos y sobrestock desde el seed
cli = sorted(d["clientes_inst"], key=lambda c: -c["mora60"])[:4]
top4 = sum(c["mora60"] for c in cli)
story += [Paragraph("3. Drill-down: dónde vive el desvío", h2),
 Paragraph(f"Constructor crece {pct(d['canal_real']['Constructor'] / d['ly_canal']['Constructor'] * 100 - 100)} YoY "
  f"pero falla un ppto agresivo ({pct(d['canal_ppto']['Constructor'] / d['ly_canal']['Constructor'] * 100 - 100)} vs LY): "
  f"el desvío es de presupuesto, no de demanda. Su CxC de {M(d['cxc_canal']['Constructor'])} "
  f"tiene mora 60+ de {K(d['mora60'])} concentrada en cuatro —"
  f"{', '.join(c['nombre'] + ' ' + K(c['mora60']) for c in cli)} "
  f"({K(top4)} entre los cuatro)— y un DSO del canal de "
  f"{d['cxc_canal']['Constructor'] / (d['canal_real']['Constructor'] / 181):.0f} días. "
  f"En Acabados, 3 SKUs concentran {K(d['sobrestock'])} con más de 6 meses de cobertura.".replace(".", ","), p),
 Image(str(BASE / "aging_inst.png"), width=165 * mm, height=72 * mm),
 Paragraph("4. Caja y capital de trabajo", h2),
 Paragraph(f"CxC {M(d['bal_jun']['cxc'])} (DSO {d['k_real']['dso']:.0f} d) por morosidad constructor; "
  f"inventarios {M(d['bal_jun']['inv'])} (DIO {d['k_real']['dio']:.0f} d) por sobrestock de Acabados; "
  f"CxP {M(d['bal_jun']['cxp'])} (DPO {d['k_real']['dpo']:.0f} d). "
  f"Deuda CP {M(d['bal_jun']['deuda_cp'])} (+{M(d['bal_jun']['deuda_cp'] - d['bal_dic']['deuda_cp'])} vs dic-25). "
  f"Deuda/EBITDA LTM {d['supuestos']['deuda_ebitda']}x; cobertura {d['supuestos']['cobertura']}x. "
  f"Exposición cambiaria neta pasiva USD {d['fx']['exposicion_usd'] / 1e3:.0f}k: cada 10 céntimos mueven "
  f"{K(d['fx']['sens_10cts'])} (≈{d['fx']['pct_neta']}% de la neta H1). Sin cobertura vigente.".replace(".", ","), p),
 Image(str(BASE / "ccc.png"), width=120 * mm, height=61 * mm),
 Paragraph(f"El flujo H1 ata la historia: neta {K(d['flujo']['neta'])} + depreciación {K(d['flujo']['dep'])} "
  f"− capital de trabajo {K(-(d['flujo']['d_cxc'] + d['flujo']['d_inv'] + d['flujo']['d_cxp_com'] + d['flujo']['d_otros_pc']))} "
  f"= flujo operativo {K(d['flujo']['fco'])}; menos capex {K(d['flujo']['capex'])} "
  f"más deuda neta +{K(d['flujo']['d_deuda_cp'] + d['flujo']['d_deuda_lp'])} "
  f"= caja {K(d['flujo']['d_caja'])}, el saldo del balance.", p),
 Image(str(BASE / "flujo_h1.png"), width=170 * mm, height=71 * mm),
 Paragraph("5. Decisión propuesta al directorio", h2)]
for a in d["acciones"]:
    story.append(Paragraph(f"<b>{a['id']} · {a['nombre']}.</b> {a['kpi']}. Efecto caja {K(a['efecto_caja'])}; PyG: {a['efecto_py']}.", p))
story += [Paragraph(f"Se solicita aprobar la línea revolvente por <b>{M(d['fy']['linea_adicional'])}</b> "
 f"para cubrir el pico de octubre (deuda base {M(d['fy']['pico_deuda_oct'])}) "
 "y el programa forward del 50% de la exposición a 90 días.", p),
 Paragraph("Anexo: modelo Excel con fórmulas (15 hojas), diccionario y linaje. Metodología: PyG con fórmulas atadas a PPTO_REAL; "
  "balance que cuadra Activo = Pasivo + Patrimonio; flujo indirecto que ata a caja; KPIs con fórmulas DSO/DIO/DPO; comparativo LY like-for-like; "
  "puentes PVM y EBITDA reconciliados; drill-down de clientes (aging) y SKUs (cobertura); forecast FY base vs ppto.", small)]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
 title="FP&A Monthly Pack — 1-pager directorio jun-2026 (sintético)")
doc.build(story)
print("pdf OK", OUT.stat().st_size, "bytes")
