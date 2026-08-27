/**
 * Revelado de figuras en las notas de análisis.
 *
 * Cada figura se dibuja una sola vez, cuando entra en pantalla, y queda
 * quieta en su estado final. Un bucle eterno compite con el texto en una
 * página que se lee, y no se puede pausar ni comparar.
 */
(function () {
  const figuras = document.querySelectorAll('.fig-animada');
  if (!figuras.length) return;

  const sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Sin IntersectionObserver o sin movimiento: estado final directo.
  if (sinMovimiento || !('IntersectionObserver' in window)) {
    figuras.forEach((f) => f.classList.add('revelado'));
    return;
  }

  // Las líneas necesitan su largo real para dibujarse; el navegador lo sabe.
  figuras.forEach((f) => {
    f.querySelectorAll('.an-linea').forEach((l) => {
      if (typeof l.getTotalLength === 'function') {
        l.style.setProperty('--largo', l.getTotalLength());
      }
    });
  });

  const observador = new IntersectionObserver(
    (entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('revelado');
        observador.unobserve(e.target); // una sola vez
      });
    },
    { threshold: 0.25, rootMargin: '0px 0px -8% 0px' }
  );

  figuras.forEach((f) => observador.observe(f));
})();
