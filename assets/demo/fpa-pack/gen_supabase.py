"""Genera supabase/fpa_schema.sql: DDL + RLS + vistas + seed del FP&A Monthly Pack.

El seed sale de data.json (fuente canonica). Idempotente: todo con
CREATE TABLE IF NOT EXISTS + INSERT ... ON CONFLICT DO NOTHING.

Convencion de la casa (panel-minero/supabase/migracion.sql):
pegar completo en Supabase > SQL Editor y ejecutar.
"""
import json
import pathlib

BASE = pathlib.Path(r"C:\Users\FGUERR~1\AppData\Local\Temp\opencode\fpa-pack")
d = json.loads((BASE / "data.json").read_text(encoding="utf-8"))

MESES = d["meses"][:6]
CANALES = ["Mayorista", "Minorista", "Institucional"]
LINEAS = ["Abarrotes importados", "Cuidado del hogar"]
TRAMOS = ["Corriente", "31-60", "61-90", "90+"]

# ---------- hecho ventas: mes x canal x linea x version (soles enteros) ----------
# REAL y PPTO: totales mensuales conocidos; LY: se distribuye con la
# estacionalidad del ppto (supuesto declarado en el DICC del Excel).
cells = []  # (mes, canal, linea, version, monto)
for version, mes_tot, c_tot, l_tot in [
    ("REAL", d["real_m"][:6], d["canal_real"], d["linea_real"]),
    ("PPTO", d["ppto_m"][:6], d["canal_ppto"], d["linea_ppto"])]:
    h1 = sum(mes_tot)
    csh = {c: c_tot[c] / h1 for c in CANALES}
    lsh = {l: l_tot[l] / h1 for l in LINEAS}
    for mi, mt in enumerate(mes_tot, start=1):
        grp = []
        for c in CANALES:
            for l in LINEAS:
                grp.append((mi, c, l, version, round(mt * csh[c] * lsh[l])))
        drift = mt - sum(x[4] for x in grp)
        mi_, c_, l_, v_, m_ = grp[-1]
        grp[-1] = (mi_, c_, l_, v_, m_ + drift)
        assert sum(x[4] for x in grp) == mt
        cells.extend(grp)
    # ajuste fino: los H1 por canal atan exacto al canonico (el redondeo
    # mensual deriva +-soles). Se absorbe en jun/Hogar sin mover el mes:
    # la suma de derivas por canal es 0 porque los meses atan.
    for c in CANALES:
        dc = c_tot[c] - sum(m for (mi, cc, ll, vv, m) in cells if vv == version and cc == c)
        assert abs(dc) < 50, (version, c, dc)
        for i, (mi, cc, ll, vv, m) in enumerate(cells):
            if vv == version and mi == 6 and cc == c and ll == "Cuidado del hogar":
                cells[i] = (mi, cc, ll, vv, m + dc)
                break
    for c in CANALES:
        assert sum(m for (mi, cc, ll, vv, m) in cells if vv == version and cc == c) == c_tot[c]
# LY por canal con pesos mensuales del ppto
wp = [v / sum(d["ppto_m"][:6]) for v in d["ppto_m"][:6]]
lsh_ly = {l: d["ly_linea"][l] / d["ly_h1"] for l in LINEAS}
for c in CANALES:
    monthly = [round(d["ly_canal"][c] * w) for w in wp]
    monthly[-1] += d["ly_canal"][c] - sum(monthly)
    assert sum(monthly) == d["ly_canal"][c]
    for mi, mt in enumerate(monthly, start=1):
        grp = [(mi, c, l, "LY", round(mt * lsh_ly[l])) for l in LINEAS]
        drift = mt - sum(x[4] for x in grp)
        mi_, c_, l_, v_, m_ = grp[-1]
        grp[-1] = (mi_, c_, l_, v_, m_ + drift)
        cells.extend(grp)

# verificaciones del seed
for version, h1 in [("REAL", d["real_h1"]), ("PPTO", d["ppto_h1"]), ("LY", d["ly_h1"])]:
    tot = sum(m for (_, _, _, v, m) in cells if v == version)
    assert tot == h1, (version, tot, h1)
print(f"ventas: {len(cells)} filas, H1 atan (REAL/PPTO/LY)")

