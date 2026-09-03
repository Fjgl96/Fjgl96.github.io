# fjgl96.github.io

Sitio personal de Francisco Guerrero López — finanzas corporativas y valuación.
Construido sobre la plantilla [iPortfolio](https://bootstrapmade.com/iportfolio-bootstrap-portfolio-websites-template/) de BootstrapMade.

El sitio se publica en **https://fjgl96.github.io/**. Todas las URL absolutas
(canonical, Open Graph, sitemap, JSON-LD) apuntan ahí.

## Publicar

Settings → Pages → Source: *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
El archivo `.nojekyll` evita que Jekyll procese los assets.

## Estructura

```
index.html                 Portada (una sola página, navegación por anclas)
proyectos/                 Una sub-página por proyecto
  lab-planeamiento.html    Laboratorio de Planeamiento Financiero
  portfolio-suite.html     En desarrollo
  panel-minero.html
  wacc-lab.html            Laboratorio de Costo de Capital (Good Finance)
  lab-montecarlo.html      Laboratorio de Trayectorias de Patrimonio (Monte Carlo, Atlas)
  lab-payoff.html          Laboratorio de Derivados
  cfagent.html
  atlas.html               Proyecto especial, fuera de la portada
agentes/                   Índice y ficha de cada flujo de automatización
  index.html
  reporte-ejecutivo.html
  investigacion-redaccion.html
  visualizacion-animada.html
  briefs-visuales.html
  tutoria-cfa.html
research/
  banks-fintechs.html      El modelo del paper, con sus diagramas
analisis/                  Notas de análisis (borradores no indexados)
  bvn.html                 Buenaventura: empresa pública, fuentes abiertas (SMV, Yahoo, Damodaran)
clases/                    Material didáctico (borradores no indexados)
  proyecto-inmobiliario.html  Proyecto sintético: ningún dato corresponde a un cliente real
  modelo-proyecto-norte.py    Modelo mensual que genera las cifras de la clase
figuras/                   Datos JSON para las figuras animadas
scripts/figura.js          Generador de las figuras SVG
404.html · robots.txt · sitemap.xml
assets/
  css/style.css            CSS de iPortfolio (sin modificar)
  css/custom.css           Estilos propios + correcciones de accesibilidad
  css/subpagina.css        Estilos de las sub-páginas de proyecto
  css/analisis.css         Estilos de notas de análisis y clases
  js/main.js               JS de la plantilla (respeta prefers-reduced-motion)
  js/analisis.js           Animación de figuras en notas y clases
  js/fig-engine.js         Motor de figuras
  img/proyectos/           Capturas reales y diagramas SVG
  img/research/            Diagramas del paper (círculo de Salop, regiones)
  img/og-image.jpg         Imagen para compartir (1200 × 630)
  docs/cv-francisco-guerrero.pdf  CV en PDF (botón de descarga de la sección CV)
  demo/reporte-ejecutivo/  Demo del flujo de reporte sobre un caso sintético
  vendor/                  Bootstrap (solo CSS), Bootstrap Icons, AOS, Typed.js, PureCounter
```

Secciones: Inicio · Perfil · Proyectos · Automatización financiera · Research · CV · Contacto.

La portada funciona como índice: muestra siete proyectos y cinco flujos, y el detalle vive en las sub-páginas.

## Criterio de datos

- `analisis/` trabaja solo con **empresas públicas y fuentes abiertas** (SMV, Yahoo Finance, Damodaran), con disclaimer de no recomendación y declaración de conflictos.
- `clases/` y `assets/demo/` trabajan solo con **casos sintéticos**: ninguna cifra corresponde a un cliente o proyecto real.
- No se publican nombres de clientes privados ni datos explícitos de empresas no listadas.

## Qué falta completar

| Pendiente | Dónde | Nota |
|---|---|---|
| CV en PDF | `assets/docs/cv-francisco-guerrero.pdf` | El botón de descarga ya apunta ahí; copiar el PDF con ese nombre exacto |
| Fecha de inicio en Good Finance | Sección CV | Hoy dice «En paralelo · actualidad»; añade el mes y año cuando lo tengas |

Después de cada publicación, verifica la tarjeta social en el
[Post Inspector de LinkedIn](https://www.linkedin.com/post-inspector/): cachea las previsualizaciones ~7 días.
Tras editar páginas, actualiza el `lastmod` correspondiente en `sitemap.xml`.

## Desarrollo local

```bash
python -m http.server 8000
# http://127.0.0.1:8000
```

## Créditos

Plantilla iPortfolio de [BootstrapMade](https://bootstrapmade.com/), bajo su
[licencia gratuita](https://bootstrapmade.com/license/), que exige mantener el enlace de atribución en el pie.
