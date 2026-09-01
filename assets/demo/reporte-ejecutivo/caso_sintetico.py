"""
Genera el caso sintético para el demo público de financial-executive-report.

Datos 100% inventados. La estructura de cuentas y el layout de hojas imitan un
juego real de EEFF de una distribuidora peruana, pero ninguna cifra proviene de
una empresa real.

El caso está DISEÑADO para contener hallazgos específicos:
  H1  Margen bruto se comprime: se vende más y se gana menos.
  H2  La utilidad operativa cae fuerte mientras el resultado neto sube.
  H3  El puente entre ambos es la diferencia de cambio, partida no operativa.
  H4  Existencias crecen muy por encima de ventas.
  H5  La cobertura de intereses se deteriora a la mitad.

Y defectos de calidad de datos plantados a propósito, para que la minuta los levante:
  D1  Encabezado de periodo desfasado en la hoja ERF.
  D2  Categoría de gasto nueva en el año 2 (ambigüedad reclasificación vs gasto nuevo).
  D3  Rótulo de columna del balance del año 1 inconsistente con el título de la hoja.
"""

EMPRESA = "NUTRIANDES DISTRIBUCIONES S.A.C."   # verificar en SUNAT que no exista
A1, A2 = 2027, 2028                             # años ficticios, futuros a propósito

# ---------------------------------------------------------------- ESTADO DE RESULTADOS
er = {
    A1: {
        "ventas":            42_000_000,
        "margen_bruto_pct":  0.1850,
        "gastos": {
            "Gastos de Administración": 1_290_000,
            "Gastos de Venta":          1_940_000,
            "Gastos de Producción":       215_000,
            "Gastos de Distribución":     925_000,
        },
        "ingresos_financieros":     85_000,
        "gastos_financieros":      640_000,
        "diferencia_cambio":      -350_000,     # pérdida cambiaria
        "otros_ingresos_gestion":   60_000,
    },
    A2: {
        "ventas":            45_700_000,        # +8.8%
        "margen_bruto_pct":  0.1640,            # -210 pbs  <- H1
        "gastos": {
            "Gastos de Administración":                1_505_000,
            "Gastos de Venta":                         2_060_000,
            "Gastos de Producción":                      248_000,
            "Gastos de Distribución":                  1_180_000,
            "Gastos de Desarrollo de Nuevos Negocios":   395_000,   # <- D2, categoría nueva
        },
        "ingresos_financieros":    105_000,
        "gastos_financieros":      810_000,
        "diferencia_cambio":     1_240_000,     # ganancia cambiaria  <- H3
        "otros_ingresos_gestion":  175_000,
    },
}
TASA_IR = 0.295


def resolver_er(d):
    ventas = d["ventas"]
    ub = round(ventas * d["margen_bruto_pct"], 2)
    cv = round(ventas - ub, 2)
    gastos_total = sum(d["gastos"].values())
    uo = round(ub - gastos_total, 2)
    uai = round(uo + d["ingresos_financieros"] - d["gastos_financieros"]
                + d["diferencia_cambio"] + d["otros_ingresos_gestion"], 2)
    ir = round(uai * TASA_IR, 2)
    return {
        "ventas": ventas, "costo_ventas": cv, "utilidad_bruta": ub,
        "gastos": d["gastos"], "gastos_total": gastos_total, "utilidad_operativa": uo,
        "ingresos_financieros": d["ingresos_financieros"],
        "gastos_financieros": d["gastos_financieros"],
        "diferencia_cambio": d["diferencia_cambio"],
        "otros_ingresos_gestion": d["otros_ingresos_gestion"],
        "uai": uai, "impuesto_renta": ir, "resultado": round(uai - ir, 2),
    }


ER = {a: resolver_er(d) for a, d in er.items()}

# ---------------------------------------------------------------- BALANCE
# El patrimonio se arma para que cierre contra el resultado del ER.
CAPITAL = 3_000_000
RES_ACUM_A1 = 1_650_000
DIVIDENDOS_A2 = 900_000