# ---------- pyg / balance ----------
PYG = [  # (periodo, cuenta, monto, orden)
    ("H1-2025", "Ventas netas", d["ly_h1"], 1), ("H1-2025", "Costo de ventas", d["ly_cogs"], 2),
    ("H1-2025", "Utilidad bruta", d["ly_ub"], 3), ("H1-2025", "Gastos operativos", d["ly_opex"], 4),
    ("H1-2025", "EBITDA", d["ly_ebitda"], 5), ("H1-2025", "Depreciación", 430000, 6),
    ("H1-2025", "EBIT", d["ly_ebit"], 7), ("H1-2025", "Gastos financieros", d["ly_gf"], 8),
    ("H1-2025", "Diferencia de cambio", d["ly_dc"], 9), ("H1-2025", "EBT", d["ly_ebt"], 10),
    ("H1-2025", "Impuesto a la renta 29.5%", d["ly_ir"], 11), ("H1-2025", "Utilidad neta", d["ly_net"], 12),
    ("H1-2026-PPTO", "Ventas netas", d["ppto_h1"], 1), ("H1-2026-PPTO", "Costo de ventas", d["cogs_ppto"], 2),
    ("H1-2026-PPTO", "Utilidad bruta", d["ub_ppto"], 3), ("H1-2026-PPTO", "Gastos operativos", d["opex_ppto"], 4),
    ("H1-2026-PPTO", "EBITDA", d["ebitda_ppto"], 5), ("H1-2026-PPTO", "Depreciación", 450000, 6),
    ("H1-2026-PPTO", "EBIT", d["ebit_ppto"], 7), ("H1-2026-PPTO", "Gastos financieros", d["gf_ppto"], 8),
    ("H1-2026-PPTO", "Diferencia de cambio", d["dc_ppto"], 9), ("H1-2026-PPTO", "EBT", d["ebt_ppto"], 10),
    ("H1-2026-PPTO", "Impuesto a la renta 29.5%", d["ir_ppto"], 11), ("H1-2026-PPTO", "Utilidad neta", d["net_ppto"], 12),
    ("H1-2026-REAL", "Ventas netas", d["real_h1"], 1), ("H1-2026-REAL", "Costo de ventas", d["cogs_real"], 2),
    ("H1-2026-REAL", "Utilidad bruta", d["ub_real"], 3), ("H1-2026-REAL", "Gastos operativos", d["opex_real"], 4),
    ("H1-2026-REAL", "EBITDA", d["ebitda_real"], 5), ("H1-2026-REAL", "Depreciación", 450000, 6),
    ("H1-2026-REAL", "EBIT", d["ebit_real"], 7), ("H1-2026-REAL", "Gastos financieros", d["gf_real"], 8),
    ("H1-2026-REAL", "Diferencia de cambio", d["dc_real"], 9), ("H1-2026-REAL", "EBT", d["ebt_real"], 10),
    ("H1-2026-REAL", "Impuesto a la renta 29.5%", d["ir_real"], 11), ("H1-2026-REAL", "Utilidad neta", d["net_real"], 12),
    ("FY-2026-PPTO", "Ventas netas", d["fy"]["ventas_ppto"], 1), ("FY-2026-PPTO", "EBITDA", d["fy"]["ebitda_ppto"], 5),
    ("FY-2026-PPTO", "Utilidad neta", d["fy"]["neta_ppto"], 12),
    ("FY-2026-BASE", "Ventas netas", d["fy"]["ventas_base"], 1), ("FY-2026-BASE", "EBITDA", d["fy"]["ebitda_base"], 5),
    ("FY-2026-BASE", "Utilidad neta", d["fy"]["neta_base"], 12)]

BAL = []  # (corte, grupo, cuenta, monto, orden)
for corte, b in [("2025-12", d["bal_dic"]), ("2026-06", d["bal_jun"])]:
    BAL += [(corte, "ACTIVO", "Caja", b["caja"], 1),
            (corte, "ACTIVO", "Cuentas por cobrar", b["cxc"], 2),
            (corte, "ACTIVO", "Inventarios", b["inv"], 3),
            (corte, "ACTIVO", "Otros AC", b["otros_ac"], 4),
            (corte, "ACTIVO", "Activo fijo neto", b["af_neto"], 5),
            (corte, "PASIVO", "Cuentas por pagar", b["cxp"], 6),
            (corte, "PASIVO", "Deuda CP", b["deuda_cp"], 7),
            (corte, "PASIVO", "Otros pasivos CP", b["otros_pc"], 8),
            (corte, "PASIVO", "Deuda LP", b["deuda_lp"], 9),
            (corte, "PATRIMONIO", "Patrimonio", b["patrimonio"], 10)]

AGING = []  # (cliente, tramo, monto)
key = {"Corriente": "corriente", "31-60": "b30", "61-90": "b60", "90+": "b90"}
for c in d["clientes_inst"]:
    for t in TRAMOS:
        AGING.append((c["nombre"], t, c[key[t]]))

SKUS = [(s["sku"], s["nombre"], s["stock_u"], s["costo_u"], s["vta_mes_u"])
        for s in d["skus_hogar"]]

