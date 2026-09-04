"""Generador del caso sintetico FP&A Monthly Pack - Distribuidora Andina del Sur S.A.C.
100% inventado. Ninguna cifra corresponde a empresa real.
"""
import json, pathlib
OUT = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
OUT.mkdir(parents=True, exist_ok=True)

EMPRESA = "Distribuidora Andina del Sur S.A.C."
CORTE = "Junio 2026 (H1)"
MONEDA = "PEN (soles)"
TASA_IR = 0.295

MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
# Presupuesto mensual 2026 (PEN)
PPTO_M = [4_600_000,4_400_000,5_000_000,5_000_000,5_200_000,5_900_000,
          5_200_000,5_000_000,4_900_000,5_100_000,5_000_000,4_900_000]
REAL_M = [4_550_000,4_200_000,4_750_000,4_700_000,4_850_000,5_350_000,
          None,None,None,None,None,None]
# Canales H1 real vs ppto (PEN)
CANAL_PPTO_H1 = {"Mayorista":13_545_000,"Minorista":10_535_000,"Institucional":6_020_000}
CANAL_REAL_H1 = {"Mayorista":13_314_000,"Minorista":9_942_000,"Institucional":5_144_000}
# Lineas H1
LINEA_PPTO_H1 = {"Abarrotes importados":19_565_000,"Cuidado del hogar":10_535_000}
LINEA_REAL_H1 = {"Abarrotes importados":18_768_000,"Cuidado del hogar":9_632_000}
TC_PPTO = 3.72
TC_REAL_PROM_H1 = 3.81
TC_JUN = 3.84

PPTO_H1 = sum(PPTO_M[:6]); REAL_H1 = sum([x for x in REAL_M[:6] if x])
FY_PPTO = sum(PPTO_M)
assert PPTO_H1 == 30_100_000 and REAL_H1 == 28_400_000 and FY_PPTO == 60_200_000

MG_PPTO = 0.240; MG_REAL = 0.221
UB_PPTO_H1 = round(PPTO_H1*MG_PPTO); UB_REAL_H1 = round(REAL_H1*MG_REAL)
COGS_PPTO_H1 = PPTO_H1-UB_PPTO_H1; COGS_REAL_H1 = REAL_H1-UB_REAL_H1
# Opex: fletes suben pero se compensan
OPEX_PPTO_H1 = 3_924_000
OPEX_REAL_H1 = 3_926_400
EBITDA_PPTO_H1 = UB_PPTO_H1-OPEX_PPTO_H1
EBITDA_REAL_H1 = UB_REAL_H1-OPEX_REAL_H1
DEP_H1 = 450_000
EBIT_PPTO = EBITDA_PPTO_H1-DEP_H1; EBIT_REAL = EBITDA_REAL_H1-DEP_H1
GF_PPTO = 550_000; GF_REAL = 680_000
DC_PPTO = -100_000; DC_REAL = -280_000
EBT_PPTO = EBIT_PPTO-GF_PPTO+DC_PPTO
EBT_REAL = EBIT_REAL-GF_REAL+DC_REAL
IR_PPTO = round(EBT_PPTO*TASA_IR); IR_REAL = round(EBT_REAL*TASA_IR)
NET_PPTO = EBT_PPTO-IR_PPTO; NET_REAL = EBT_REAL-IR_REAL

# Bridge EBITDA ppto->real (suma = desvio)
BRIDGE = [
 ("EBITDA ppto", EBITDA_PPTO_H1),
 ("Efecto volumen", -410_000),
 ("Efecto precio / mix", -120_000),
 ("Efecto costo FX (TC 3.72->3.81)", -300_000),
 ("Descuento comercial defensivo", -120_000),
 ("Fletes y personal", -180_000),
 ("Ahorro marketing y variables", 180_000),
 ("EBITDA real H1", EBITDA_REAL_H1),
]
assert sum(v for _,v in BRIDGE[1:-1]) == EBITDA_REAL_H1-EBITDA_PPTO_H1

# Balance dic-25 vs jun-26
BAL_DIC = {"caja":1_200_000,"cxc":6_800_000,"inv":6_650_000,"otros_ac":400_000,
 "af_neto":8_450_000,"cxp":4_500_000,"deuda_cp":3_800_000,"otros_pc":1_000_000,
 "deuda_lp":4_970_000,"patrimonio":9_230_000}