patrimonio = {
    A1: {"Capital": CAPITAL,
         "Resultados acumulados": RES_ACUM_A1,
         "Resultado del Periodo": ER[A1]["resultado"]},
    A2: {"Capital": CAPITAL,
         "Resultados acumulados": round(RES_ACUM_A1 + ER[A1]["resultado"] - DIVIDENDOS_A2, 2),
         "Resultado del Periodo": ER[A2]["resultado"]},
}
for a in (A1, A2):
    patrimonio[a]["_total"] = round(sum(v for k, v in patrimonio[a].items()
                                        if not k.startswith("_")), 2)

activo = {
    A1: {
        "corriente": {
            "Efectivo y Equivalentes de Efectivo": 1_420_000,
            "Cuentas por Cobrar Comerciales":      5_520_000,
            "Cuentas por cobrar al Personal":         28_000,
            "Cuentas por Cobrar Diversas":           390_000,
            "Existencias":                         4_010_000,
            "Gastos Contratados por Anticipado":      48_000,
            "Otros Activos":                         380_000,
        },
        "no_corriente": {
            "Inversiones Mobiliarias":               420_000,
            "Otras Cuentas por Cobrar Diversas L.P": 2_050_000,
            "Intangibles (neto)":                    195_000,
            "Propiedad Planta y Equipo (Neto)":    6_240_000,
        },
    },
    A2: {
        "corriente": {
            "Efectivo y Equivalentes de Efectivo": 1_180_000,   # baja
            "Cuentas por Cobrar Comerciales":      5_780_000,
            "Cuentas por cobrar al Personal":         19_000,
            "Cuentas por Cobrar Diversas":         1_395_000,
            "Existencias":                         4_995_000,   # +24.6%  <- H4
            "Gastos Contratados por Anticipado":     138_000,
            "Otros Activos":                         720_000,
        },
        "no_corriente": {
            "Inversiones Mobiliarias":               120_000,
            "Otras Cuentas por Cobrar Diversas L.P": 1_250_000,
            "Intangibles (neto)":                    248_000,
            "Propiedad Planta y Equipo (Neto)":    7_410_000,
        },
    },
}

pasivo_corriente = {
    A1: {
        "Cuentas por Pagar Comerciales":               8_640_000,
        "Tributos y Aportes por Pagar":                   95_000,
        "Remuneraciones y Participaciones por Pagar":    348_000,
        "Otras Cuentas por Pagar":                     2_900_000,
    },
    A2: {
        "Cuentas por Pagar Comerciales":               9_780_000,
        "Tributos y Aportes por Pagar":                  735_000,
        "Remuneraciones y Participaciones por Pagar":    432_000,
        "Otras Cuentas por Pagar":                       178_000,
        "Otras Cuentas por Pagar a Corto Plazo":       1_310_000,
    },
}

# El pasivo no corriente es la variable de cierre: fuerza A = P + Pat exacto.
BAL = {}
for a in (A1, A2):
    ac = round(sum(activo[a]["corriente"].values()), 2)
    anc = round(sum(activo[a]["no_corriente"].values()), 2)
    total_activo = round(ac + anc, 2)
    pc = round(sum(pasivo_corriente[a].values()), 2)
    pnc = round(total_activo - pc - patrimonio[a]["_total"], 2)
    BAL[a] = {
        "activo_corriente": activo[a]["corriente"], "total_ac": ac,
        "activo_no_corriente": activo[a]["no_corriente"], "total_anc": anc,
        "total_activo": total_activo,
        "pasivo_corriente": pasivo_corriente[a], "total_pc": pc,
        "pasivo_no_corriente": {"Otras Cuentas por Pagar a Largo Plazo": pnc},
        "total_pnc": pnc,
        "patrimonio": {k: v for k, v in patrimonio[a].items() if not k.startswith("_")},
        "total_patrimonio": patrimonio[a]["_total"],
    }

# ---------------------------------------------------------------- VERIFICACIÓN
def verificar():
    ok = True
    for a in (A1, A2):
        b = BAL[a]
        izq = b["total_activo"]
        der = round(b["total_pc"] + b["total_pnc"] + b["total_patrimonio"], 2)
        eq = abs(izq - der) < 0.01
        tie = abs(b["patrimonio"]["Resultado del Periodo"] - ER[a]["resultado"]) < 0.01
        print(f"[{a}] Activo={izq:>15,.2f}  P+Pat={der:>15,.2f}  ecuacion={'OK' if eq else 'FALLA'}"
              f"  resultado_ER=BG:{'OK' if tie else 'FALLA'}")
        ok = ok and eq and tie
    return ok


