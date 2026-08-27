# -*- coding: utf-8 -*-
"""Proyecto Norte — modelo mensual de un desarrollo inmobiliario de dos torres.

Proyecto SINTÉTICO. Los números son inventados y redondos; lo que se conserva
del oficio es la mecánica: la velocidad de ventas dispara umbrales, los umbrales
disparan la obra, el costo sale antes que el ingreso y el IGV se paga sobre
anticipos que todavía no son venta.
"""

# ── Supuestos del proyecto ────────────────────────────────────────────────
P = dict(
    torres           = 2,
    deptos_torre     = 120,
    m2_depto         = 70,
    precio_m2        = 1600,      # US$ por m2 vendible
    ratio_techado    = 1.40,      # area techada / area vendible
    costo_m2_techado = 600,       # US$, costo directo
    otros_duros_pct  = 0.08,      # ascensores, bombas, contra incendio
    blandos_pct      = 0.18,      # diseño, licencias, promotora, publicidad
    terreno_total    = 2_700_000, # 1 800 m2 a US$ 1 500

    venta_inicial    = 1,         # deptos vendidos el primer mes
    incremento       = 1,
    velocidad_max    = 6,         # tope de deptos por mes
    umbral_obra      = 0.30,      # preventa que dispara el inicio de obra
    umbral_torre_b   = 0.50,      # avance de la torre A que abre la venta de B
    meses_obra       = 14,
    mes_inicio_venta = 1,

    cuota_inicial    = 0.16,      # promedio ponderado de las modalidades
    igv_compras      = 0.18,
    igv_ventas       = 0.09,      # tasa reducida de vivienda
    horizonte        = 72,
)

def curva_s(n):
    """Reparto del costo de obra: arranca lento, pico al medio, cierra lento."""
    import math
    b = [math.sin(math.pi * (i + 0.5) / n) for i in range(n)]
    t = sum(b)
    return [x / t for x in b]

def correr(p=None, **cambios):
    p = dict(P if p is None else p)
    p.update(cambios)
    H = p['horizonte']
    z = lambda: [0.0] * (H + 1)

    ingreso_torre = p['deptos_torre'] * p['m2_depto'] * p['precio_m2']
    m2_techado    = p['deptos_torre'] * p['m2_depto'] * p['ratio_techado']
    directo       = m2_techado * p['costo_m2_techado']
    duros         = directo * (1 + p['otros_duros_pct'])
    blandos       = ingreso_torre * p['blandos_pct']
    precio_depto  = p['m2_depto'] * p['precio_m2']

    # ── Ventas: rampa hasta el tope, por torre, con su mes de apertura ────
    def ventas(mes_apertura):
        v, acum, vel = z(), 0, p['venta_inicial'] - p['incremento']
        for m in range(mes_apertura, H + 1):
            if acum >= p['deptos_torre']: break
            vel = min(vel + p['incremento'], p['velocidad_max'])
            n = min(vel, p['deptos_torre'] - acum)
            v[m] = n; acum += n
        return v

    vA = ventas(p['mes_inicio_venta'])
    acumA = [sum(vA[:m + 1]) for m in range(H + 1)]

    # Gatillo 1: la torre B abre cuando A cruza su umbral
    mes_abre_B = next((m for m in range(H + 1)
                       if acumA[m] >= p['umbral_torre_b'] * p['deptos_torre']), None)
    mes_abre_B = (mes_abre_B + 1) if mes_abre_B else H
    vB = ventas(mes_abre_B)
    acumB = [sum(vB[:m + 1]) for m in range(H + 1)]

    # Gatillo 2: la obra arranca cuando la preventa de esa torre cruza el umbral
    def mes_obra(acum):
        m = next((m for m in range(H + 1)
                  if acum[m] >= p['umbral_obra'] * p['deptos_torre']), None)
        return (m + 1) if m is not None else None
    obraA, obraB = mes_obra(acumA), mes_obra(acumB)
    entregaA = obraA + p['meses_obra'] if obraA else None
    entregaB = obraB + p['meses_obra'] if obraB else None

    # ── Cobranza: la inicial al vender, el saldo a la entrega ─────────────
    cobro = z()
    for v, entrega in ((vA, entregaA), (vB, entregaB)):
        for m in range(H + 1):
            if not v[m]: continue
            cobro[m] += v[m] * precio_depto * p['cuota_inicial']
            me = max(entrega, m) if entrega else H
            saldo_u = v[m] * precio_depto * (1 - p['cuota_inicial'])
            for k, w in enumerate((0.5, 0.3, 0.2)):   # entrega e independización
                if me + k <= H: cobro[me + k] += saldo_u * w

    # ── Egresos ───────────────────────────────────────────────────────────
    egreso = z()
    egreso[1] += p['terreno_total'] * 0.5          # dos fracciones, como en la práctica
    egreso[12] += p['terreno_total'] * 0.5
    for obra, v in ((obraA, vA), (obraB, vB)):
        if not obra: continue
        for i, w in enumerate(curva_s(p['meses_obra'])):
            if obra + i <= H: egreso[obra + i] += duros * w
        # blandos: mitad antes de la obra, mitad durante
        pre = max(obra - 9, 1)
        for m in range(pre, obra):
            egreso[m] += blandos * 0.5 / max(obra - pre, 1)
        for i in range(p['meses_obra']):
            if obra + i <= H: egreso[obra + i] += blandos * 0.5 / p['meses_obra']

    # ── IGV ───────────────────────────────────────────────────────────────
    # El 18 % de las compras sale de caja con el costo. El 9 % de la cobranza
    # se debe, pero se compensa contra el crédito acumulado. Mientras el
    # crédito no se agote no se paga nada — y ese saldo es caja inmovilizada.
    igv_flujo, credito_acum = z(), z()
    saldo = 0.0
    for m in range(H + 1):
        credito = egreso[m] * p['igv_compras']     # sale de caja
        debito  = cobro[m] * p['igv_ventas']       # se debe
        igv_flujo[m] = credito                     # salida por compras
        saldo += credito
        usa = min(saldo, debito)
        saldo -= usa
        igv_flujo[m] -= usa                        # el débito compensado no sale de caja
        if debito > usa:
            igv_flujo[m] += (debito - usa)         # el exceso sí se paga
        credito_acum[m] = saldo

    neto  = [cobro[m] - egreso[m] - igv_flujo[m] for m in range(H + 1)]
    acumc = []
    s = 0.0
    for m in range(H + 1):
        s += neto[m]; acumc.append(s)

    pico = min(acumc)
    mes_pico = acumc.index(pico)
    return dict(p=p, vA=vA, vB=vB, acumA=acumA, acumB=acumB, cobro=cobro,
                egreso=egreso, igv=igv_flujo, credito_igv=credito_acum, neto=neto, acum=acumc,
                obraA=obraA, obraB=obraB, entregaA=entregaA, entregaB=entregaB,
                mes_abre_B=mes_abre_B, pico=pico, mes_pico=mes_pico,
                ingreso_total=sum(cobro), egreso_total=sum(egreso) + sum(igv_flujo),
                utilidad=sum(neto), ingreso_torre=ingreso_torre,
                precio_depto=precio_depto, duros=duros, blandos=blandos)

