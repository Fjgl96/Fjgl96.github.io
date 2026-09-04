"""Genera Excel con formulas + PDF 1-pager + PNGs del FP&A Monthly Pack."""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
d = json.loads((BASE/"data.json").read_text(encoding="utf-8"))

AZUL = "0B6D9E"; AZUL_L = "DFF3FC"; GRIS = "F5F8FD"; VERDE = "0F6B46"; ROJO = "B00020"
H_FILL = PatternFill("solid", fgColor=AZUL); H_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
T_FONT = Font(name="Calibri", bold=True, size=11, color=AZUL)
N_FONT = Font(name="Calibri", size=10); B_FONT = Font(name="Calibri", bold=True, size=10)
MONEY = '#,##0;-#,##0;-'; PCT = '0.0%;0.0%;-'; thin = Side(style="thin", color="D9E2EC")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

def estilo_header(ws, row, ncols):
    for c in range(1, ncols+1):
        cell = ws.cell(row=row, column=c)
        cell.fill = H_FILL; cell.font = H_FONT; cell.alignment = Alignment(horizontal="center", wrap_text=True)

def dinero(ws, row, col, value=None, formula=None, bold=False):
    c = ws.cell(row=row, column=col)
    if formula: c.value = formula
    else: c.value = value
    c.number_format = MONEY; c.font = B_FONT if bold else N_FONT; c.border = BORDER
    return c

wb = Workbook()

# ---------- LEEME ----------
ws = wb.active; ws.title = "LEEME"
ws["A1"] = d["empresa"]; ws["A1"].font = Font(name="Calibri", bold=True, size=14, color=AZUL)
ws["A2"] = "FP&A Monthly Pack — corte Junio 2026 (H1) · Caso 100% sintético"
ws["A2"].font = T_FONT
ws["A4"] = ("AVISO: todas las cifras son inventadas para fines demostrativos. Ningún dato corresponde "
 "a un cliente real. Moneda: soles (PEN). Tasa IR 29.5%. TC ppto 3.72, real prom H1 3.81, cierre jun 3.84.")
ws["A4"].alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[4].height = 30
indice = ["PARAM: supuestos (TC, tasas, calendario)",
 "PPTO_REAL: ventas mensuales ppto vs real ene-jun + acumulado",
 "PyG_H1: estado de resultados H1 con fórmulas, desvíos y márgenes",
 "BAL: balance dic-25 vs jun-26, cuadra Activo = Pasivo + Patrimonio",
 "KPIs: DSO/DIO/DPO/CCC y rentabilidad con semáforos y fórmulas",
 "BRIDGE: puente EBITDA ppto → real (atribuye los -950k)",
 "FX_FORECAST: exposición USD, sensibilidad y forecast FY con plan de acción",
 "DICC: diccionario de campos y linaje"]
for i, t in enumerate(indice, start=6):
    ws.cell(row=i, column=1, value=t).font = N_FONT
ws.column_dimensions["A"].width = 130
for r in [1,2,4]:
    ws.merge_cells(f"A{r}:A{r}")

# ---------- PARAM ----------
ws = wb.create_sheet("PARAM")
params = [("Parámetro","Valor","Fuente / nota"),
 ("TC presupuesto 2026",3.72,"Supuesto anual"),
 ("TC promedio real H1",3.81,"BCRP (sintético)"),
 ("TC cierre junio",3.84,"BCRP (sintético)"),
 ("Tasa IR",0.295,"Régimen general"),
 ("Días H1 (ene-jun)",181,"Calendario"),
 ("% compras en USD",0.70,"Política importaciones"),
 ("Caja mínima operativa",900_000,"Tesorería"),
 ("Presupuesto ventas FY",d["fy"]["ventas_ppto"],"PPTO_2026 aprobado"),
 ("Línea revolvente propuesta",d["fy"]["linea_adicional"],"Banco, por aprobar")]
for r,(a,b,c_) in enumerate([("Parámetro","Valor","Fuente / nota")]+params[0:], start=1):
    for col,v in enumerate([a,b,c_], start=1):
        cell = ws.cell(row=r, column=col, value=v); cell.border = BORDER
        cell.font = H_FONT if r==1 else N_FONT
        if r==1: cell.fill = H_FILL