ACCIONES = [(a["id"], a["nombre"], a["efecto_caja"], a["efecto_py"], a["kpi"])
            for a in d["acciones"]]

PUENTES = ([("PVM", b["paso"], b["monto"], i) for i, b in enumerate(d["pvm"])] +
           [("EBITDA", b["paso"], b["monto"], i) for i, b in enumerate(d["bridge"])])

PARAMS = [("tc_ppto", d["tc_ppto"], "Tipo de cambio presupuesto 2026"),
          ("tc_real_h1", d["tc_real"], "TC promedio real H1"),
          ("tc_jun", d["tc_jun"], "TC cierre junio"),
          ("tasa_ir", d["tasa_ir"], "Impuesto a la renta"),
          ("dias_h1", 181, "Dias del semestre"),
          ("pct_compras_usd", 0.70, "Compras en USD"),
          ("exposicion_usd", d["fx"]["exposicion_usd"], "Exposicion neta pasiva USD"),
          ("pico_deuda_oct", d["fy"]["pico_deuda_oct"], "Pico de deuda octubre (base)"),
          ("linea_adicional", d["fy"]["linea_adicional"], "Linea revolvente propuesta")]

CXC_CANAL = [(c, m) for c, m in d["cxc_canal"].items()]
INV_LINEA = [(l, m) for l, m in d["inv_linea"].items()]

# ---------- SQL ----------
def lit(v):
    if v is None:
        return "null"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    return str(v)

L = []
A = L.append
A("-- ============================================================")
A("-- FP&A MONTHLY PACK — esquema estrella sintético (Supabase)")
A("-- Caso 100% inventado. Pegar completo en SQL Editor y ejecutar.")
A("-- Idempotente: re-ejecutable sin duplicar (ON CONFLICT DO NOTHING).")
A("-- Tablas fpa_*: conviven con panel-minero / vigilante / registro.")
A("-- Supuesto declarado: LY mensual reparte cada canal con la")
A("-- estacionalidad del ppto (ver DICC del Excel).")
A("-- ============================================================")
A("")
A("drop view if exists v_fpa_ventas_canal cascade;")
A("drop view if exists v_fpa_ventas_mes cascade;")
A("drop view if exists v_fpa_ventas_linea cascade;")
A("drop view if exists v_fpa_aging_cliente cascade;")
A("drop view if exists v_fpa_sku cascade;")
A("")
A("create table if not exists fpa_ventas (")
A("  mes     int not null check (mes between 1 and 6),")
A("  canal   text not null check (canal in ('Mayorista','Minorista','Institucional')),")
A("  linea   text not null check (linea in ('Abarrotes importados','Cuidado del hogar')),")
A("  version text not null check (version in ('LY','PPTO','REAL')),")
A("  monto   numeric(14,2) not null check (monto >= 0),")
A("  primary key (mes, canal, linea, version)")
A(");")
A("")
A("create table if not exists fpa_pyg (")
A("  periodo text not null,")
A("  cuenta  text not null,")
A("  monto   numeric(14,2) not null,")
A("  orden   int not null,")
A("  primary key (periodo, cuenta)")
A(");")
A("")
A("create table if not exists fpa_balance (")
A("  corte  text not null check (corte in ('2025-12','2026-06')),")
A("  grupo  text not null check (grupo in ('ACTIVO','PASIVO','PATRIMONIO')),")
A("  cuenta text not null,")
A("  monto  numeric(14,2) not null,")
A("  orden  int not null,")
A("  primary key (corte, cuenta)")
A(");")
A("")
A("create table if not exists fpa_cxc_aging (")
A("  cliente text not null,")
A("  tramo   text not null check (tramo in ('Corriente','31-60','61-90','90+')),")
A("  monto   numeric(14,2) not null check (monto >= 0),")
A("  primary key (cliente, tramo)")
A(");")
A("")
A("create table if not exists fpa_inv_sku (")
A("  sku       text primary key,")
A("  nombre    text not null,")
A("  stock_u   int not null check (stock_u >= 0),")
A("  costo_u   numeric(12,2) not null check (costo_u >= 0),")
A("  vta_mes_u int not null check (vta_mes_u > 0)")
A(");")
A("")
A("create table if not exists fpa_puente (")
A("  tipo  text not null check (tipo in ('PVM','EBITDA')),")
A("  paso  text not null,")
A("  monto numeric(14,2) not null,")
A("  orden int not null,")
A("  primary key (tipo, paso)")
A(");")
A("")
A("create table if not exists fpa_parametros (")
A("  clave    text primary key,")
A("  valor    numeric(14,4) not null,")
A("  etiqueta text not null")
A(");")
A("")
A("create table if not exists fpa_cxc_canal (")
A("  canal text primary key check (canal in ('Mayorista','Minorista','Institucional')),")
A("  monto numeric(14,2) not null check (monto >= 0)")
A(");")
A("")
A("create table if not exists fpa_inv_linea (")
A("  linea text primary key check (linea in ('Abarrotes importados','Cuidado del hogar')),")
A("  monto numeric(14,2) not null check (monto >= 0)")
A(");")
A("")
A("create table if not exists fpa_acciones (")
A("  id         text primary key,")
A("  nombre     text not null,")
A("  efecto_caja numeric(14,2) not null,")
A("  efecto_py  text not null,")
A("  kpi        text not null")
A(");")
A("")
A("-- RLS: lectura publica (misma convencion que panel-minero) --")
for t in ["fpa_ventas", "fpa_pyg", "fpa_balance", "fpa_cxc_aging",
          "fpa_inv_sku", "fpa_puente", "fpa_parametros",
          "fpa_cxc_canal", "fpa_inv_linea", "fpa_acciones"]:
    A(f"alter table {t} enable row level security;")
    A(f'drop policy if exists "lectura publica {t}" on {t};')
    A(f'create policy "lectura publica {t}" on {t} for select to anon using (true);')
    A("")
