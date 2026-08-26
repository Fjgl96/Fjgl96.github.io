# fguerrero.github.io

Sitio personal de Francisco Guerrero López — planeamiento financiero, control de gestión y agentes de IA.
Construido sobre la plantilla [iPortfolio](https://bootstrapmade.com/iportfolio-bootstrap-portfolio-websites-template/) de BootstrapMade.

El sitio se publica en **https://fjgl96.github.io/**. Todas las URL absolutas
(canonical, Open Graph, sitemap, JSON-LD) apuntan ahí.

## Publicar

Settings → Pages → Source: *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
El archivo `.nojekyll` evita que Jekyll procese los assets.

## Estructura

```
index.html                 Portada (una sola página, navegación por anclas)
proyectos/                 Una sub-página por proyecto, con diagrama de bloques
  panel-minero.html
  wacc-lab.html
  atlas.html
  lab-montecarlo.html
  lab-payoff.html
  cfagent.html
research/
  banks-fintechs.html      El modelo del paper, con sus diagramas
404.html · robots.txt · sitemap.xml
assets/
  css/style.css            CSS de iPortfolio (sin modificar)
  css/custom.css           Estilos propios + correcciones de accesibilidad
  css/subpagina.css        Estilos de las sub-páginas de proyecto
  js/main.js               JS de la plantilla (sin Swiper ni Isotope; respeta prefers-reduced-motion)
  img/proyectos/           Capturas reales y diagramas SVG
  img/research/            Diagramas del paper (círculo de Salop, regiones)
  docs/                    CV en PDF
  vendor/                  Bootstrap, AOS, Boxicons, Bootstrap Icons, GLightbox, Typed.js,
                           Waypoints, PureCounter
```

Secciones: Inicio · Perfil · Proyectos · Panel de agentes · Research · CV · Contacto.

## Qué falta completar

Busca `PLACEHOLDER` en `index.html` para ubicarlos en contexto.

| Pendiente | Dónde | Nota |
|---|---|---|
| Foto de perfil | `assets/img/profile-img.svg` | 400 × 400 px |
| Foto de la sección Perfil | `assets/img/about-img.svg` | 600 × 800 px (3:4) |
| Fondo de portada | `assets/img/hero-bg.svg` | 1920 × 1080 px; la regla está en `custom.css` |
| **Imagen para compartir** | `assets/img/og-image.jpg` | **1200 × 630 px, JPG, < 300 KB.** Sin ella, LinkedIn y WhatsApp muestran una tarjeta gris |
| Rol en Good Finance | Sección CV | Falta confirmar cargo y fecha de inicio |
| CV en PDF | `assets/docs/cv-francisco-guerrero.pdf` | El botón de descarga ya apunta ahí |
| Ícono para iOS | `assets/img/apple-touch-icon.png` | 180 × 180 px, opcional |

Después de subir el `og-image.jpg`, fuerza el re-escaneo en el
[Post Inspector de LinkedIn](https://www.linkedin.com/post-inspector/): cachea las previsualizaciones ~7 días.

## Desarrollo local

```bash
python3 -m http.server 8000
# http://127.0.0.1:8000
```

## Créditos

Plantilla iPortfolio de [BootstrapMade](https://bootstrapmade.com/), bajo su
[licencia gratuita](https://bootstrapmade.com/license/), que exige mantener el enlace de atribución en el pie.
