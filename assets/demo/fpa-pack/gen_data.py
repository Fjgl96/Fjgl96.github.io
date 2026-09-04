"""Caso sintetico FP&A Monthly Pack V5 — Comercial Los Alamos S.A.C.
Distribuidora de materiales de construccion, 40% de compras en USD.
100% inventado. Ninguna cifra corresponde a empresa real.
"""
import json
import pathlib

OUT = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
OUT.mkdir(parents=True, exist_ok=True)

EMPRESA = "Comercial Los Alamos S.A.C."
CORTE = "Junio 2026 (H1)"
MONEDA = "PEN (soles)"
TASA_IR = 0.295
DIAS_H1 = 181

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
CANALES = ["Ferretero", "Constructor", "Retail"]
LINEAS = ["Materiales base", "Acabados"]

PPTO_M = [1_800_000, 1_750_000, 2_000_000, 2_000_000, 2_100_000, 2_350_000,
          2_050_000, 2_000_000, 1_950_000, 2_050_000, 2_000_000, 1_950_000]
REAL_M = [1_760_000, 1_680_000, 1_900_000, 1_880_000, 1_950_000, 2_130_000,
          None, None, None, None, None, None]
CANAL_PPTO_H1 = {"Ferretero": 5_400_000, "Constructor": 4_200_000, "Retail": 2_400_000}
CANAL_REAL_H1 = {"Ferretero": 5_130_000, "Constructor": 3_840_000, "Retail": 2_330_000}
CANAL_LY_H1 = {"Ferretero": 5_000_000, "Constructor": 3_600_000, "Retail": 2_100_000}
LINEA_PPTO_H1 = {"Materiales base": 7_800_000, "Acabados": 4_200_000}
LINEA_REAL_H1 = {"Materiales base": 7_450_000, "Acabados": 3_850_000}
LINEA_LY_H1 = {"Materiales base": 7_100_000, "Acabados": 3_600_000}
TC_PPTO = 3.72
TC_REAL_PROM_H1 = 3.81
TC_JUN = 3.84
PCT_USD = 0.40

PPTO_H1 = sum(PPTO_M[:6]); REAL_H1 = sum(x for x in REAL_M[:6] if x)
FY_PPTO = sum(PPTO_M)
LY_H1 = sum(CANAL_LY_H1.values())
assert PPTO_H1 == 12_000_000 and REAL_H1 == 11_300_000
assert FY_PPTO == 24_000_000 and LY_H1 == 10_700_000
assert sum(CANAL_PPTO_H1.values()) == PPTO_H1
assert sum(CANAL_REAL_H1.values()) == REAL_H1
assert sum(LINEA_PPTO_H1.values()) == PPTO_H1
assert sum(LINEA_REAL_H1.values()) == REAL_H1
assert sum(LINEA_LY_H1.values()) == LY_H1

MG_PPTO, MG_REAL, MG_LY = 0.260, 0.242, 0.251
UB_PPTO_H1 = round(PPTO_H1 * MG_PPTO); UB_REAL_H1 = round(REAL_H1 * MG_REAL)
LY_UB = round(LY_H1 * MG_LY)
COGS_PPTO_H1 = PPTO_H1 - UB_PPTO_H1
COGS_REAL_H1 = REAL_H1 - UB_REAL_H1
LY_COGS = LY_H1 - LY_UB
OPEX_PPTO_H1, OPEX_REAL_H1, LY_OPEX = 1_680_000, 1_684_600, 1_450_000
EBITDA_PPTO_H1 = UB_PPTO_H1 - OPEX_PPTO_H1
EBITDA_REAL_H1 = UB_REAL_H1 - OPEX_REAL_H1
LY_EBITDA = LY_UB - LY_OPEX
DEP_H1, DEP_LY = 180_000, 170_000
EBIT_PPTO, EBIT_REAL = EBITDA_PPTO_H1 - DEP_H1, EBITDA_REAL_H1 - DEP_H1
LY_EBIT = LY_EBITDA - DEP_LY
GF_PPTO, GF_REAL, LY_GF = 220_000, 275_000, 210_000
DC_PPTO, DC_REAL, LY_DC = -40_000, -110_000, -50_000
EBT_PPTO = EBIT_PPTO - GF_PPTO + DC_PPTO
EBT_REAL = EBIT_REAL - GF_REAL + DC_REAL
LY_EBT = LY_EBIT - LY_GF + LY_DC
IR_PPTO, IR_REAL = round(EBT_PPTO * TASA_IR), round(EBT_REAL * TASA_IR)
LY_IR = round(LY_EBT * TASA_IR)
NET_PPTO, NET_REAL = EBT_PPTO - IR_PPTO, EBT_REAL - IR_REAL
LY_NET = LY_EBT - LY_IR
assert (PPTO_H1, UB_PPTO_H1, EBITDA_PPTO_H1, EBT_PPTO, NET_PPTO) == (12_000_000, 3_120_000, 1_440_000, 1_000_000, 705_000)
assert (REAL_H1, UB_REAL_H1, EBITDA_REAL_H1, EBT_REAL, NET_REAL) == (11_300_000, 2_734_600, 1_050_000, 485_000, 341_925)
assert (LY_H1, LY_UB, LY_EBITDA, LY_EBT, LY_NET) == (10_700_000, 2_685_700, 1_235_700, 805_700, 568_018)