BAL_JUN = {"caja":950_000,"cxc":8_160_000,"inv":7_450_000,"otros_ac":400_000,
 "af_neto":8_350_000,"cxp":4_320_000,"deuda_cp":6_097_300,"otros_pc":1_100_000,
 "deuda_lp":3_900_000,"patrimonio":9_892_700}
def bal_total(b):
    ac=b["caja"]+b["cxc"]+b["inv"]+b["otros_ac"]; tot=ac+b["af_neto"]
    pc=b["cxp"]+b["deuda_cp"]+b["otros_pc"]; pas_pat=pc+b["deuda_lp"]+b["patrimonio"]
    return ac,tot,pc,pas_pat
for nombre,b in [("dic",BAL_DIC),("jun",BAL_JUN)]:
    ac,tot,pc,pp=bal_total(b); assert tot==pp, (nombre,tot,pp)
# patrimonio jun = dic + neta H1 (sin dividendos en el caso)
assert BAL_JUN["patrimonio"]-BAL_DIC["patrimonio"]==NET_REAL, "patrimonio debe atar con resultado H1"

# KPIs
DIAS_H1 = 181
def kpis(b, ventas_h1, cogs_h1):
    v_d=ventas_h1/DIAS_H1; c_d=cogs_h1/DIAS_H1
    compras=cogs_h1+(b["inv"]-BAL_DIC["inv"]); comp_d=compras/DIAS_H1
    dso=b["cxc"]/v_d; dio=b["inv"]/c_d; dpo=b["cxp"]/comp_d
    return {"dso":dso,"dio":dio,"dpo":dpo,"ccc":dso+dio-dpo,
            "v_d":v_d,"c_d":c_d,"compras":compras}
K_PPTO = kpis({"cxc":7_060_000,"inv":7_060_000,"cxp":4_350_000}, PPTO_H1, COGS_PPTO_H1)
# K_PPTO usa niveles ppto implicitos coherentes con DSO45/DIO56/DPO34 aprox
K_REAL = kpis(BAL_JUN, REAL_H1, COGS_REAL_H1)
K_DIC = {"dso":45.3,"dio":58.1,"dpo":39.2,"ccc":64.2}

# FX
FX = {"exposicion_usd":1_100_000,"cxp_usd":1_350_000,"caja_usd":250_000,
      "sens_10cts":110_000,"pct_neta":round(110_000/NET_REAL*100,1)}
# Forecast FY base con plan de accion
FY = {"ventas_base":58_500_000,"ebitda_base":5_400_000,"neta_base":1_700_000,
      "ventas_ppto":60_200_000,"ebitda_ppto":6_700_000,"neta_ppto":3_100_000,
      "pico_deuda_oct":11_200_000,"linea_adicional":2_500_000}
ACCIONES = [
 {"id":"A1","nombre":"Cobranza institucional + pronto pago","efecto_caja":950_000,"efecto_py":"- S/ 60k descuento financiero","kpi":"DSO 52 -> 46 dias"},
 {"id":"A2","nombre":"Ajuste lista de precios 2H (+2%)","efecto_caja":550_000,"efecto_py":"+ S/ 550k margen","kpi":"Margen bruto +90 pbs en 2H"},
 {"id":"A3","nombre":"Recorte compra hogar -15%","efecto_caja":700_000,"efecto_py":"neutro","kpi":"DIO 61 -> 55 dias"},
 {"id":"A4","nombre":"Forward 50% exposicion 90 dias","efecto_caja":0,"efecto_py":"acota riesgo 110k -> 55k por 10 cts","kpi":"Exposicion neta USD 1.10M -> 0.55M"},
 {"id":"A5","nombre":"Linea revolvente +S/ 2.5M","efecto_caja":2_500_000,"efecto_py":"- S/ 90k intereses 2H","kpi":"Cubre pico de octubre"}]

# ---------- V2: comparativo LY, puente precio-volumen-mix, drill-down ----------
# H1-2025 (año anterior, real). Institucional crece YoY pero falla un ppto agresivo (+22.9% vs LY).
LY_H1 = 26_900_000
LY_CANAL = {"Mayorista":12_600_000,"Minorista":9_400_000,"Institucional":4_900_000}
assert sum(LY_CANAL.values()) == LY_H1
LY_LINEA = {"Abarrotes importados":17_600_000,"Cuidado del hogar":9_300_000}
assert sum(LY_LINEA.values()) == LY_H1
LY_MG = 0.232
LY_UB = round(LY_H1*LY_MG); LY_COGS = LY_H1-LY_UB
LY_OPEX = 3_480_000
LY_EBITDA = LY_UB-LY_OPEX
LY_EBIT = LY_EBITDA-430_000
LY_GF = 520_000; LY_DC = -120_000
LY_EBT = LY_EBIT-LY_GF+LY_DC
LY_IR = round(LY_EBT*TASA_IR); LY_NET = LY_EBT-LY_IR