estilo_header(ws,1,3)
ws["B3"].number_format='0.00'; ws["B4"].number_format='0.00'; ws["B5"].number_format='0.00'
ws["B7"].number_format=PCT; ws["B10"].number_format=MONEY; ws["B11"].number_format=MONEY
for col,w in zip("ABC",(34,22,44)): ws.column_dimensions[col].width=w

# ---------- PPTO_REAL ----------
ws = wb.create_sheet("PPTO_REAL")
hdr = ["Mes","Ppto","Real","Desvío (S/)","Desvío %"]
for c,h in enumerate(hdr,1): ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,5)
for i,m in enumerate(d["meses"][:6], start=2):
    p = d["ppto_m"][i-2]; r_ = d["real_m"][i-2]
    ws.cell(row=i,column=1,value=m).font=N_FONT
    dinero(ws,i,2,p); dinero(ws,i,3,r_)
    dinero(ws,i,4,None,formula=f"=C{i}-B{i}")
    c5 = ws.cell(row=i,column=5); c5.value=f"=IF(B{i}=0,0,C{i}/B{i}-1)"; c5.number_format=PCT; c5.font=N_FONT; c5.border=BORDER
tot = 8
ws.cell(row=tot,column=1,value="H1").font=B_FONT
for col in (2,3): dinero(ws,tot,col,None,formula=f"=SUM({get_column_letter(col)}2:{get_column_letter(col)}7)",bold=True)
dinero(ws,tot,4,None,formula="=C8-B8",bold=True)
c5 = ws.cell(row=tot,column=5); c5.value="=C8/B8-1"; c5.number_format=PCT; c5.font=B_FONT; c5.border=BORDER
for col,w in zip("ABCDE",(10,16,16,16,12)): ws.column_dimensions[col].width=w

# ---------- PyG_H1 ----------
ws = wb.create_sheet("PyG_H1")
for c,h in enumerate(["Cuenta","Ppto H1","Real H1","Desvío","Desv %","Margen real"],1):
    ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,6)
filas = [("Ventas netas",d["ppto_h1"],d["real_h1"],False),
 ("Costo de ventas",d["cogs_ppto"],d["cogs_real"],False),
 ("Utilidad bruta",d["ub_ppto"],d["ub_real"],True),
 ("Gastos operativos",d["opex_ppto"],d["opex_real"],False),
 ("EBITDA",d["ebitda_ppto"],d["ebitda_real"],True),
 ("Depreciación",DEP:=450_000,450_000,False),
 ("EBIT",d["ebit_ppto"],d["ebit_real"],True),
 ("Gastos financieros",d["gf_ppto"],d["gf_real"],False),
 ("Diferencia de cambio",d["dc_ppto"],d["dc_real"],False),
 ("EBT",d["ebt_ppto"],d["ebt_real"],True),
 ("Impuesto a la renta 29.5%",d["ir_ppto"],d["ir_real"],False),
 ("Utilidad neta",d["net_ppto"],d["net_real"],True)]
for i,(cta,p,r_,bold) in enumerate(filas, start=2):
    ws.cell(row=i,column=1,value=cta).font = B_FONT if bold else N_FONT
    dinero(ws,i,2,p,bold=bold); dinero(ws,i,3,r_,bold=bold)
    dinero(ws,i,4,None,formula=f"=C{i}-B{i}",bold=bold)
    c5=ws.cell(row=i,column=5); c5.value=f"=IF(B{i}=0,0,C{i}/B{i}-1)"; c5.number_format=PCT; c5.font=B_FONT if bold else N_FONT; c5.border=BORDER
    c6=ws.cell(row=i,column=6)
    if cta in ("Utilidad bruta","EBITDA","EBIT","EBT","Utilidad neta"):
        c6.value=f"=IF($C$2=0,0,C{i}/$C$2)"; c6.number_format=PCT
    else: c6.value="—"
    c6.font=B_FONT if bold else N_FONT; c6.border=BORDER
for col,w in zip("ABCDEF",(30,16,16,16,10,12)): ws.column_dimensions[col].width=w

# ---------- BAL ----------
ws = wb.create_sheet("BAL")
for c,h in enumerate(["Cuenta","Dic-25","Jun-26","Var S/","Var %"],1): ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,5)
orden = [("Caja",1),("Cuentas por cobrar",1),("Inventarios",1),("Otros AC",1),("ACTIVO CORRIENTE",2),
 ("Activo fijo neto",1),("TOTAL ACTIVO",2),("Cuentas por pagar comerciales",1),
 ("Deuda CP",1),("Otros pasivos CP",1),("TOTAL PASIVO CORRIENTE",2),("Deuda LP",1),
 ("PATRIMONIO",1),("TOTAL PAS+PAT",2)]