# Puente de ventas ppto -> real: volumen, precio, mix, descuento.
PVM = [("Ventas ppto", PPTO_H1), ("Efecto volumen", -450_000),
       ("Efecto precio (+2% lista parcial)", 110_000),
       ("Efecto mix canal/linea", -180_000),
       ("Descuento comercial defensivo", -180_000),
       ("Ventas real H1", REAL_H1)]
assert sum(v for _, v in PVM[1:-1]) == REAL_H1 - PPTO_H1

# Bridge EBITDA reconciliado con el PVM a margen estandar 26%.
BRIDGE = [
 ("EBITDA ppto", EBITDA_PPTO_H1),
 ("Efecto volumen (margen std 26%)", round(-450_000 * MG_PPTO)),
 ("Efecto precio / mix / descuento", round(-250_000 * MG_PPTO)),
 ("Costo FX (TC 3.72->3.81)", -120_000),
 ("Otros costos", -83_400),
 ("Opex neto", -(OPEX_REAL_H1 - OPEX_PPTO_H1)),
 ("EBITDA real H1", EBITDA_REAL_H1),
]
assert sum(v for _, v in BRIDGE[1:-1]) == EBITDA_REAL_H1 - EBITDA_PPTO_H1

# Balance dic-25 vs jun-26 (patrimonio derivado: ata con la neta).
BAL_DIC = {"caja": 480_000, "cxc": 2_720_000, "inv": 2_660_000, "otros_ac": 160_000,
           "af_neto": 3_380_000, "cxp": 1_800_000, "deuda_cp": 1_520_000,
           "otros_pc": 400_000, "deuda_lp": 1_990_000, "patrimonio": 3_690_000}
JUN = {"caja": 380_000, "cxc": 3_246_400, "inv": None, "otros_ac": 160_000,
       "af_neto": 3_370_000, "cxp": 1_651_700, "otros_pc": 440_000, "deuda_lp": 1_560_000}
JUN["patrimonio"] = BAL_DIC["patrimonio"] + NET_REAL

def kpis(b, ventas_h1, cogs_h1):
    v_d = ventas_h1 / DIAS_H1
    c_d = cogs_h1 / DIAS_H1
    compras = cogs_h1 + (b["inv"] - BAL_DIC["inv"])
    comp_d = compras / DIAS_H1
    dso = b["cxc"] / v_d
    dio = b["inv"] / c_d
    dpo = b["cxp"] / comp_d
    return {"dso": dso, "dio": dio, "dpo": dpo, "ccc": dso + dio - dpo}

SKUS_HOGAR = [
 {"sku": "CER-101", "nombre": "Porcelanato 60x60 caja", "stock_u": 2_100, "costo_u": 68.00, "vta_mes_u": 475},
 {"sku": "PIN-020", "nombre": "Pintura latex 20L", "stock_u": 1_900, "costo_u": 92.50, "vta_mes_u": 390},
 {"sku": "PEG-025", "nombre": "Pegamento ceramico 25kg", "stock_u": 4_500, "costo_u": 24.80, "vta_mes_u": 1_100},
 {"sku": "LAC-011", "nombre": "Laca selladora 1L", "stock_u": 3_250, "costo_u": 18.90, "vta_mes_u": 850},
 {"sku": "PER-008", "nombre": "Perfiles aluminio 6m", "stock_u": 1_200, "costo_u": 45.00, "vta_mes_u": 140},
 {"sku": "SAN-031", "nombre": "Griferia cocina", "stock_u": 950, "costo_u": 62.00, "vta_mes_u": 115},
 {"sku": "ILU-044", "nombre": "Focos LED 12W caja x24", "stock_u": 2_500, "costo_u": 38.40, "vta_mes_u": 360}]
