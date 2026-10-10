/* Original decorative food atmosphere. No external assets or dependencies. */
(() => {
  'use strict';
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  let enabled = !media.matches;
  const root = document.documentElement;
  const surfaces = new Set();
  const visible = new Set();
  const refresh = () => {
    root.classList.toggle('pf-motion-enabled', enabled && !document.hidden);
    let budget = 0;
    surfaces.forEach(el => el.classList.toggle('pf-motion-running', visible.has(el) && budget++ < 4));
    document.querySelectorAll('#pfMotionToggle').forEach(button => {
      button.textContent = enabled ? 'Pause motion' : 'Play motion';
      button.setAttribute('aria-pressed', String(enabled));
    });
    const status = document.getElementById('pfMotionStatus');
    if (status) status.textContent = enabled ? 'Gentle food atmosphere is on.' : media.matches ? 'Reduced motion respected. Preview only if you wish.' : 'Food atmosphere is paused.';
  };
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting}) => isIntersecting ? visible.add(target) : visible.delete(target));
    refresh();
  }, {threshold: .15}) : null;
  function register(el) {
    surfaces.add(el);
    if (observer) observer.observe(el); else visible.add(el);
  }
  function control() {
    let container = document.querySelector('.pf-motion-preview');
    if (!container && document.querySelector('.seo-recipe')) {
      container = document.createElement('div');
      container.className = 'pf-motion-preview';
      container.innerHTML = '<button type="button" id="pfMotionToggle" aria-pressed="false">Play motion</button><span id="pfMotionStatus" role="status" aria-live="polite"></span>';
      document.querySelector('.seo-recipe figure').after(container);
    }
    if (container) {
      container.hidden = false;
      container.querySelector('button').addEventListener('click', () => { enabled = !enabled; refresh(); });
    }
  }
  const kind = slug => /^(chicken-biryani|chicken-karahi|beef-nihari|haleem|halwa-puri|kashmiri-chai|doodh-patti-chai|masala-chai)$/.test(slug) ? 'steam'
    : /^(seekh-kabab|chapli-kabab|chicken-sajji|chicken-tikka)$/.test(slug) ? 'heat'
    : /^(mango-lassi|lassi|sweet-lassi|namkeen-lassi)$/.test(slug) ? 'fresh'
    : /^(jalebi|rice-kheer|gulab-jamun|ras-malai)$/.test(slug) ? 'light' : null;
  const ns = 'http://www.w3.org/2000/svg';
  function decorate(host, img, type) {
    if (!host || !img || !type) return;
    host.classList.add('pf-food-host');
    const layer = document.createElement('span');
    layer.className = 'pf-food-atmosphere pf-' + type;
    layer.setAttribute('aria-hidden', 'true');
    if (type === 'steam' || type === 'heat') {
      for (let i = 0; i < 3; i++) {
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', '0 0 80 150');
        svg.setAttribute('focusable', 'false');
        svg.classList.add('pf-wisp');
        const path = document.createElementNS(ns, 'path');
        path.setAttribute('d', 'M40 145 C8 113 72 95 39 66 C12 43 60 25 43 5');
        // Layered translucent strokes soften the edge without animated filters.
        [24, 17, 9].forEach((width, index) => {
          const mist = path.cloneNode();
          mist.style.strokeWidth = width;
          mist.style.strokeOpacity = [.045, .075, .13][index];
          svg.append(mist);
        });
        layer.append(svg);
      }
    } else layer.innerHTML = '<span class="pf-reflection"></span>';
    host.append(layer);
    const measure = () => {
      layer.style.top = img.offsetTop + 'px';
      layer.style.left = img.offsetLeft + 'px';
      layer.style.width = img.offsetWidth + 'px';
      layer.style.height = img.offsetHeight + 'px';
      layer.hidden = !img.naturalWidth || img.src.includes('unavailable');
    };
    img.addEventListener('load', measure);
    img.addEventListener('error', () => {layer.hidden = true;});
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(img);
    else window.addEventListener('resize', measure, {passive:true});
    measure(); register(layer);
  }
  document.querySelectorAll('.featured-card, .popular-recipe-card').forEach(card => {
    const slug = card.getAttribute('href').split('/').pop().replace('.html', '');
    decorate(card, card.querySelector('img'), kind(slug));
  });
  const picture = document.querySelector('.seo-recipe figure picture');
  if (picture) decorate(picture, picture.querySelector('img'), kind(location.pathname.split('/').pop().replace('.html', '')));
  document.querySelectorAll('.hero, .category-box:nth-child(-n+3), .featured-heading').forEach(register);
  control(); refresh();
  media.addEventListener('change', () => { enabled = !media.matches; refresh(); });
  document.addEventListener('visibilitychange', refresh);
})();