Dic = d["bal_dic"]; Jun = d["bal_jun"]
vals = {"Caja":(Dic["caja"],Jun["caja"]),"Cuentas por cobrar":(Dic["cxc"],Jun["cxc"]),
 "Inventarios":(Dic["inv"],Jun["inv"]),"Otros AC":(Dic["otros_ac"],Jun["otros_ac"]),
 "ACTIVO CORRIENTE":(Dic["caja"]+Dic["cxc"]+Dic["inv"]+Dic["otros_ac"],Jun["caja"]+Jun["cxc"]+Jun["inv"]+Jun["otros_ac"]),
 "Activo fijo neto":(Dic["af_neto"],Jun["af_neto"]),
 "TOTAL ACTIVO":(Dic["caja"]+Dic["cxc"]+Dic["inv"]+Dic["otros_ac"]+Dic["af_neto"],Jun["caja"]+Jun["cxc"]+Jun["inv"]+Jun["otros_ac"]+Jun["af_neto"]),
 "Cuentas por pagar comerciales":(Dic["cxp"],Jun["cxp"]),"Deuda CP":(Dic["deuda_cp"],Jun["deuda_cp"]),
 "Otros pasivos CP":(Dic["otros_pc"],Jun["otros_pc"]),
 "TOTAL PASIVO CORRIENTE":(Dic["cxp"]+Dic["deuda_cp"]+Dic["otros_pc"],Jun["cxp"]+Jun["deuda_cp"]+Jun["otros_pc"]),
 "Deuda LP":(Dic["deuda_lp"],Jun["deuda_lp"]),"PATRIMONIO":(Dic["patrimonio"],Jun["patrimonio"]),
 "TOTAL PAS+PAT":(Dic["cxp"]+Dic["deuda_cp"]+Dic["otros_pc"]+Dic["deuda_lp"]+Dic["patrimonio"],
                  Jun["cxp"]+Jun["deuda_cp"]+Jun["deuda_cp"]*0+Jun["otros_pc"]+Jun["deuda_lp"]+Jun["patrimonio"])}
r = 2
for cta,_ in orden:
    a,b = vals[cta]; bold = cta.isupper()
    ws.cell(row=r,column=1,value=cta).font = B_FONT if bold else N_FONT
    dinero(ws,r,2,a,bold=bold); dinero(ws,r,3,b,bold=bold)
    dinero(ws,r,4,None,formula=f"=C{r}-B{r}",bold=bold)
    c5=ws.cell(row=r,column=5); c5.value=f"=IF(B{r}=0,0,C{r}/B{r}-1)"; c5.number_format=PCT; c5.font=B_FONT if bold else N_FONT; c5.border=BORDER
    r += 1
ws.cell(row=r+1,column=1,value="Check: Activo − (Pas+Pat) = 0 →").font=B_FONT
dinero(ws,r+1,2,None,formula=f"=C8-C15",bold=True)
for col,w in zip("ABCDE",(32,16,16,16,10)): ws.column_dimensions[col].width=w

# ---------- KPIs ----------
ws = wb.create_sheet("KPIs")
for c,h in enumerate(["KPI","Dic-25","Ppto H1","Real H1","Desv vs ppto","Semáforo"],1): ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,6)
k = d["k_real"]; kd = d["k_dic"]
krows = [("DSO (días)",kd["dso"],45.0,k["dso"],"alto malo"),
 ("DIO (días)",kd["dio"],56.0,k["dio"],"alto malo"),
 ("DPO (días)",kd["dpo"],34.0,k["dpo"],"alto bueno"),
 ("CCC (días)",kd["ccc"],67.0,k["ccc"],"alto malo"),
 ("Margen bruto %",None,24.0,round(d["ub_real"]/d["real_h1"]*100,1),"alto bueno"),
 ("Margen EBITDA %",None,round(d["ebitda_ppto"]/d["ppto_h1"]*100,1),round(d["ebitda_real"]/d["real_h1"]*100,1),"alto bueno"),
 ("Deuda total / EBITDA LTM (x)",1.45,1.40,1.80,"alto malo"),
 ("Cobertura intereses (x)",4.8,4.5,3.6,"alto bueno")]