for s in SKUS_HOGAR:
    # Exacto en centimos (nada de float): costo con 2 decimales.
    s["valorizado"] = s["stock_u"] * int(round(s["costo_u"] * 100)) // 100
    s["cobertura_m"] = round(s["stock_u"] / s["vta_mes_u"], 1)
RESTO_HOGAR = 68_642 * 10.00  # fila agregada honesta ("varios"): entera y exacta
SKUS_HOGAR.append({"sku": "ACA-VAR", "nombre": "Varios Acabados (agregado)", "stock_u": 68_642,
                   "costo_u": 10.00, "vta_mes_u": 32_687, "valorizado": int(RESTO_HOGAR),
                   "cobertura_m": round(68_642 / 32_687, 1)})
INV_LINEA = {"Materiales base": 1_500_000,
             "Acabados": sum(s["valorizado"] for s in SKUS_HOGAR)}
assert SKUS_HOGAR[-1]["cobertura_m"] == 2.1
SOBRESTOCK = sum(s["valorizado"] for s in SKUS_HOGAR
                 if isinstance(s["cobertura_m"], float) and s["cobertura_m"] > 6)
assert SOBRESTOCK == 208_900
# Cierre del balance: inv y deuda CP por despeje (nunca a mano).
JUN["inv"] = sum(INV_LINEA.values())
ac = JUN["caja"] + JUN["cxc"] + JUN["inv"] + JUN["otros_ac"]
tot_jun = ac + JUN["af_neto"]
JUN["deuda_cp"] = (tot_jun - JUN["cxp"] - JUN["otros_pc"] - JUN["deuda_lp"] - JUN["patrimonio"])
BAL_JUN = JUN
assert BAL_JUN["patrimonio"] - BAL_DIC["patrimonio"] == NET_REAL
tot = ac + BAL_JUN["af_neto"]
pas = BAL_JUN["cxp"] + BAL_JUN["deuda_cp"] + BAL_JUN["otros_pc"] + BAL_JUN["deuda_lp"] + BAL_JUN["patrimonio"]
assert tot == pas and BAL_JUN["deuda_cp"] > 0, (tot, pas)

K_REAL = kpis(BAL_JUN, REAL_H1, COGS_REAL_H1)
K_DIC = {"dso": 46.1, "dio": 59.8, "dpo": 38.5, "ccc": 67.4}
assert round(K_REAL["dso"], 1) == 52.0 and round(K_REAL["dio"], 1) == 61.0
assert round(K_REAL["dpo"], 1) == 34.0 and round(K_REAL["ccc"], 1) == 79.0

ac_d = BAL_DIC["caja"] + BAL_DIC["cxc"] + BAL_DIC["inv"] + BAL_DIC["otros_ac"]
assert ac_d + BAL_DIC["af_neto"] == 9_400_000
assert (BAL_DIC["cxp"] + BAL_DIC["deuda_cp"] + BAL_DIC["otros_pc"] + BAL_DIC["deuda_lp"] + BAL_DIC["patrimonio"]) == 9_400_000




# FX y forecast
FX = {"exposicion_usd": 180_000, "cxp_usd": 220_000, "caja_usd": 40_000,
      "sens_10cts": 18_000, "pct_neta": round(18_000 / NET_REAL * 100, 1)}
FY = {"ventas_base": 23_100_000, "ebitda_base": 2_250_000, "neta_base": 720_000,
      "ventas_ppto": 24_000_000, "ebitda_ppto": 2_880_000, "neta_ppto": 1_410_000,
      "pico_deuda_oct": 4_500_000, "linea_adicional": 1_000_000}
ACCIONES = [
 {"id": "A1", "nombre": "Cobranza constructor + pronto pago", "efecto_caja": 375_000,
  "efecto_py": "- S/ 25k descuento financiero", "kpi": "DSO 52 -> 46 dias"},
 {"id": "A2", "nombre": "Ajuste lista de precios 2H (+2%)", "efecto_caja": 220_000,
  "efecto_py": "+ S/ 220k margen", "kpi": "Margen bruto +80 pbs en 2H"},
 {"id": "A3", "nombre": "Recorte compra acabados -15%", "efecto_caja": 280_000,
  "efecto_py": "neutro", "kpi": "DIO 61 -> 55 dias"},
 {"id": "A4", "nombre": "Forward 50% exposicion 90 dias", "efecto_caja": 0,
  "efecto_py": "acota riesgo 18k -> 9k por 10 cts", "kpi": "Exposicion neta USD 180k -> 90k"},
 {"id": "A5", "nombre": "Linea revolvente +S/ 1.0M", "efecto_caja": 1_000_000,
  "efecto_py": "- S/ 35k intereses 2H", "kpi": "Cubre pico de octubre"}]
