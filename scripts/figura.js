#!/usr/bin/env node
/**
 * figura.js — de un JSON de datos al SVG listo para pegar.
 *
 * El sitio es estático y sin build, y las figuras viven en línea dentro del
 * HTML (que es lo correcto: quedan en el código fuente, las lee un buscador
 * y se ven sin JavaScript). Este script es el puente: el análisis se escribe
 * como datos en `figuras/`, y de acá sale el <svg> para pegar en la nota.
 *
 *   node scripts/figura.js figuras/bvn-margen.json          → imprime el SVG
 *   node scripts/figura.js figuras/bvn-margen.json --figure → con <figure> y caption
 *
 * Si la cascada no cierra, no imprime nada: avisa y sale con error.
 */
var fs = require('fs');
var path = require('path');
var Fig = require(path.join(__dirname, '..', 'assets', 'js', 'fig-engine.js'));

var archivo = process.argv[2];
var conFigure = process.argv.indexOf('--figure') > -1;

if (!archivo) {
  console.error('uso: node scripts/figura.js <datos.json> [--figure]');
  process.exit(2);
}

var spec;
try {
  spec = JSON.parse(fs.readFileSync(archivo, 'utf8'));
} catch (e) {
  console.error('No pude leer ' + archivo + ': ' + e.message);
  process.exit(2);
}

var tipos = { cascada: Fig.cascada };
var dibujar = tipos[spec.tipo];
if (!dibujar) {
  console.error('Tipo de figura desconocido: "' + spec.tipo + '". Disponibles: ' + Object.keys(tipos).join(', '));
  process.exit(2);
}

var svg;
try {
  svg = dibujar(spec);
} catch (e) {
  console.error('\n  ✗ ' + e.message + '\n');
  process.exit(1);
}

if (!conFigure) { console.log(svg); process.exit(0); }

var cap = spec.caption ? '\n  <figcaption>' + spec.caption + '</figcaption>' : '';
console.log(
  '<figure class="proyecto-media sub-figura sub-figura--bloques fig-animada">\n' +
  '  <div class="sub-figura-lienzo">' + svg + '</div>' + cap + '\n' +
  '</figure>'
);