def indicadores():
    print("\n%-28s %14s %14s %10s" % ("", A1, A2, "Var"))
    print("-" * 70)
    def fila(n, x, y, pct=True, suf=""):
        if pct and x:
            print("%-28s %14s %14s %9.1f%%" % (n, f"{x:,.0f}", f"{y:,.0f}", 100*(y/x-1)))
        else:
            print("%-28s %14s %14s" % (n, f"{x:,.2f}{suf}", f"{y:,.2f}{suf}"))
    e1, e2 = ER[A1], ER[A2]
    fila("Ventas netas", e1["ventas"], e2["ventas"])
    fila("Utilidad bruta", e1["utilidad_bruta"], e2["utilidad_bruta"])
    fila("Gastos operativos", e1["gastos_total"], e2["gastos_total"])
    fila("Utilidad operativa", e1["utilidad_operativa"], e2["utilidad_operativa"])
    fila("Diferencia de cambio", e1["diferencia_cambio"], e2["diferencia_cambio"], pct=False)
    fila("Resultado del ejercicio", e1["resultado"], e2["resultado"])
    print()
    for n, f_ in [("Margen bruto", lambda e: 100*e["utilidad_bruta"]/e["ventas"]),
                  ("Margen operativo", lambda e: 100*e["utilidad_operativa"]/e["ventas"]),
                  ("Margen neto", lambda e: 100*e["resultado"]/e["ventas"])]:
        a, b = f_(e1), f_(e2)
        print("%-28s %13.2f%% %13.2f%%  %+.0f pbs" % (n, a, b, 100*(b-a)))
    b1, b2 = BAL[A1], BAL[A2]
    rc1, rc2 = b1["total_ac"]/b1["total_pc"], b2["total_ac"]/b2["total_pc"]
    en1 = 100*(b1["total_pc"]+b1["total_pnc"])/b1["total_activo"]
    en2 = 100*(b2["total_pc"]+b2["total_pnc"])/b2["total_activo"]
    print("%-28s %14.3f %14.3f" % ("Ratio corriente", rc1, rc2))
    print("%-28s %13.1f%% %13.1f%%" % ("Endeudamiento", en1, en2))
    print("%-28s %13.1f%% %13.1f%%" % ("ROE", 100*e1["resultado"]/b1["total_patrimonio"],
                                              100*e2["resultado"]/b2["total_patrimonio"]))
    print("%-28s %14.2f %14.2f" % ("Cobertura de intereses",
          e1["utilidad_operativa"]/e1["gastos_financieros"],
          e2["utilidad_operativa"]/e2["gastos_financieros"]))
    di1 = 365*b1["activo_corriente"]["Existencias"]/e1["costo_ventas"]
    di2 = 365*b2["activo_corriente"]["Existencias"]/e2["costo_ventas"]
    dc1 = 365*b1["activo_corriente"]["Cuentas por Cobrar Comerciales"]/e1["ventas"]
    dc2 = 365*b2["activo_corriente"]["Cuentas por Cobrar Comerciales"]/e2["ventas"]
    dp1 = 365*b1["pasivo_corriente"]["Cuentas por Pagar Comerciales"]/e1["costo_ventas"]
    dp2 = 365*b2["pasivo_corriente"]["Cuentas por Pagar Comerciales"]/e2["costo_ventas"]
    print("%-28s %14.0f %14.0f" % ("Dias de inventario", di1, di2))
    print("%-28s %14.0f %14.0f" % ("Dias de cobro", dc1, dc2))
    print("%-28s %14.0f %14.0f" % ("Dias de pago", dp1, dp2))
    print("%-28s %14.0f %14.0f" % ("Ciclo de conversion", di1+dc1-dp1, di2+dc2-dp2))
    print("\nExistencias %+.1f%%  vs  ventas %+.1f%%" % (
        100*(b2["activo_corriente"]["Existencias"]/b1["activo_corriente"]["Existencias"]-1),
        100*(e2["ventas"]/e1["ventas"]-1)))


if __name__ == "__main__":
    assert verificar(), "Las invariantes contables no se cumplen"
    indicadores()