DEUDA_H2 = [4_100_000, 4_300_000, 4_400_000, 4_500_000, 4_200_000, 4_000_000]
assert max(DEUDA_H2) == 4_500_000

# Flujo H1 indirecto: ata caja dic->jun.
FLUJO = {"neta": NET_REAL, "dep": DEP_H1,
         "d_cxc": -(BAL_JUN["cxc"] - BAL_DIC["cxc"]),
         "d_inv": -(BAL_JUN["inv"] - BAL_DIC["inv"]),
         "d_cxp_com": BAL_JUN["cxp"] - BAL_DIC["cxp"],
         "d_otros_pc": BAL_JUN["otros_pc"] - BAL_DIC["otros_pc"]}
FLUJO["fco"] = (FLUJO["neta"] + FLUJO["dep"] + FLUJO["d_cxc"] + FLUJO["d_inv"]
                + FLUJO["d_cxp_com"] + FLUJO["d_otros_pc"])
FLUJO["capex"] = -((BAL_JUN["af_neto"] - BAL_DIC["af_neto"]) + DEP_H1)
FLUJO["d_deuda_cp"] = BAL_JUN["deuda_cp"] - BAL_DIC["deuda_cp"]
FLUJO["d_deuda_lp"] = BAL_JUN["deuda_lp"] - BAL_DIC["deuda_lp"]
FLUJO["d_caja"] = FLUJO["fco"] + FLUJO["capex"] + FLUJO["d_deuda_cp"] + FLUJO["d_deuda_lp"]
assert FLUJO["fco"] == -339_670 and FLUJO["capex"] == -170_000
assert FLUJO["d_caja"] == BAL_JUN["caja"] - BAL_DIC["caja"] == -100_000

SUPUESTOS = {"ly_h2_ebitda": 1_350_000, "ly_h2_ebit": 980_000,
             "ly_intereses_ltm": 514_000, "dso_ppto": 45.0,
             "nota": "H2-2025 supuesto; LTM = H2-2025 + H1-2026"}
SUPUESTOS["ebitda_ltm"] = SUPUESTOS["ly_h2_ebitda"] + EBITDA_REAL_H1
SUPUESTOS["deuda_total_jun"] = BAL_JUN["deuda_cp"] + BAL_JUN["deuda_lp"]
SUPUESTOS["deuda_ebitda"] = round(SUPUESTOS["deuda_total_jun"] / SUPUESTOS["ebitda_ltm"], 2)
SUPUESTOS["cobertura"] = round((SUPUESTOS["ly_h2_ebit"] + EBIT_REAL) / SUPUESTOS["ly_intereses_ltm"], 1)
assert SUPUESTOS["ebitda_ltm"] == 2_400_000 and SUPUESTOS["deuda_ebitda"] == 1.63
assert SUPUESTOS["cobertura"] == 3.6

# Drill-down cobranza: CxC Constructor S/ 800k en 8 clientes.
CLIENTES_INST = [
 {"nombre": "Municipalidad de San Juan", "corriente": 120_000, "b30": 60_000, "b60": 28_000, "b90": 0},
 {"nombre": "Red Salud Norte", "corriente": 80_000, "b30": 48_000, "b60": 24_000, "b90": 12_000},
 {"nombre": "EduCorp S.A.", "corriente": 100_000, "b30": 32_000, "b60": 8_000, "b90": 0},
 {"nombre": "Minera Cascajal", "corriente": 112_000, "b30": 0, "b60": 0, "b90": 0},
 {"nombre": "Agroindustrial del Valle", "corriente": 40_000, "b30": 20_000, "b60": 12_000, "b90": 0},
 {"nombre": "Constructora VialSur", "corriente": 16_000, "b30": 12_000, "b60": 8_000, "b90": 12_000},
 {"nombre": "Gobierno Regional", "corriente": 0, "b30": 8_000, "b60": 12_000, "b90": 16_000},
 {"nombre": "Otros menores", "corriente": 12_000, "b30": 8_000, "b60": 0, "b90": 0}]
VTA_D_CONST = CANAL_REAL_H1["Constructor"] / DIAS_H1
for c in CLIENTES_INST:
    c["total"] = c["corriente"] + c["b30"] + c["b60"] + c["b90"]
    c["dso"] = round(c["total"] / VTA_D_CONST, 1)
    c["mora60"] = c["b60"] + c["b90"]