# Puente de ventas ppto -> real (S/): volumen, precio, mix, descuento. Suma = -1.70M.
PVM = [("Ventas ppto",PPTO_H1),("Efecto volumen",-1_100_000),("Efecto precio (+2% lista parcial)",250_000),
 ("Efecto mix canal/linea",-450_000),("Descuento comercial defensivo",-400_000),("Ventas real H1",REAL_H1)]
assert sum(v for _,v in PVM[1:-1]) == REAL_H1-PPTO_H1

# Drill-down cobranza: CxC institucional S/ 2.00M en 8 clientes con aging (S/).
# Ventas diarias institucionales = 5.144M/181 = 28.42k/dia -> DSO institucional 70.4d.
CLIENTES_INST = [
 {"nombre":"Municipalidad de San Juan","corriente":300_000,"b30":150_000,"b60":70_000,"b90":0},
 {"nombre":"Red Salud Norte","corriente":200_000,"b30":120_000,"b60":60_000,"b90":30_000},
 {"nombre":"EduCorp S.A.","corriente":250_000,"b30":80_000,"b60":20_000,"b90":0},
 {"nombre":"Minera Cascajal","corriente":280_000,"b30":0,"b60":0,"b90":0},
 {"nombre":"Agroindustrial del Valle","corriente":100_000,"b30":50_000,"b60":30_000,"b90":0},
 {"nombre":"Constructora VialSur","corriente":40_000,"b30":30_000,"b60":20_000,"b90":30_000},
 {"nombre":"Gobierno Regional","corriente":0,"b30":20_000,"b60":30_000,"b90":40_000},
 {"nombre":"Otros menores","corriente":30_000,"b30":20_000,"b60":0,"b90":0}]
VTA_D_INST = CANAL_REAL_H1["Institucional"]/DIAS_H1
for c in CLIENTES_INST:
    c["total"] = c["corriente"]+c["b30"]+c["b60"]+c["b90"]
    c["dso"] = round(c["total"]/VTA_D_INST,1)
    c["mora60"] = c["b60"]+c["b90"]
TOT_INST = sum(c["total"] for c in CLIENTES_INST)
assert TOT_INST == 2_000_000, TOT_INST
MORA60 = sum(c["mora60"] for c in CLIENTES_INST)  # 330k
CXc_CANAL = {"Mayorista":3_900_000,"Minorista":2_260_000,"Institucional":2_000_000}
assert sum(CXc_CANAL.values()) == BAL_JUN["cxc"]

# Drill-down inventarios: linea Hogar S/ 3.35M en 8 SKUs (stock, costo, venta mensual).
SKUS_HOGAR = [
 {"sku":"HOG-014","nombre":"Detergente industrial 20kg","stock_u":14_000,"costo_u":18.50,"vta_mes_u":3_200},
 {"sku":"HOG-022","nombre":"Jabon liquido 5L","stock_u":22_000,"costo_u":12.80,"vta_mes_u":4_800},
 {"sku":"HOG-031","nombre":"Papel toalla x12","stock_u":30_000,"costo_u":9.40,"vta_mes_u":7_500},
 {"sku":"HOG-007","nombre":"Desinfectante 1L","stock_u":45_000,"costo_u":4.20,"vta_mes_u":12_000},
 {"sku":"HOG-045","nombre":"Escobas premium","stock_u":18_000,"costo_u":6.90,"vta_mes_u":2_100},
 {"sku":"HOG-046","nombre":"Trapeadores","stock_u":25_000,"costo_u":5.60,"vta_mes_u":3_000},
 {"sku":"HOG-052","nombre":"Bolsas basura 100L x50","stock_u":60_000,"costo_u":7.30,"vta_mes_u":9_000}]
for s in SKUS_HOGAR:
    s["valorizado"] = round(s["stock_u"]*s["costo_u"])
    s["cobertura_m"] = round(s["stock_u"]/s["vta_mes_u"],1)
RESTO_HOGAR = 3_350_000-sum(s["valorizado"] for s in SKUS_HOGAR)
SKUS_HOGAR.append({"sku":"HOG-RESTO","nombre":"Resto linea Hogar (agregado)","stock_u":None,
 "costo_u":None,"vta_mes_u":None,"valorizado":RESTO_HOGAR,"cobertura_m":2.1})