A("-- Vistas de agregados: lo que consume el demo --")
A("create or replace view v_fpa_ventas_canal as")
A("select version, canal, sum(monto) as monto from fpa_ventas group by version, canal;")
A("")
A("create or replace view v_fpa_ventas_mes as")
A("select version, mes, sum(monto) as monto from fpa_ventas group by version, mes order by version, mes;")
A("")
A("create or replace view v_fpa_ventas_linea as")
A("select version, linea, sum(monto) as monto from fpa_ventas group by version, linea;")
A("")
A("-- DSO del canal institucional: ventas diarias = 5144000 / 181 --")
A("create or replace view v_fpa_aging_cliente as")
A("select cliente,")
A("  sum(monto) as total,")
A("  sum(case when tramo in ('61-90','90+') then monto else 0 end) as mora60,")
A("  round((sum(monto) / (5144000.0 / 181))::numeric, 1) as dso")
A("from fpa_cxc_aging group by cliente order by total desc;")
A("")
A("create or replace view v_fpa_sku as")
A("select sku, nombre, stock_u, costo_u, vta_mes_u,")
A("  round((stock_u * costo_u)::numeric, 0) as valorizado,")
A("  round((stock_u::numeric / vta_mes_u), 1) as cobertura_m")
A("from fpa_inv_sku order by valorizado desc;")
A("")
A("-- Seed (idempotente) --")
def ins(table, cols, rows):
    A(f"insert into {table} ({', '.join(cols)}) values")
    A(",\n".join("  (" + ", ".join(lit(v) for v in r) + ")" for r in rows))
    A("on conflict do nothing;")
    A("")

ins("fpa_ventas", ["mes", "canal", "linea", "version", "monto"], cells)
ins("fpa_pyg", ["periodo", "cuenta", "monto", "orden"], PYG)
ins("fpa_balance", ["corte", "grupo", "cuenta", "monto", "orden"], BAL)
ins("fpa_cxc_aging", ["cliente", "tramo", "monto"], AGING)
ins("fpa_inv_sku", ["sku", "nombre", "stock_u", "costo_u", "vta_mes_u"], SKUS)
ins("fpa_puente", ["tipo", "paso", "monto", "orden"], PUENTES)
ins("fpa_parametros", ["clave", "valor", "etiqueta"], PARAMS)
ins("fpa_cxc_canal", ["canal", "monto"], CXC_CANAL)
ins("fpa_inv_linea", ["linea", "monto"], INV_LINEA)
ins("fpa_acciones", ["id", "nombre", "efecto_caja", "efecto_py", "kpi"], ACCIONES)

A("-- Verificacion post-carga (deben devolver una fila 'OK' cada una) --")
A("-- select case when sum(monto)=28400000 then 'OK ventas REAL' else 'FALLA' end from fpa_ventas where version='REAL';")
A("-- select case when sum(monto)=2000000 then 'OK aging' else 'FALLA' end from fpa_cxc_aging;")
A("-- select case when sum(stock_u*costo_u)=1713800 then 'OK skus' else 'FALLA' end from fpa_inv_sku;")

sql = "\n".join(L)
(BASE / "fpa_schema.sql").write_text(sql, encoding="utf-8")
print(f"fpa_schema.sql OK: {len(sql)} chars, {len(cells)} filas ventas, "
      f"{len(PYG)} pyg, {len(BAL)} balance, {len(AGING)} aging, {len(SKUS)} skus")
