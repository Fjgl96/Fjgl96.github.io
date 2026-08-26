# fguerrero.github.io

Sitio personal de Francisco Guerrero — finanzas corporativas y agentes de IA.
Página única construida sobre la plantilla [iPortfolio](https://bootstrapmade.com/iportfolio-bootstrap-portfolio-websites-template/) de BootstrapMade.

## Publicar en GitHub Pages

En el repositorio: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
rama `main` (o la que uses), carpeta `/ (root)`. El sitio queda en `https://fjgl96.github.io/`.

El archivo `.nojekyll` está incluido para que GitHub Pages sirva los assets tal cual, sin procesarlos con Jekyll.

## Qué falta reemplazar

Todo lo marcado abajo son **placeholders**. Busca `PLACEHOLDER` en `index.html` para encontrarlos en contexto.

### Imágenes

| Archivo | Uso | Tamaño sugerido |
|---|---|---|
| `assets/img/profile-img.svg` | Foto del sidebar (se muestra circular) | 400 × 400 px |
| `assets/img/about-img.svg` | Foto de la sección Perfil | 600 × 800 px (3:4) |
| `assets/img/hero-bg.svg` | Fondo de la portada | 1920 × 1080 px |
| `assets/img/portfolio/portfolio-1..9.svg` | Capturas de los entregables | 800 × 600 px (4:3) |
| `assets/img/apple-touch-icon.png` | Ícono para iOS (opcional) | 180 × 180 px |

Si subes `.jpg` o `.png` en lugar de `.svg`, acuérdate de cambiar la extensión en `index.html`.
Para el fondo de portada, la regla está en `assets/css/custom.css` (al final del archivo).

### Enlaces y datos

- **Redes del sidebar** — los `href="#"` de LinkedIn y GitHub en `index.html` (línea ~60).
- **LinkedIn en Contacto** — el texto `[tu perfil de LinkedIn]`.
- **Enlaces "Ver más" del portafolio** — los `href="#"` de cada proyecto.
- **Formulario de contacto** — apunta a `https://formspree.io/f/TU_ID`. Crea una cuenta gratis en
  [formspree.io](https://formspree.io), copia tu endpoint y reemplaza `TU_ID`.
  GitHub Pages no ejecuta PHP, por eso no se usa el formulario original de la plantilla.

### CV

La sección **CV** tiene la estructura armada pero los datos entre corchetes son placeholders:
formación, experiencia, certificaciones e idiomas. Reemplaza cada `[...]` con tus datos reales.
También puedes subir tu CV en PDF a `assets/docs/cv-francisco-guerrero.pdf` — el botón de descarga ya apunta ahí.

## Estructura

```
index.html                 Página completa (una sola página, navegación por anclas)
assets/
  css/style.css            CSS de la plantilla iPortfolio (sin modificar)
  css/custom.css           Estilos propios: panel de agentes, hero, portafolio, botón de CV
  js/main.js               JS de la plantilla (se quitaron los bloques de Swiper, no se usa)
  img/                     Imágenes y placeholders
  docs/                    CV en PDF
  vendor/                  Librerías: Bootstrap, AOS, Boxicons, Bootstrap Icons,
                           GLightbox, Isotope, Typed.js, Waypoints, PureCounter
```

Las secciones son: Inicio, Perfil, **Panel de Agentes**, Portafolio, CV y Contacto.
La plantilla original trae una sección de testimonios; se eliminó junto con la librería Swiper
que la movía, porque por ahora no hay recomendaciones que mostrar.

## Desarrollo local

```bash
python3 -m http.server 8000
# abrir http://127.0.0.1:8000
```

## Créditos

Plantilla iPortfolio de [BootstrapMade](https://bootstrapmade.com/), usada bajo su
[licencia gratuita](https://bootstrapmade.com/license/), que exige mantener el enlace de
atribución en el pie de página.