assert sum(s["valorizado"] for s in SKUS_HOGAR) == 3_350_000
SOBRESTOCK = sum(s["valorizado"] for s in SKUS_HOGAR if isinstance(s["cobertura_m"],float) and s["cobertura_m"]>6)
INV_LINEA = {"Abarrotes importados":4_100_000,"Cuidado del hogar":3_350_000}
assert sum(INV_LINEA.values()) == BAL_JUN["inv"]

data = {"empresa":EMPRESA,"corte":CORTE,"moneda":MONEDA,"tasa_ir":TASA_IR,
 "meses":MESES,"ppto_m":PPTO_M,"real_m":REAL_M,
 "ppto_h1":PPTO_H1,"real_h1":REAL_H1,"desvio_ventas":REAL_H1-PPTO_H1,
 "ub_ppto":UB_PPTO_H1,"ub_real":UB_REAL_H1,"cogs_ppto":COGS_PPTO_H1,"cogs_real":COGS_REAL_H1,
 "opex_ppto":OPEX_PPTO_H1,"opex_real":OPEX_REAL_H1,
 "ebitda_ppto":EBITDA_PPTO_H1,"ebitda_real":EBITDA_REAL_H1,
 "ebit_ppto":EBIT_PPTO,"ebit_real":EBIT_REAL,"gf_ppto":GF_PPTO,"gf_real":GF_REAL,
 "dc_ppto":DC_PPTO,"dc_real":DC_REAL,"ebt_ppto":EBT_PPTO,"ebt_real":EBT_REAL,
 "ir_ppto":IR_PPTO,"ir_real":IR_REAL,"net_ppto":NET_PPTO,"net_real":NET_REAL,
 "bridge":[{"paso":p,"monto":m} for p,m in BRIDGE],
 "canal_ppto":CANAL_PPTO_H1,"canal_real":CANAL_REAL_H1,
 "linea_ppto":LINEA_PPTO_H1,"linea_real":LINEA_REAL_H1,
 "tc_ppto":TC_PPTO,"tc_real":TC_REAL_PROM_H1,"tc_jun":TC_JUN,
 "bal_dic":BAL_DIC,"bal_jun":BAL_JUN,
 "k_real":{"dso":round(K_REAL["dso"],1),"dio":round(K_REAL["dio"],1),"dpo":round(K_REAL["dpo"],1),"ccc":round(K_REAL["ccc"],1)},
 "k_dic":K_DIC,"fx":FX,"fy":FY,"acciones":ACCIONES,
 "ly_h1":LY_H1,"ly_canal":LY_CANAL,"ly_linea":LY_LINEA,"ly_ub":LY_UB,"ly_cogs":LY_COGS,"ly_opex":LY_OPEX,
 "ly_ebitda":LY_EBITDA,"ly_ebit":LY_EBIT,"ly_gf":LY_GF,"ly_dc":LY_DC,"ly_ebt":LY_EBT,
 "ly_ir":LY_IR,"ly_net":LY_NET,
 "pvm":[{"paso":p,"monto":m} for p,m in PVM],
 "clientes_inst":CLIENTES_INST,"cxc_canal":CXc_CANAL,"mora60":MORA60,
 "skus_hogar":SKUS_HOGAR,"inv_linea":INV_LINEA,"sobrestock":SOBRESTOCK}
(OUT/"data.json").write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding="utf-8")
print("data.json OK")
print(f"Ventas H1 real {REAL_H1/1e6:.2f}M vs ppto {PPTO_H1/1e6:.2f}M ({(REAL_H1/PPTO_H1-1)*100:+.1f}%)")
print(f"EBITDA {EBITDA_REAL_H1/1e6:.2f}M vs {EBITDA_PPTO_H1/1e6:.2f}M, desvio {(EBITDA_REAL_H1-EBITDA_PPTO_H1)/1e3:+.0f}k")
print(f"Neta {NET_REAL/1e6:.2f}M vs {NET_PPTO/1e6:.2f}M")
print(f"K_REAL DSO {K_REAL['dso']:.1f} DIO {K_REAL['dio']:.1f} DPO {K_REAL['dpo']:.1f} CCC {K_REAL['ccc']:.1f}")
print(f"Patrimonio ata: {BAL_JUN['patrimonio']-BAL_DIC['patrimonio']} == neta {NET_REAL}")