for i,(n,dic_,pp,real,crit) in enumerate(krows, start=2):
    ws.cell(row=i,column=1,value=n).font=N_FONT
    ws.cell(row=i,column=2,value=dic_).font=N_FONT
    ws.cell(row=i,column=3,value=pp).font=N_FONT
    ws.cell(row=i,column=4,value=real).font=B_FONT
    c5=ws.cell(row=i,column=5); c5.value=f"=D{i}-C{i}"; c5.number_format='0.0'; c5.font=N_FONT; c5.border=BORDER
    for col in (2,3,4): ws.cell(row=i,column=col).border=BORDER
    sem = ws.cell(row=i,column=6)
    if "bueno" in crit: sem.value = "OK" if real>=pp or (crit=="alto malo" and real<=pp) else "Alerta"
    else: sem.value = "Alerta" if (crit=="alto malo" and real>pp) else "OK"
    sem.font=B_FONT; sem.border=BORDER
    # correccion simple: para alto-bueno OK si real>=pp; alto-malo OK si real<=pp
    if crit=="alto bueno": sem.value = "OK" if real>=pp else "Alerta"
    else: sem.value = "OK" if real<=pp else "Alerta"
for col,w in zip("ABCDEF",(30,12,12,12,14,12)): ws.column_dimensions[col].width=w

# ---------- BRIDGE ----------
ws = wb.create_sheet("BRIDGE")
for c,h in enumerate(["Paso","Monto (S/)","Acumulado"],1): ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,3)
acum = 0
for i,b in enumerate(d["bridge"], start=2):
    ws.cell(row=i,column=1,value=b["paso"]).font = B_FONT if i in (2,9) else N_FONT
    dinero(ws,i,2,b["monto"],bold=(i in (2,9)))
    if i==2: acum = b["monto"]
    elif i<9: acum += b["monto"]
    else: acum = b["monto"]
    dinero(ws,i,3,acum,bold=(i in (2,9)))
for col,w in zip("ABC",(40,16,16)): ws.column_dimensions[col].width=w

# ---------- FX_FORECAST ----------
ws = wb.create_sheet("FX_FORECAST")
ws["A1"]="Exposición cambiaria (jun-26)"; ws["A1"].font=T_FONT
fxrows = [("CxP exterior (USD)",d["fx"]["cxp_usd"]),("Caja USD",-d["fx"]["caja_usd"]),
 ("Exposición neta pasiva (USD)",d["fx"]["exposicion_usd"]),
 ("Sensibilidad por 10 cts (PEN)",d["fx"]["sens_10cts"]),
 ("% sobre utilidad neta H1",d["fx"]["pct_neta"])]
for i,(a,b) in enumerate(fxrows, start=2):
    ws.cell(row=i,column=1,value=a).font=N_FONT
    dinero(ws,i,2,b)
ws["A8"]="Forecast FY26 — escenario base con plan de acción"; ws["A8"].font=T_FONT
for c,h in enumerate(["Concepto","Ppto FY","Base FY","Desvío"],1): ws.cell(row=9,column=c,value=h)
estilo_header(ws,9,4)
frowns = [("Ventas",d["fy"]["ventas_ppto"],d["fy"]["ventas_base"]),
 ("EBITDA",d["fy"]["ebitda_ppto"],d["fy"]["ebitda_base"]),
 ("Utilidad neta",d["fy"]["neta_ppto"],d["fy"]["neta_base"])]
for i,(a,p,b_) in enumerate(frowns, start=10):
    ws.cell(row=i,column=1,value=a).font=N_FONT
    dinero(ws,i,2,p); dinero(ws,i,3,b_); dinero(ws,i,4,None,formula=f"=C{i}-B{i}")
ws.cell(row=13,column=1,value="Pico deuda octubre (base)").font=N_FONT; dinero(ws,13,2,d["fy"]["pico_deuda_oct"])
ws.cell(row=14,column=1,value="Línea adicional propuesta").font=N_FONT; dinero(ws,14,2,d["fy"]["linea_adicional"])
ws.cell(row=16,column=1,value="Plan de acción (efectos 2H)").font=T_FONT
for c,h in enumerate(["ID","Acción","Efecto caja","Efecto PyG","KPI"],1): ws.cell(row=17,column=c,value=h)
estilo_header(ws,17,5)
for i,a in enumerate(d["acciones"], start=18):
    ws.cell(row=i,column=1,value=a["id"]).font=N_FONT
    ws.cell(row=i,column=2,value=a["nombre"]).font=N_FONT
    dinero(ws,i,3,a["efecto_caja"])
    ws.cell(row=i,column=4,value=a["efecto_py"]).font=N_FONT
    ws.cell(row=i,column=5,value=a["kpi"]).font=N_FONT
