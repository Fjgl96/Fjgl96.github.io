"""1-pager directorio (2 paginas) del FP&A Monthly Pack."""
import json, pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle

BASE = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
d = json.loads((BASE/"data.json").read_text(encoding="utf-8"))
OUT = BASE/"fpa_1pager_jun2026.pdf"

AZUL = HexColor("#0B6D9E"); GRIS = HexColor("#F5F8FD"); LINEA = HexColor("#D9E2EC")
t = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=17, textColor=AZUL, spaceAfter=2*mm)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, textColor=AZUL, spaceBefore=4*mm, spaceAfter=2*mm)
p = ParagraphStyle("p", fontName="Helvetica", fontSize=9, leading=12.5)
small = ParagraphStyle("small", fontName="Helvetica-Oblique", fontSize=7.5, textColor=HexColor("#5F7391"))
b = ParagraphStyle("b", parent=p, fontName="Helvetica-Bold")

def M(v): return f"S/ {v/1e6:,.2f}M".replace(",","_").replace(".",",").replace("_",".")
def K(v): return f"S/ {v/1e3:,.0f}k".replace(",",".")

story = [Paragraph("Distribuidora Andina del Sur S.A.C. — Reporte de Directorio", t),
 Paragraph("Corte junio 2026 (H1) · FP&A Monthly Pack · Caso 100% sintético — ninguna cifra corresponde a una empresa real", small),
 Spacer(1,2*mm),
 Paragraph("1. Titular del mes", h2),
  Paragraph("Vendimos <b>S/ 28,40M</b> vs <b>S/ 30,10M</b> del ppto (<b>−5,6%</b>) y +5,6% vs H1-2025: "
  "crecemos pero ganamos menos — el margen bruto cayó a <b>22,1%</b> (ppto 24,0%; LY 23,2%) por tipo de cambio "
  "(S/ 3,72 → 3,81) y descuentos defensivos en Mayorista. "
  "El <b>EBITDA H1 quedó en S/ 2,35M vs S/ 3,30M</b> (−S/ 950k) y la utilidad neta en <b>S/ 0,66M vs S/ 1,55M</b>. "
  "El ciclo de conversión subió de 64 a <b>79 días</b> (DSO 52, DIO 61, DPO 34): la cobranza institucional y el sobrestock "
  "de Hogar inmovilizaron caja y la deuda CP subió en S/ 2,30M. Sin acción, el año cierra en ventas S/ 58,5M y EBITDA S/ 5,4M.", p),
 Paragraph("2. PyG H1 — LY vs ppto vs real (S/ miles)", h2)]
rows = [["Cuenta","H1-2025","Ppto","Real","Desvío","YoY"]]
for cta,ly,pp,rr in [("Ventas",d["ly_h1"],d["ppto_h1"],d["real_h1"]),("Utilidad bruta",d["ly_ub"],d["ub_ppto"],d["ub_real"]),
 ("EBITDA",d["ly_ebitda"],d["ebitda_ppto"],d["ebitda_real"]),
 ("Utilidad neta",d["ly_net"],d["net_ppto"],d["net_real"])]:
    rows.append([cta, K(ly), K(pp), K(rr), K(rr-pp), f"{(rr/ly-1)*100:+.1f}%".replace(".",",")])
tab = Table(rows, colWidths=[38*mm,26*mm,26*mm,26*mm,26*mm,22*mm])
tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),AZUL),("TEXTCOLOR",(0,0),(-1,0),"white"),
 ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),
 ("GRID",(0,0),(-1,-1),0.5,LINEA),("ALIGN",(1,0),(-1,-1),"RIGHT")]))
story += [tab, Paragraph("Puente de ventas (−S/ 1,70M): volumen −1.100k · precio +250k · mix −450k · descuento −400k. "
 "Puente EBITDA (−S/ 950k): volumen −410k · precio/mix −120k · costo FX −300k · descuento −120k · fletes/personal −180k · ahorro mkt +180k.", small)]
story += [Image(str(BASE/"pvm_ventas.png"), width=170*mm, height=71*mm)]
story += [Paragraph("3. Drill-down: dónde vive el desvío", h2),
 Paragraph("Institucional crece +5,0% YoY pero falla un ppto agresivo (+22,9% vs LY): el desvío de −S/ 876k es presupuesto, "
  "no demanda. Su CxC de S/ 2,00M tiene mora 60+ de S/ 330k concentrada en Red Salud Norte (S/ 90k), VialSur (S/ 50k) y "
  "Gobierno Regional (S/ 70k); DSO del canal: 70 días. En Hogar, 3 SKUs (escobas, trapeadores, bolsas 100L) concentran "
  "S/ 702k con más de 6 meses de cobertura: de ahí el recorte de compra A3.", p),
 Image(str(BASE/"aging_inst.png"), width=165*mm, height=72*mm),
 Paragraph("4. Caja y capital de trabajo", h2),
 Paragraph(f"CxC S/ 8,16M (DSO {d['k_real']['dso']:.0f} d, +7 vs ppto) por morosidad institucional; inventarios S/ 7,45M "
  f"(DIO {d['k_real']['dio']:.0f} d) por sobrestock de Hogar; CxP S/ 4,32M (DPO {d['k_real']['dpo']:.0f} d). "
  "Deuda CP S/ 6,10M (+S/ 2,30M vs dic-25). Ratio deuda/EBITDA LTM 1,80x; cobertura de intereses 3,6x. "
  "Exposición cambiaria neta pasiva USD 1,10M: cada 10 céntimos mueven S/ 110k (≈17% de la neta H1). Sin cobertura vigente.", p),
 Image(str(BASE/"ccc.png"), width=120*mm, height=61*mm),
 Paragraph("5. Decisión propuesta al directorio", h2)]
for a in d["acciones"]:
    story.append(Paragraph(f"<b>{a['id']} · {a['nombre']}.</b> {a['kpi']}. Efecto caja {K(a['efecto_caja'])}; PyG: {a['efecto_py']}.", p))
story += [Paragraph("Se solicita aprobar la línea revolvente por <b>S/ 2,5M</b> para cubrir el pico de octubre (deuda base S/ 11,2M) "
 "y el programa forward del 50% de la exposición a 90 días.", p),
 Paragraph("Anexo: modelo Excel con fórmulas (13 hojas), diccionario y linaje. Metodología: PyG con fórmulas atadas a PPTO_REAL; "
  "balance que cuadra Activo = Pasivo + Patrimonio; KPIs con fórmulas DSO/DIO/DPO; comparativo LY like-for-like; "
  "puentes PVM y EBITDA; drill-down de clientes (aging) y SKUs (cobertura); forecast FY base vs ppto.", small)]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=14*mm,
 title="FP&A Monthly Pack — 1-pager directorio jun-2026 (sintético)")
doc.build(story)
print("pdf OK", OUT.stat().st_size, "bytes")