TOT_CONST = sum(c["total"] for c in CLIENTES_INST)
assert TOT_CONST == 800_000, TOT_CONST
MORA60 = sum(c["mora60"] for c in CLIENTES_INST)
assert MORA60 == 132_000
CXc_CANAL = {"Ferretero": 1_566_400, "Constructor": 800_000, "Retail": 880_000}
assert sum(CXc_CANAL.values()) == BAL_JUN["cxc"]

# Drill-down inventarios: linea Acabados S/ 1.3869M.

data = {"empresa": EMPRESA, "corte": CORTE, "moneda": MONEDA, "tasa_ir": TASA_IR,
 "meses": MESES, "ppto_m": PPTO_M, "real_m": REAL_M,
 "ppto_h1": PPTO_H1, "real_h1": REAL_H1, "desvio_ventas": REAL_H1 - PPTO_H1,
 "ub_ppto": UB_PPTO_H1, "ub_real": UB_REAL_H1, "cogs_ppto": COGS_PPTO_H1, "cogs_real": COGS_REAL_H1,
 "opex_ppto": OPEX_PPTO_H1, "opex_real": OPEX_REAL_H1,
 "ebitda_ppto": EBITDA_PPTO_H1, "ebitda_real": EBITDA_REAL_H1,
 "ebit_ppto": EBIT_PPTO, "ebit_real": EBIT_REAL, "gf_ppto": GF_PPTO, "gf_real": GF_REAL,
 "dc_ppto": DC_PPTO, "dc_real": DC_REAL, "ebt_ppto": EBT_PPTO, "ebt_real": EBT_REAL,
 "ir_ppto": IR_PPTO, "ir_real": IR_REAL, "net_ppto": NET_PPTO, "net_real": NET_REAL,
 "ly_h1": LY_H1, "ly_canal": CANAL_LY_H1, "ly_linea": LINEA_LY_H1,
 "ly_ub": LY_UB, "ly_cogs": LY_COGS, "ly_opex": LY_OPEX,
 "ly_ebitda": LY_EBITDA, "ly_ebit": LY_EBIT, "ly_gf": LY_GF, "ly_dc": LY_DC,
 "ly_ebt": LY_EBT, "ly_ir": LY_IR, "ly_net": LY_NET,
 "bridge": [{"paso": p, "monto": m} for p, m in BRIDGE],
 "pvm": [{"paso": p, "monto": m} for p, m in PVM],
 "canal_ppto": CANAL_PPTO_H1, "canal_real": CANAL_REAL_H1,
 "linea_ppto": LINEA_PPTO_H1, "linea_real": LINEA_REAL_H1,
 "tc_ppto": TC_PPTO, "tc_real": TC_REAL_PROM_H1, "tc_jun": TC_JUN, "pct_usd": PCT_USD,
 "bal_dic": BAL_DIC, "bal_jun": BAL_JUN,
 "k_real": {"dso": round(K_REAL["dso"], 1), "dio": round(K_REAL["dio"], 1),
            "dpo": round(K_REAL["dpo"], 1), "ccc": round(K_REAL["ccc"], 1)},
 "k_dic": K_DIC, "fx": FX, "fy": FY, "acciones": ACCIONES, "deuda_h2": DEUDA_H2,
 "flujo": FLUJO, "supuestos": SUPUESTOS,
 "clientes_inst": CLIENTES_INST, "cxc_canal": CXc_CANAL, "mora60": MORA60,
 "skus_hogar": SKUS_HOGAR, "inv_linea": INV_LINEA, "sobrestock": SOBRESTOCK}
(OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("data.json OK")
print(f"Ventas H1 real {REAL_H1/1e6:.2f}M vs ppto {PPTO_H1/1e6:.2f}M ({(REAL_H1/PPTO_H1-1)*100:+.1f}%)")
print(f"EBITDA {EBITDA_REAL_H1/1e6:.2f}M vs {EBITDA_PPTO_H1/1e6:.2f}M, desvio {(EBITDA_REAL_H1-EBITDA_PPTO_H1)/1e3:+.0f}k")
print(f"Neta {NET_REAL/1e6:.2f}M vs {NET_PPTO/1e6:.2f}M")
print(f"K_REAL DSO {K_REAL['dso']:.1f} DIO {K_REAL['dio']:.1f} DPO {K_REAL['dpo']:.1f} CCC {K_REAL['ccc']:.1f}")
print(f"Flujo d_caja {FLUJO['d_caja']} | LTM {SUPUESTOS['ebitda_ltm']} D/E {SUPUESTOS['deuda_ebitda']}")