for col,w in zip("ABCDE",(34,42,16,30,30)): ws.column_dimensions[col].width=w

# ---------- DICC ----------
ws = wb.create_sheet("DICC")
for c,h in enumerate(["Campo","Definición","Origen"],1): ws.cell(row=1,column=c,value=h)
estilo_header(ws,1,3)
dicc = [("Ventas netas","Ventas brutas menos devoluciones y descuentos","ERP ventas (sintético)"),
 ("DSO","CxC / ventas diarias","Balance + PyG"),
 ("DIO","Inventarios / costo diario","Balance + PyG"),
 ("DPO","CxP / compras diarias","Balance + compras"),
 ("CCC","DSO + DIO − DPO","Calculado"),
 ("Exposición USD","CxP USD − caja USD","Tesorería"),
 ("Bridge EBITDA","Atribución volumen/precio/FX/descuento/opex","FP&A"),
 ("Forecast base","Ventas 58.5M, EBITDA 5.4M, pico deuda oct 11.2M","Modelo + acciones A1-A5")]
for i,(a,b,c_) in enumerate(dicc, start=2):
    for col,v in enumerate([a,b,c_],1):
        cell=ws.cell(row=i,column=col,value=v); cell.font=N_FONT; cell.border=BORDER; cell.alignment=Alignment(wrap_text=True,vertical="top")
for col,w in zip("ABC",(24,60,32)): ws.column_dimensions[col].width=w

for ws in wb.worksheets:
    ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.save(BASE/"fpa_pack_jun2026.xlsx")
print("xlsx OK")

# ---------- PNGs ----------
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
# 1. Ventas ppto vs real
fig,ax = plt.subplots(figsize=(9,4))
x = range(6); w=0.35
ax.bar([i-w/2 for i in x],[v/1e6 for v in d["ppto_m"][:6]],width=w,label="Ppto",color="#0B6D9E")
ax.bar([i+w/2 for i in x],[v/1e6 for v in d["real_m"][:6]],width=w,label="Real",color="#149DDD")
ax.set_xticks(list(x),d["meses"][:6]); ax.set_ylabel("S/ millones"); ax.set_title("Ventas H1 2026: real vs ppto (−5.6%, −S/ 1.70M)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(BASE/"ventas_ppto_real.png",dpi=150); plt.close(fig)
# 2. Bridge waterfall simplificado
labels=[b["paso"] for b in d["bridge"]]; vals=[b["monto"]/1e3 for b in d["bridge"]]
fig,ax=plt.subplots(figsize=(10,4.2))
cum=vals[0]; xs=list(range(len(labels))); colors=[]
heights=[]; bottoms=[]
for i,v in enumerate(vals):
    if i==0 or i==len(vals)-1: heights.append(v if i==0 else v); bottoms.append(0); colors.append("#0B6D9E")
    else: bottoms.append(cum); heights.append(v); colors.append("#149DDD" if v>0 else "#C0392B"); cum+=v
ax.bar(xs,heights,bottom=bottoms,color=colors)
ax.set_xticks(xs,labels,rotation=18,ha="right",fontsize=8)
ax.set_ylabel("S/ miles"); ax.set_title("Puente EBITDA H1: ppto S/ 3.30M → real S/ 2.35M (−S/ 950k)")
fig.tight_layout(); fig.savefig(BASE/"bridge_ebitda.png",dpi=150); plt.close(fig)
# 3. CCC
fig,ax=plt.subplots(figsize=(7,3.6))
ax.bar(["Dic-25","Real jun-26"],[d["k_dic"]["ccc"],d["k_real"]["ccc"]],color=["#90A4AE","#0B6D9E"])
ax.set_ylabel("Días"); ax.set_title("Ciclo de conversión: 64 → 79 días (+15)")
for i,v in enumerate([d["k_dic"]["ccc"],d["k_real"]["ccc"]]): ax.text(i,v+1,f"{v:.0f} d",ha="center",fontweight="bold")
fig.tight_layout(); fig.savefig(BASE/"ccc.png",dpi=150); plt.close(fig)
print("pngs OK")
