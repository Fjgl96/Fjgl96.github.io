"""Pruebas unitarias del portafolio (sin dependencias, stdlib puro).

T1: todo .svg parsea como XML (un & sin escapar tumba la imagen).
T2: sin & desnudos en .svg.
T3: todo href/src local de index + proyectos/*.html existe en disco.
T4: balance grueso de tags en los HTML tocados.
T5: invariantes de data.json del pack (desvios, puentes, balance, drill).
T6: la ficha declara los canonicos de data.json.

Uso:  python scripts/auditar.py        (exit 0 = todo verde)
"""
import json
import pathlib
import re
import sys
import xml.dom.minidom
from html.parser import HTMLParser

BASE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(nombre, cond, extra=""):
    global ok
    print(("OK  " if cond else "FALLA"), nombre, extra)
    ok = ok and cond


# ---------- T1 + T2: SVGs ----------
svgs = sorted((BASE / "assets" / "img").rglob("*.svg"))
check("T1 hay SVGs", len(svgs) > 0, f"({len(svgs)})")
for p in svgs:
    t = p.read_text(encoding="utf-8")
    try:
        xml.dom.minidom.parse(str(p))
        well = True
    except Exception:
        well = False
    check(f"T1 xml {p.relative_to(BASE)}", well)
    bare = re.findall(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;)", t)
    check(f"T2 sin-& {p.relative_to(BASE)}", not bare, f"({len(bare)} desnudos)" if bare else "")

# ---------- T3 + T4: HTML ----------
pags = [BASE / "index.html", *sorted((BASE / "proyectos").glob("*.html"))]


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.stack = []
        self.bad = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if k in a:
                self.refs.append(a[k])
        if tag not in ("meta", "link", "img", "input", "br", "hr",
                       "source", "circle", "path", "rect", "use"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag not in ("meta", "link", "img", "input", "br", "hr"):
            self.bad.append(tag)


for pag in pags:
    html = pag.read_text(encoding="utf-8")
    p = Refs()
    p.feed(html)
    faltan = []
    for r in p.refs:
        if r.startswith(("http", "mailto:", "tel:", "#", "data:")):
            continue
        rel = r.split("#")[0].split("?")[0]
        tgt = (pag.parent / rel).resolve()
        if not tgt.exists():
            faltan.append(r)
    check(f"T3 refs {pag.relative_to(BASE)}", not faltan, str(faltan[:3]) if faltan else "")
    check(f"T4 tags {pag.relative_to(BASE)}", not p.stack and not p.bad,
          f"abiertos={p.stack} mal-cierre={p.bad}" if (p.stack or p.bad) else "")

# ---------- T5: data.json ----------
dj = BASE / "assets" / "demo" / "fpa-pack" / "data.json"
if dj.exists():
    d = json.loads(dj.read_text(encoding="utf-8"))
    check("T5 desvio ventas", d["real_h1"] - d["ppto_h1"] == -1700000)
    check("T5 desvio ebitda", d["ebitda_real"] - d["ebitda_ppto"] == -950000)
    check("T5 puente ebitda", sum(b["monto"] for b in d["bridge"][1:-1]) == -950000)
    check("T5 puente pvm", sum(b["monto"] for b in d["pvm"][1:-1]) == -1700000)
    b = d["bal_jun"]
    tot = b["caja"] + b["cxc"] + b["inv"] + b["otros_ac"] + b["af_neto"]
    pp = b["cxp"] + b["deuda_cp"] + b["otros_pc"] + b["deuda_lp"] + b["patrimonio"]
    check("T5 balance cuadra", tot == pp == 25310000)
    check("T5 aging", sum(c["total"] for c in d["clientes_inst"]) == 2000000)
    check("T5 skus", sum(s["valorizado"] for s in d["skus_hogar"]) == 3350000)
    check("T5 flujo ata", d["flujo"]["d_caja"] == -250000 == d["flujo"]["fco"] + d["flujo"]["capex"] + d["flujo"]["d_deuda_cp"] + d["flujo"]["d_deuda_lp"])
    check("T5 LTM", d["supuestos"]["ebitda_ltm"] == 5550000 and d["supuestos"]["deuda_ebitda"] == 1.80)
    # ---------- T6: ficha vs canonicos ----------
    ficha = (BASE / "proyectos" / "fpa-pack.html").read_text(encoding="utf-8")
    for txt in ["28.40M", "30.10M", "2.35M", "3.30M", "79 d", "330k", "702k"]:
        check(f"T6 ficha dice {txt}", txt in ficha)
else:
    print("T5/T6 omitidos (sin data.json del pack)")

print("RESULTADO:", "TODO OK" if ok else "HAY FALLAS")
raise SystemExit(0 if ok else 1)
