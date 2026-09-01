/**
 * fig-engine.js — LAS FIGURAS SE CALCULAN, NO SE DIBUJAN A MANO
 *
 * Las figuras de las notas de análisis son SVG en línea con revelado por
 * pasos. El formato funciona; lo que no escalaba era la autoría. En la nota
 * de Buenaventura cada coordenada está escrita a mano: la altura de cada
 * barra, la posición acumulada de cada tramo, el conector entre una barra y
 * la siguiente, y el retardo de cada texto. Para una figura se puede. Para
 * una nota por compañía, no: cambiar un número obliga a recalcular la
 * geometría entera, y un error de aritmética queda dibujado sin que nada
 * avise.
 *
 * Acá el dato entra como dato —etiqueta, valor, tipo— y la geometría sale
 * calculada. El módulo es puro: no toca el DOM, corre en Node y trae sus
 * tests. La animación no la maneja: emite las mismas clases que ya conocen
 * `analisis.css` y `analisis.js` (`an-barra`, `an-flota`, `an-aparece`, y el
 * retardo en `--d`), así que la página no cambia — cambia quién escribe el
 * SVG.
 *
 * LO QUE EL MOTOR NO DEJA PASAR: una cascada que no cierra. Si la barra
 * final no es la suma de la base más los tramos, tira error en vez de
 * dibujarla. Es el error clásico de este gráfico y a mano no se ve.
 *
 *   node assets/js/fig-engine.js     corre los tests
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Fig = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ---------- paleta: la misma de las figuras publicadas ---------- */
  var COLOR = {
    base:    '#173b6c',   /* punto de partida y llegada          */
    suma:    '#149ddd',   /* tramo que suma                      */
    resta:   '#b33a3a',   /* tramo que resta                     */
    cierre:  '#0f6b46',   /* total final, cuando se quiere verde */
    guia:    '#cfe0f2',   /* eje y conectores                    */
    tenue:   '#5f7391',   /* etiquetas                           */
    tinta:   '#173b6c'    /* texto fuerte                        */
  };

  /* Las clases tipográficas viajan dentro del SVG porque la figura tiene que
     poder leerse suelta (una imagen aparte, un embed) sin el CSS del sitio. */
  var TIPOGRAFIA =
    '\n .fh{font-family:Poppins,Helvetica,Arial,sans-serif;font-size:9.5px;font-weight:600;letter-spacing:1px;fill:#0b6d9e}' +
    '\n .fe{font-family:Poppins,Helvetica,Arial,sans-serif;font-size:9px;font-weight:600;fill:#5f7391}' +
    '\n .fv{font-family:Raleway,Helvetica,Arial,sans-serif;font-size:12px;font-weight:700;fill:#173b6c}' +
    '\n .fn{font-family:\'Open Sans\',Helvetica,Arial,sans-serif;font-size:9px;fill:#5f7391}\n';

  /* ---------- utilidades ---------- */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
  function r1(n) { return Math.round(n * 10) / 10; }

  /* Separador de miles a la española (punto). Sin esto, "2106800" obliga al
     lector a contar dígitos —que es exactamente el trabajo que la figura
     tiene que ahorrarle. */
  function miles(x, dec) {
    var s = Math.abs(x).toFixed(dec == null ? 0 : dec).split(".");
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return s.join(",");
  }
  /* El signo menos tipográfico, no el guion del teclado: en una cifra
     negativa el guion se lee como separador. */
  function conSigno(v, dec) {
    return (v < 0 ? '\u2212' : '+') + miles(v, dec);
  }
  function sinSigno(v, dec) {
    return (v < 0 ? '\u2212' : '') + miles(v, dec);
  }

  /* =====================================================================
     CASCADA (waterfall)

     Un punto de partida, tramos que suman o restan, y un cierre. Cada tramo
     flota: arranca donde terminó el anterior. Eso es justamente lo que se
     calcula mal a mano, porque la posición de un tramo depende de todos los
     que vinieron antes.
     ===================================================================== */
  var GEO = {
    ancho: 856, alto: 340,
    izq: 84, der: 72,          /* márgenes laterales    */
    arriba: 70, piso: 266,     /* banda del dibujo      */
    barra: 118,                /* ancho de barra        */
    paso: 180,                 /* retardo entre barras  */
    lag: 320                   /* el texto sigue a su barra */
  };

  function acumular(pasos) {
    var acum = 0, out = [], i, p, desde, hasta;
    for (i = 0; i < pasos.length; i++) {
      p = pasos[i];
      if (p.tipo === 'base' || p.tipo === 'total') {
        desde = 0; hasta = p.valor; acum = p.valor;
      } else {
        desde = acum; hasta = acum + p.valor; acum = hasta;
      }
      out.push({ etiqueta: p.etiqueta, valor: p.valor, tipo: p.tipo || 'delta',
                 color: p.color, desde: desde, hasta: hasta });
    }
    return out;
  }

  /* El control que justifica el motor: la cascada tiene que cerrar. */
  function verificarCierre(pasos, tol) {
    var i, esperado = null, acum = 0, visto = false;
    for (i = 0; i < pasos.length; i++) {
      var p = pasos[i];
      if (p.tipo === 'base') { acum = p.valor; visto = true; }
      else if (p.tipo === 'total') { esperado = acum; 
        if (Math.abs(p.valor - esperado) > tol) {
          throw new Error(
            'La cascada no cierra: "' + p.etiqueta + '" vale ' + p.valor +
            ' y la suma de los tramos da ' + r1(esperado) +
            ' (diferencia ' + r1(p.valor - esperado) + ', tolerancia ' + tol + ').');
        }
        acum = p.valor;
      } else { 
        if (!visto) throw new Error('La cascada arranca con un tramo: falta el paso "base".');
        acum += p.valor; }
    }
    return true;
  }

  function cascada(spec) {
    var g = Object.assign({}, GEO, spec.geo || {});
    var tol = spec.tolerancia == null ? 0.5 : spec.tolerancia;
    var dec = spec.decimales == null ? 0 : spec.decimales;
    if (!spec.pasos || spec.pasos.length < 2) throw new Error('Una cascada necesita al menos dos pasos.');

    verificarCierre(spec.pasos, tol);
    var pasos = acumular(spec.pasos);

    /* Escala: entra todo lo que la figura toca, incluido el punto más alto
       que alcanza un tramo intermedio (que puede superar al total). */
    var techo = 0, i, p;
    for (i = 0; i < pasos.length; i++) {
      techo = Math.max(techo, pasos[i].desde, pasos[i].hasta);
    }
    if (!(techo > 0)) throw new Error('La cascada no tiene valores positivos que dibujar.');
    var banda = g.piso - g.arriba;
    var y = function (v) { return g.piso - (v / techo) * banda; };

    /* Reparto horizontal: las barras se distribuyen parejo en el ancho útil. */
    /* El ancho de barra es un MÁXIMO, no un fijo: con muchos tramos el paso
       entre barras se achica y un ancho fijo las hace solaparse. Se deja un
       18 % de aire entre barras contiguas. */
    var util = g.ancho - g.izq - g.der;
    var n = pasos.length;
    var barra = g.barra;
    if (n > 1) {
      var pasoMax = util / n;
      if (barra > pasoMax * 0.82) barra = Math.max(pasoMax * 0.82, 14);
    }
    var salto = n > 1 ? (util - barra) / (n - 1) : 0;
    var x = function (k) { return g.izq + k * salto; };

    var piezas = [];
    piezas.push('<rect width="' + g.ancho + '" height="' + g.alto + '" fill="#fff"/>');
    if (spec.titulo) piezas.push('<text class="fh" x="24" y="26">' + esc(spec.titulo) + '</text>');
    piezas.push('<line x1="' + g.izq + '" y1="' + g.piso + '" x2="' + (g.ancho - g.der) +
                '" y2="' + g.piso + '" stroke="' + COLOR.guia + '" stroke-width="1.4"/>');

    for (i = 0; i < n; i++) {
      p = pasos[i];
      var yTop = y(Math.max(p.desde, p.hasta));
      var yBot = y(Math.min(p.desde, p.hasta));
      var alto = Math.max(yBot - yTop, 1.5);      /* un tramo nulo sigue siendo visible */
      var px = x(i);
      var fijo = (p.tipo === 'base' || p.tipo === 'total');
      var color = p.color || (fijo ? (p.tipo === 'total' && i === n - 1 ? COLOR.cierre : COLOR.base)
                                   : (p.valor < 0 ? COLOR.resta : COLOR.suma));
      var dBarra = i * g.paso;
      var dTexto = dBarra + g.lag;

      /* Una barra apoyada en el piso crece desde abajo (`an-barra`); un tramo
         que flota no puede escalar desde una base que no toca, así que
         aparece y se desliza (`an-flota`). Es la diferencia que el CSS ya
         distingue. */
      piezas.push('<rect class="' + (fijo ? 'an-barra' : 'an-flota') + '" style="--d:' + dBarra + 'ms" x="' +
        r1(px) + '" y="' + r1(yTop) + '" width="' + r1(barra) + '" height="' + r1(alto) +
        '" rx="3" fill="' + color + '" fill-opacity="' + (fijo ? '1' : '0.9') + '"/>');

      var texto = fijo ? sinSigno(p.valor, dec) : conSigno(p.valor, dec);
      piezas.push('<text class="fv an-aparece" style="--d:' + dTexto + 'ms" x="' + r1(px + barra / 2) +
        '" y="' + r1(yTop - 9) + '" text-anchor="middle" fill="' + color + '">' + esc(texto) + '</text>');
      piezas.push('<text class="fe an-aparece" style="--d:' + dTexto + 'ms" x="' + r1(px + barra / 2) +
        '" y="' + (g.piso + 20) + '" text-anchor="middle">' + esc(p.etiqueta) + '</text>');

      /* Conector: sale del nivel donde quedó la barra anterior y llega al
         arranque de esta. Es el hilo que hace legible la cascada. */
      if (i > 0) {
        var prev = pasos[i - 1];
        var yEnlace = y(prev.hasta);
        piezas.push('<line class="an-aparece" style="--d:' + dBarra + 'ms" x1="' + r1(x(i - 1) + barra) +
          '" y1="' + r1(yEnlace) + '" x2="' + r1(px) + '" y2="' + r1(yEnlace) +
          '" stroke="' + COLOR.guia + '" stroke-width="1.2" stroke-dasharray="3 3"/>');
      }
    }

    if (spec.nota) piezas.push('<text class="fn" x="24" y="' + (g.alto - 16) + '">' + esc(spec.nota) + '</text>');

    var a = spec.a11y || {};
    var idT = 't-' + (a.id || 'fig'), idD = 'd-' + (a.id || 'fig');
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + g.ancho + ' ' + g.alto +
      '" width="' + g.ancho + '" height="' + g.alto + '" role="img" aria-labelledby="' + idT + ' ' + idD + '">' +
      '<title id="' + idT + '">' + esc(a.titulo || spec.titulo || '') + '</title>' +
      '<desc id="' + idD + '">' + esc(a.desc || '') + '</desc>' +
      '<style>' + TIPOGRAFIA + '</style>' + piezas.join('') + '</svg>';
  }

  /* ---------- lecturas derivadas ----------
     Frases que hoy se escriben a mano abajo de la figura y que en realidad
     son aritmética: si el número cambia, la frase tiene que cambiar sola. */
  function conversion(pasos) {
    var suma = 0, resta = 0, i, p;
    for (i = 0; i < pasos.length; i++) {
      p = pasos[i];
      if (p.tipo === 'base' || p.tipo === 'total') continue;
      if (p.valor >= 0) suma += p.valor; else resta += -p.valor;
    }
    if (suma <= 0) return null;
    return { suma: suma, resta: resta, retenido: (suma - resta) / suma };
  }

  var API = { cascada: cascada, acumular: acumular, verificarCierre: verificarCierre,
              conversion: conversion, COLOR: COLOR, GEO: GEO };

  /* =====================================================================
     TESTS
     ===================================================================== */
  function tests() {
    var T = [];
    function ok(n, c) { T.push([n, !!c]); }
    function eq(n, a, b) { T.push([n + '  (' + a + ')', a === b]); }
    function tira(n, fn, frag) {
      var msg = null;
      try { fn(); } catch (e) { msg = e.message; }
      T.push([n, msg !== null && (!frag || msg.indexOf(frag) >= 0)]);
    }

    /* ---- la cascada tiene que cerrar ---- */
    var buena = [
      { etiqueta: 'Bruto 2023', valor: 91.2, tipo: 'base' },
      { etiqueta: 'Más ingresos', valor: 907.8, tipo: 'delta' },
      { etiqueta: 'Más costo', valor: -216.7, tipo: 'delta' },
      { etiqueta: 'Bruto 2025', valor: 782.3, tipo: 'total' }
    ];
    ok('una cascada que cierra pasa', API.verificarCierre(buena, 0.5));
    tira('una cascada que NO cierra tira error', function () {
      API.verificarCierre([
        { etiqueta: 'A', valor: 100, tipo: 'base' },
        { etiqueta: 'B', valor: 50, tipo: 'delta' },
        { etiqueta: 'C', valor: 900, tipo: 'total' }
      ], 0.5);
    }, 'no cierra');
    tira('el error dice cuánto falta', function () {
      API.verificarCierre([
        { etiqueta: 'A', valor: 100, tipo: 'base' },
        { etiqueta: 'C', valor: 130, tipo: 'total' }
      ], 0.5);
    }, 'diferencia 30');
    ok('la tolerancia absorbe el redondeo de los datos publicados',
       API.verificarCierre([
         { etiqueta: 'A', valor: 91.2, tipo: 'base' },
         { etiqueta: 'B', valor: 907.8, tipo: 'delta' },
         { etiqueta: 'C', valor: -216.7, tipo: 'delta' },
         { etiqueta: 'D', valor: 782.4, tipo: 'total' }   /* 0.1 de redondeo */
       ], 0.5));
    tira('pero no absorbe un error de verdad', function () {
      API.verificarCierre([
        { etiqueta: 'A', valor: 91.2, tipo: 'base' },
        { etiqueta: 'B', valor: 907.8, tipo: 'delta' },
        { etiqueta: 'C', valor: -216.7, tipo: 'delta' },
        { etiqueta: 'D', valor: 800, tipo: 'total' }
      ], 0.5);
    }, 'no cierra');
    tira('una cascada que arranca con un tramo tira error', function () {
      API.verificarCierre([{ etiqueta: 'B', valor: 50, tipo: 'delta' }], 0.5);
    }, 'arranca con un tramo');

    /* ---- acumulación: cada tramo arranca donde terminó el anterior ---- */
    var ac = API.acumular(buena);
    eq('el tramo 2 arranca en la base', ac[1].desde, 91.2);
    eq('el tramo 2 termina en base+valor', r1(ac[1].hasta), 999);
    eq('el tramo 3 arranca donde terminó el 2', r1(ac[2].desde), 999);
    eq('un tramo negativo baja', ac[2].hasta < ac[2].desde, true);
    eq('el total vuelve al piso', ac[3].desde, 0);

    /* ---- geometría ---- */
    var svg = API.cascada({
      titulo: 'T', nota: 'N', a11y: { id: 'x', titulo: 'ti', desc: 'de' }, pasos: buena, decimales: 0
    });
    ok('devuelve un SVG', svg.indexOf('<svg') === 0);
    ok('lleva title y desc para lectores de pantalla',
       svg.indexOf('<title id="t-x">ti</title>') > 0 && svg.indexOf('<desc id="d-x">de</desc>') > 0);
    ok('las barras fijas usan an-barra', svg.indexOf('class="an-barra"') > 0);
    ok('los tramos que flotan usan an-flota', svg.indexOf('class="an-flota"') > 0);
    ok('los textos usan an-aparece', svg.indexOf('class="fv an-aparece"') > 0);
    ok('cada pieza trae su retardo', /style="--d:\d+ms"/.test(svg));

    /* toda la geometría, adentro del lienzo */
    var fuera = 0, m, re = /<rect class="an-[^"]*"[^>]*x="([-\d.]+)"[^>]*y="([-\d.]+)"[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"/g;
    while ((m = re.exec(svg))) {
      var X = +m[1], Y = +m[2], W = +m[3], H = +m[4];
      if (X < 0 || Y < 0 || X + W > GEO.ancho || Y + H > GEO.alto || H <= 0) fuera++;
    }
    eq('ninguna barra se sale del lienzo ni tiene altura cero', fuera, 0);

    /* los retardos avanzan, nunca retroceden */
    var ds = [], dm, dre = /--d:(\d+)ms/g;
    while ((dm = dre.exec(svg))) ds.push(+dm[1]);
    var desordenado = 0;
    for (var i = 1; i < ds.length; i++) if (ds[i] < ds[i - 1] - GEO.lag) desordenado++;
    eq('los retardos no retroceden', desordenado, 0);

    /* el signo se dibuja con el menos tipográfico, no con un guion */
    ok('el tramo negativo lleva menos tipográfico', svg.indexOf('\u2212217') > 0);
    ok('el tramo positivo lleva su +', svg.indexOf('+908') > 0);
    ok('la base va sin signo', svg.indexOf('>91<') > 0);

    /* ---- escala ---- */
    var alto2 = API.cascada({ pasos: [
      { etiqueta: 'a', valor: 100, tipo: 'base' },
      { etiqueta: 'b', valor: 900, tipo: 'delta' },
      { etiqueta: 'c', valor: -900, tipo: 'delta' },
      { etiqueta: 'd', valor: 100, tipo: 'total' }
    ] });
    ok('la escala considera el pico de un tramo intermedio, no solo el total',
       alto2.indexOf('an-flota') > 0 && alto2.length > 0);
    tira('una cascada sin valores positivos tira error', function () {
      API.cascada({ pasos: [
        { etiqueta: 'a', valor: 0, tipo: 'base' },
        { etiqueta: 'b', valor: 0, tipo: 'total' }
      ] });
    }, 'positivos');
    tira('una cascada de un solo paso tira error', function () {
      API.cascada({ pasos: [{ etiqueta: 'a', valor: 1, tipo: 'base' }] });
    }, 'al menos dos');

    /* ---- legibilidad de las cifras ---- */
    eq("miles con separador español", miles(2106800), "2.106.800");
    eq("miles no toca los de tres dígitos", miles(908), "908");
    eq("tramo negativo grande, con signo y separador", conSigno(-830956), "\u2212830.956");
    var grande = API.cascada({ pasos: [
      { etiqueta: "a", valor: 2106800, tipo: "base" },
      { etiqueta: "b", valor: 1240000, tipo: "delta" },
      { etiqueta: "c", valor: -830956, tipo: "delta" },
      { etiqueta: "d", valor: 2515844, tipo: "total" }
    ] });
    ok("las cifras grandes salen agrupadas", grande.indexOf("2.106.800") > 0);

    /* ---- las barras no se solapan, haya los tramos que haya ---- */
    function solapan(nPasos) {
      var ps = [{ etiqueta: "base", valor: 1000, tipo: "base" }], acum = 1000, i;
      for (i = 1; i < nPasos - 1; i++) { ps.push({ etiqueta: "t" + i, valor: 100, tipo: "delta" }); acum += 100; }
      ps.push({ etiqueta: "fin", valor: acum, tipo: "total" });
      var svg = API.cascada({ pasos: ps }), m, re = /<rect class="an-[^"]*"[^>]*x="([\d.]+)"[^>]*width="([\d.]+)"/g;
      var cajas = [];
      while ((m = re.exec(svg))) cajas.push([+m[1], +m[1] + +m[2]]);
      cajas.sort(function (a, b) { return a[0] - b[0]; });
      for (i = 1; i < cajas.length; i++) if (cajas[i][0] < cajas[i - 1][1] - 0.01) return true;
      return false;
    }
    ok("4 tramos: sin solape", !solapan(4));
    ok("7 tramos: sin solape", !solapan(7));
    ok("12 tramos: sin solape", !solapan(12));

    /* ---- lectura derivada ---- */
    var c = API.conversion(buena);
    eq('cuánto de lo que sumó quedó en pie', Math.round(c.retenido * 100), 76);

    /* ---- el texto que entra se escapa ---- */
    var inj = API.cascada({ titulo: '<script>alert(1)</script>', pasos: buena, a11y: { id: 'i' } });
    ok('el título no puede inyectar marcado', inj.indexOf('<script>') === -1);
    ok('las comillas de una etiqueta no rompen el atributo',
       API.cascada({ pasos: [
         { etiqueta: 'a "b"', valor: 10, tipo: 'base' },
         { etiqueta: 'c', valor: 10, tipo: 'total' }
       ] }).indexOf('a &quot;b&quot;') > 0);

    return T;
  }

  function run() {
    var T = tests(), pass = 0, i;
    for (i = 0; i < T.length; i++) {
      if (T[i][1]) pass++; else console.log('  FAIL  ' + T[i][0]);
    }
    console.log('\n' + pass + '/' + T.length + ' tests OK');
    return pass === T.length;
  }

  API.tests = tests; API.run = run;
  if (typeof module === 'object' && module.exports && require.main === module) {
    if (!run()) process.exit(1);
  }
  return API;
});