if __name__ == '__main__':
    r = correr()
    p = r['p']
    M = lambda v: f"{v/1e6:,.2f}".replace(',', ' ')
    print("══ PROYECTO NORTE · supuestos ══")
    print(f"  {p['torres']} torres x {p['deptos_torre']} deptos de {p['m2_depto']} m2 · "
          f"US$ {p['precio_m2']:,}/m2 → depto US$ {r['precio_depto']:,.0f}")
    print(f"  ingreso por torre US$ {M(r['ingreso_torre'])} M · costo duro por torre US$ {M(r['duros'])} M")
    print(f"  terreno US$ {M(p['terreno_total'])} M · obra {p['meses_obra']} meses")
    print(f"  velocidad: arranca en {p['venta_inicial']}, +{p['incremento']}/mes, tope {p['velocidad_max']}")

    print("\n══ GATILLOS (los calcula el modelo, no se fijan a mano) ══")
    print(f"  torre A: preventa cruza {p['umbral_obra']:.0%} en el mes {r['obraA']-1} → obra arranca mes {r['obraA']}, entrega mes {r['entregaA']}")
    print(f"  torre B: venta abre mes {r['mes_abre_B']} (A llegó a {p['umbral_torre_b']:.0%}) → obra mes {r['obraB']}, entrega mes {r['entregaB']}")

    costos = sum(r['egreso'])
    util_op = r['ingreso_total'] - costos
    saldo_igv = r['credito_igv'][-1]
    print("\n══ RESULTADO ══")
    print(f"  ingresos            US$ {M(r['ingreso_total'])} M")
    print(f"  costos del proyecto US$ {M(costos)} M")
    print(f"  utilidad            US$ {M(util_op)} M   ·  margen {util_op/r['ingreso_total']:.1%}")
    print(f"\n  IGV: salió con el costo US$ {M(sum(r['egreso'])*p['igv_compras'])} M, se compensó contra la cobranza,")
    print(f"       y queda un saldo a favor de US$ {M(saldo_igv)} M al cierre.")
    print(f"       No es una pérdida: es caja que no volvió dentro del proyecto.")

    print(f"\n══ NECESIDAD MÁXIMA DE CAPITAL ══")
    print(f"  US$ {M(-r['pico'])} M en el mes {r['mes_pico']}")
    print(f"  = {-r['pico']/r['ingreso_total']:.1%} de los ingresos del proyecto")
    print(f"  se recupera en el mes {next(m for m in range(r['mes_pico'], len(r['acum'])) if r['acum'][m] >= 0)}")

    print("\n  mes  ventas A/B   cobranza    egreso      IGV      acumulado")
    for m in range(1, 49):
        if m <= 6 or m % 3 == 0 or m in (r['obraA'], r['obraB'], r['entregaA'], r['entregaB'], r['mes_pico']):
            marca = ''
            if m == r['obraA']: marca = ' ← obra A'
            if m == r['obraB']: marca = ' ← obra B'
            if m == r['entregaA']: marca = ' ← entrega A'
            if m == r['entregaB']: marca = ' ← entrega B'
            if m == r['mes_pico']: marca = ' ◄ PICO'
            print(f"  {m:>3}   {r['vA'][m]:>3.0f}/{r['vB'][m]:<3.0f}  {r['cobro'][m]/1e6:>9.2f} {r['egreso'][m]/1e6:>9.2f} {r['igv'][m]/1e6:>8.2f} {r['acum'][m]/1e6:>12.2f}{marca}")
