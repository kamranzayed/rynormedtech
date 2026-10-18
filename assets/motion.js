(() => {
  'use strict';
  const script = document.currentScript;
  const asset = name => new URL(`vendor/${name}`, script.src).href;
  const { gsap, ScrollTrigger, Lenis } = window;
  if (!gsap || !ScrollTrigger || !Lenis) return;
  gsap.registerPlugin(ScrollTrigger);

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const desktop = matchMedia('(min-width: 900px) and (pointer: fine)');
  const root = document.documentElement;
  const toggle = document.querySelector('[data-motion-toggle]');
  const hero = document.querySelector('[data-hero-motion]');
  let preference;
  try { preference = localStorage.getItem('rynor-motion'); } catch { /* Storage is optional. */ }
  let context, lenis, ticker, modalObserver, heroObserver, waves;
  let heroVisible = true;
  let webglSupport;
  let generation = 0;
  const loaders = new Map();
  const load = name => {
    if (!loaders.has(name)) loaders.set(name, new Promise((resolve, reject) => {
      const tag = document.createElement('script');
      tag.src = asset(name);
      tag.onload = resolve;
      tag.onerror = () => { loaders.delete(name); tag.remove(); reject(new Error(`Could not load ${name}`)); };
      document.head.append(tag);
    }));
    return loaders.get(name);
  };
  const destroyWaves = () => {
    if (waves) { waves.destroy(); waves = null; }
    if (hero) { hero.replaceChildren(); hero.dataset.state = 'static'; }
  };
  const supportsWebGL = () => {
    if (webglSupport !== undefined) return webglSupport;
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
      webglSupport = Boolean(gl);
      gl?.getExtension('WEBGL_lose_context')?.loseContext();
    } catch { webglSupport = false; }
    return webglSupport;
  };
  const startWaves = async id => {
    if (!hero || !heroVisible || !desktop.matches || document.hidden || navigator.connection?.saveData || !supportsWebGL()) return;
    try {
      await load('three-0.134.0.min.js');
      await load('vanta-waves-0.5.24.min.js');
      if (id !== generation || !heroVisible || reduced.matches || preference === 'off' || document.hidden || waves) return;
      waves = window.VANTA.WAVES({
        el: hero, THREE: window.THREE,
        mouseControls: false, touchControls: false, gyroControls: false,
        color: 0x4c93a8, shininess: 12, waveHeight: 6, waveSpeed: 0.28,
        zoom: 0.85, scale: 1.5, scaleMobile: 2, minHeight: 200, minWidth: 200
      });
      const canvas = hero.querySelector('canvas');
      if (!canvas) throw new Error('No WebGL canvas');
      canvas.setAttribute('aria-hidden', 'true');
      canvas.addEventListener('webglcontextlost', destroyWaves, { once: true });
      hero.dataset.state = 'animated';
    } catch { destroyWaves(); /* The original static background stays visible. */ }
  };
  const dispose = () => {
    generation++;
    modalObserver?.disconnect(); modalObserver = null;
    heroObserver?.disconnect(); heroObserver = null;
    if (ticker) { gsap.ticker.remove(ticker); ticker = null; }
    lenis?.destroy(); lenis = null;
    context?.revert(); context = null;
    destroyWaves();
    delete root.dataset.smoothScroll;
  };
  const configure = () => {
    dispose();
    const enabled = !reduced.matches && preference !== 'off';
    root.dataset.motion = enabled ? 'on' : 'off';
    if (toggle) {
      toggle.hidden = false;
      toggle.disabled = reduced.matches;
      toggle.setAttribute('aria-pressed', String(!enabled));
      toggle.textContent = reduced.matches ? 'Reduced motion enabled' : enabled ? 'Pause motion' : 'Enable motion';
    }
    if (!enabled) return;
    const id = generation;
    try {
      context = gsap.context(() => {
        const intro = document.querySelector('.hero-copy, .page-heading .container');
        if (intro) gsap.from(intro.children, { y: 16, opacity: 0, duration: 0.65, stagger: 0.09, ease: 'power2.out', clearProps: 'transform,opacity' });
        const figure = document.querySelector('.hero-figure');
        if (figure) gsap.from(figure, { opacity: 0, duration: 0.8, ease: 'power1.out', clearProps: 'opacity' });
        document.querySelectorAll('.section-top, .product-preview, .two-column > .copy-stack, .principle, .contact-band-inner > div').forEach(element => {
          gsap.from(element, { y: 18, opacity: 0, duration: 0.65, ease: 'power2.out', clearProps: 'transform,opacity', scrollTrigger: { trigger: element, start: 'top 94%', once: true } });
        });
      });
      if (desktop.matches) {
        lenis = new Lenis({ autoRaf: false, smoothWheel: true, syncTouch: false, anchors: false, lerp: 0.1, allowNestedScroll: true, prevent: node => Boolean(node.closest('dialog, [data-lenis-prevent]')) });
        lenis.on('scroll', ScrollTrigger.update);
        ticker = time => lenis?.raf(time * 1000);
        gsap.ticker.add(ticker);
        gsap.ticker.lagSmoothing(0);
        root.dataset.smoothScroll = 'lenis';
        const syncModal = () => document.hidden || document.querySelector('dialog[open]') ? lenis?.stop() : lenis?.start();
        modalObserver = new MutationObserver(syncModal);
        document.querySelectorAll('dialog').forEach(dialog => modalObserver.observe(dialog, { attributes: true, attributeFilter: ['open'] }));
        syncModal();
      }
      ScrollTrigger.refresh();
      if (hero && desktop.matches) {
        const bounds = hero.getBoundingClientRect();
        heroVisible = bounds.bottom > -120 && bounds.top < innerHeight + 120;
        if ('IntersectionObserver' in window) {
          heroObserver = new IntersectionObserver(entries => {
            if (id !== generation) return;
            heroVisible = entries[0].isIntersecting;
            if (!heroVisible) destroyWaves();
            else if (root.dataset.motion === 'on') startWaves(id);
          }, { rootMargin: '120px 0px' });
          heroObserver.observe(hero);
        }
      }
      startWaves(id);
    } catch {
      dispose();
      root.dataset.motion = 'unavailable';
      if (toggle) toggle.hidden = true;
    }
  };
  toggle?.addEventListener('click', () => {
    preference = root.dataset.motion === 'on' ? 'off' : 'on';
    try { localStorage.setItem('rynor-motion', preference); } catch { /* Session preference still works. */ }
    configure();
  });
  reduced.addEventListener('change', configure);
  desktop.addEventListener('change', configure);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { destroyWaves(); lenis?.stop(); }
    else if (root.dataset.motion === 'on') {
      if (!document.querySelector('dialog[open]')) lenis?.start();
      startWaves(generation);
    }
  });
  window.addEventListener('pagehide', dispose);
  window.addEventListener('pageshow', event => { if (event.persisted) configure(); });
  configure();
})();
