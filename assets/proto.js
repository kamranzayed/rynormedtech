/* RYNOR site kit: shared header, footer, mobile bar, WhatsApp, smart forms, language switch, reveals. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  if (!document.querySelector('link[rel=icon]')) document.head.insertAdjacentHTML('beforeend', '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">');
  const body = document.body;
  const page = body.dataset.page || '';
  const WHATSAPP = ''; // Add the business WhatsApp number (country code, digits only, e.g. '919XXXXXXXXX') to show WhatsApp buttons.
  const FORM_ENDPOINT = 'https://formspree.io/f/mbgdblpw';
  const TEST_MODE = /[?&]qa\b/.test(location.search); // QA runs never send real enquiries.
  const EMAIL = 'syedkamran@rynormedtech.com';
  const waLink = text => `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(text)}`;
  const icon = {
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    wa: '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3a.5.5 0 0 0 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .2-1.2c-.1-.1-.3-.2-.6-.3z"/></svg>',
    home: '<svg viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
    box: '<svg viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8l-9-5-9 5 9 5 9-5zM3 8v8l9 5 9-5V8M12 13v8"/></svg>',
    play: '<svg viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l6-3.5z"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="#06264b" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="#06264b" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    tick: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
  };
  window.RYNOR = { icon, waLink, EMAIL, hasWhatsApp: Boolean(WHATSAPP) };

  // --- Language: English / Hindi ---
  // Translates by matching the English text of each paragraph, heading, button or label against assets/i18n-hi.js,
  // keeping links and markup inside mixed elements intact. A MutationObserver translates text that appears later
  // (forms, video captions, quiz steps, product details), and switching back restores the original English.
  const INLINE = new Set(['B', 'STRONG', 'EM', 'I', 'BR', 'SPAN']);
  const SKIP = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT']);
  const norm = s => s.replace(/\s+/g, ' ').trim();
  const inlineOnly = el => [...el.children].every(c => INLINE.has(c.nodeName.toUpperCase()) && inlineOnly(c));
  const textOf = el => { let out = ''; el.childNodes.forEach(n => { if (n.nodeType === 3) out += n.nodeValue; else if (n.nodeName.toUpperCase() === 'BR') out += ' '; else if (n.nodeType === 1) out += textOf(n); }); return out; };
  const lookup = key => {
    const dict = window.RYNOR_HI || {};
    if (Object.prototype.hasOwnProperty.call(dict, key)) return dict[key];
    for (const [re, fn] of window.RYNOR_HI_PATTERNS || []) { const m = key.match(re); if (m) return fn(m); }
    return null;
  };
  const changed = new Set();
  const setHTML = (el, html) => { if (el instanceof SVGElement) el.textContent = html.replace(/<[^>]+>/g, ''); else el.innerHTML = html; };
  const translate = root => {
    if (!root || root.nodeType !== 1 || SKIP.has(root.nodeName.toUpperCase()) || root.closest('.lang, [data-no-translate]')) return;
    ['placeholder', 'aria-label'].forEach(attr => [root, ...root.querySelectorAll(`[${attr}]`)].forEach(el => {
      if (!el.hasAttribute(attr)) return;
      const hi = lookup(norm(el.getAttribute(attr)));
      if (hi !== null) { (el.__enAttr ||= {})[attr] = el.getAttribute(attr); el.setAttribute(attr, hi.replace(/<[^>]+>/g, '')); changed.add(el); }
    }));
    const walk = el => {
      if (SKIP.has(el.nodeName.toUpperCase()) || el.matches('.lang, [data-no-translate]')) return;
      if (inlineOnly(el)) {
        const hi = lookup(norm(textOf(el)));
        // Replace the whole element only if it has no child elements, or the translation supplies its own markup;
        // otherwise translate the text pieces inside, so elements scripts rely on (ids, counters) survive.
        if (hi !== null && (!el.children.length || /<[a-z]/i.test(hi))) { el.__en = el.innerHTML; setHTML(el, hi); changed.add(el); return; }
      }
      el.childNodes.forEach(n => {
        if (n.nodeType === 1) walk(n);
        else if (n.nodeType === 3 && /[a-z]/i.test(n.nodeValue)) {
          const hi = lookup(norm(n.nodeValue));
          if (hi !== null) { n.__en = n.nodeValue; n.nodeValue = n.nodeValue.match(/^\s*/)[0] + hi.replace(/<[^>]+>/g, '') + n.nodeValue.match(/\s*$/)[0]; changed.add(n); }
        }
      });
    };
    walk(root);
  };
  const revert = () => {
    changed.forEach(x => {
      if (x.nodeType === 3) { if (x.__en !== undefined) x.nodeValue = x.__en; }
      else { if (x.__en !== undefined) x.innerHTML = x.__en; if (x.__enAttr) Object.entries(x.__enAttr).forEach(([a, v]) => x.setAttribute(a, v)); }
      delete x.__en; delete x.__enAttr;
    });
    changed.clear();
  };
  let observer;
  const watch = on => {
    observer?.disconnect(); observer = null;
    if (!on) return;
    observer = new MutationObserver(records => {
      observer.disconnect();
      const targets = new Set();
      records.forEach(r => {
        if (r.type === 'characterData') targets.add(r.target.parentElement);
        if (r.type === 'attributes') targets.add(r.target);
        r.addedNodes.forEach(n => targets.add(n.nodeType === 1 ? n : n.parentElement));
      });
      targets.forEach(t => t && t.isConnected && translate(t));
      observer.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['aria-label', 'placeholder'] });
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['aria-label', 'placeholder'] });
  };
  const I18N_V = '4a926bad95';
  let dictLoading;
  const loadDict = () => dictLoading ||= window.RYNOR_HI ? Promise.resolve() : new Promise(resolve => {
    const tag = document.createElement('script');
    tag.src = new URL('i18n-hi.js?v=' + I18N_V, document.currentScript?.src || document.querySelector('script[src*="assets/proto.js"]').src).href;
    tag.onload = resolve; tag.onerror = resolve;
    document.head.append(tag);
  });
  const getLang = () => { try { return localStorage.getItem('rynor-lang') || 'en'; } catch { return 'en'; } };
  const applyLang = async lang => {
    document.querySelectorAll('.lang button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
    try { localStorage.setItem('rynor-lang', lang); } catch { /* optional */ }
    if (lang === 'hi') {
      await loadDict();
      document.documentElement.lang = 'hi';
      translate(document.body);
      watch(true);
    } else {
      watch(false);
      revert();
      document.documentElement.lang = 'en';
    }
  };
  window.RYNOR.applyLang = applyLang;

  // --- Shell: header, mobile menu, floating actions, bottom bar, footer, modal ---
  const NAV = [['index.html', 'nav.home', 'Home'], ['supplies.html', 'nav.supplies', 'Supplies'], ['pd-at-home.html', 'nav.pd', 'PD at Home'], ['doctors.html', 'nav.doctors', 'For doctors'], ['investors.html', 'nav.investors', 'For investors'], ['about.html', 'nav.about', 'About']];
  const links = NAV.map(([href, key, label]) => `<a href="${href}" data-i18n="${key}" ${page === href.replace('.html', '') ? 'aria-current="page"' : ''}>${label}</a>`).join('');
  const lang = '<div class="lang" role="group" aria-label="Language"><button type="button" data-lang="en">EN</button><button type="button" data-lang="hi">हिं</button></div>';
  const header = `<header class="site-header"><div class="container header-inner">
    <a class="brand" href="index.html"><img src="assets/brand/rynor-logo.svg" alt="RYNOR Medtech"></a>
    <nav class="nav" aria-label="Primary">${links}</nav>${lang}
    <button class="btn small" type="button" data-modal="contact" data-i18n="nav.contact">Contact</button>
    <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false">${icon.menu}</button>
  </div></header>
  <div class="mobile-menu" aria-hidden="true"><div class="mobile-menu-top"><a class="brand" href="index.html"><img src="assets/brand/rynor-logo.svg" alt="RYNOR Medtech"></a><button class="menu-toggle" style="display:inline-flex" type="button" aria-label="Close menu" data-close-menu>${icon.close}</button></div>
    <nav aria-label="Mobile">${links}</nav>${lang}
    <div class="actions" style="margin-top:24px">${WHATSAPP ? `<a class="btn wa" href="${waLink('Hello RYNOR, I would like to know more.')}" target="_blank" rel="noopener">${icon.wa.replace('<svg', '<svg fill="#fff"')}<span data-i18n="cta.wa">Chat on WhatsApp</span></a>` : ''}<button class="btn light" type="button" data-modal="contact" data-i18n="nav.contact">Contact</button></div>
  </div>`;
  const cta = { supplies: ['quote', 'cta.quote', 'Request a quote'], 'pd-at-home': ['interest', 'cta.interest', 'Register interest'], doctors: ['trial', '', 'Collaborate with us'], investors: ['deck', '', 'Request investor deck'] }[page] || ['contact', 'cta.contact', 'Talk to RYNOR'];
  const shellBottom = `
  <div class="float"><button class="cta-pill" type="button" data-modal="${cta[0]}" ${cta[1] ? `data-i18n="${cta[1]}"` : ''}>${cta[2]}</button>${WHATSAPP ? `<a class="wa-fab" href="${waLink('Hello RYNOR, I would like to know more.')}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">${icon.wa}</a>` : ''}</div>
  <nav class="bottom-bar" aria-label="Quick links">
    <a href="index.html" ${page === 'index' ? 'aria-current="page"' : ''}>${icon.home}<span data-i18n="bar.home">Home</span></a>
    <a href="supplies.html" ${page === 'supplies' ? 'aria-current="page"' : ''}>${icon.box}<span data-i18n="bar.supplies">Supplies</span></a>
    <a href="pd-at-home.html#apd" ${page === 'pd-at-home' ? 'aria-current="page"' : ''}>${icon.play}<span data-i18n="bar.video">PD video</span></a>
    ${WHATSAPP ? `<a class="wa" href="${waLink('Hello RYNOR, I would like to know more.')}" target="_blank" rel="noopener">${icon.wa.replace('<svg', '<svg style="fill:#1a8d5f;stroke:none"')}<span data-i18n="bar.wa">WhatsApp</span></a>` : `<a href="index.html?contact" data-modal="contact"><svg viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4z"/></svg><span data-i18n="nav.contact">Contact</span></a>`}
  </nav>
  <footer class="site-footer"><div class="container">
    <div class="footer-grid">
      <div><span class="footer-brand"><img src="assets/brand/rynor-logo.svg" alt="RYNOR Medtech"></span><p style="font-size:14px;color:#b7c9d8;max-width:300px">An Indian company developing an automated peritoneal dialysis machine and a complete PD supply range.</p></div>
      <div><h4>Explore</h4><a href="index.html#machine">Our machine</a><a href="supplies.html">Supplies</a><a href="pd-at-home.html">PD at home</a><a href="about.html">About RYNOR</a></div>
      <div><h4>Partners</h4><a href="doctors.html">For doctors</a><a href="investors.html">For investors</a><a href="supplies.html#distributors">Distributors</a><a href="privacy.html">Privacy notice</a></div>
      <div><h4 data-i18n="foot.updates">Get development updates</h4><p style="font-size:13.5px;color:#b7c9d8">Occasional, verified progress news. No spam.</p><form class="signup" data-signup><input type="email" required placeholder="Your email" aria-label="Your email"><button class="btn teal small" type="submit">Join</button></form><a href="mailto:${EMAIL}" style="margin-top:14px">${EMAIL}</a></div>
    </div>
    <div class="footer-bottom"><span>© 2026 RYNOR Medtech · <a href="privacy.html" style="display:inline;padding:0;color:inherit;text-decoration:underline">Privacy</a></span><span>The RYNOR APD machine is in development and not for sale. General information, not medical advice.</span></div>
  </div></footer>
  <dialog class="modal" id="modal" aria-labelledby="modal-title"></dialog>
  <div class="toast" id="toast" role="status"></div>
  <svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="waveGrad" x1="0" x2="1"><stop offset="0" stop-color="#6fd6e8" stop-opacity="0"/><stop offset=".5" stop-color="#6fd6e8"/><stop offset="1" stop-color="#007a93" stop-opacity="0"/></linearGradient></defs></svg>`;
  body.insertAdjacentHTML('afterbegin', header);
  body.insertAdjacentHTML('beforeend', shellBottom);

  const siteHeader = document.querySelector('.site-header');
  const onScroll = () => siteHeader.classList.toggle('is-scrolled', scrollY > 10);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const menu = document.querySelector('.mobile-menu'), toggle = document.querySelector('.header-inner .menu-toggle');
  const setMenu = open => { menu.classList.toggle('is-open', open); menu.setAttribute('aria-hidden', String(!open)); toggle.setAttribute('aria-expanded', String(open)); body.style.overflow = open ? 'hidden' : ''; };
  toggle.addEventListener('click', () => setMenu(true));
  menu.querySelector('[data-close-menu]').addEventListener('click', () => setMenu(false));
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', () => applyLang(b.dataset.lang)));

  const toast = msg => { const t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toast.timer); toast.timer = setTimeout(() => t.classList.remove('show'), 2600); };
  window.RYNOR.toast = toast;
  document.querySelector('[data-signup]').addEventListener('submit', async e => {
    e.preventDefault();
    const email = e.target.querySelector('input').value;
    try { await send({ form_type: 'Development updates sign-up', email, _subject: '[RYNOR website] Updates sign-up' }); e.target.reset(); toast('Thanks! You’re on the update list.'); }
    catch { toast(`Sorry, that didn’t send. Please email ${EMAIL}.`); }
  });

  // Sends to the owner's Formspree form. Test runs (?qa) resolve without sending.
  async function send(payload) {
    if (TEST_MODE) return;
    const res = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) throw new Error('Form service error');
  }

  // --- Smart forms: one dialog, shaped by purpose ---
  const F = {
    name: '<div class="field"><label>Your name</label><input name="name" autocomplete="name" required></div>',
    contactRow: '<div class="field-row"><div class="field"><label>Phone / WhatsApp</label><input name="phone" type="tel" autocomplete="tel" placeholder="+91"></div><div class="field"><label>Email</label><input name="email" type="email" autocomplete="email"></div></div>',
    city: '<div class="field"><label>City <span style="font-weight:400;color:#566477">(optional)</span></label><input name="city" autocomplete="address-level2"></div>',
    message: '<div class="field"><label>Message <span style="font-weight:400;color:#566477">(optional)</span></label><textarea name="message"></textarea></div>',
    product: p => `<div class="field"><label>Product</label><input name="product" value="${p || ''}" ${p ? 'readonly' : ''}></div>`
  };
  const MODALS = {
    contact: ['Talk to RYNOR', 'Tell us who you are and we will route your message to the right person.', () => `<div class="field"><label>I am a…</label><select name="role"><option>Patient or family member</option><option>Doctor or PD professional</option><option>Investor</option><option>Distributor or hospital buyer</option><option>Other</option></select></div>${F.name}${F.contactRow}${F.message}`, 'Send message'],
    notify: ['Notify me when available', 'We’ll let you know as soon as this product can be ordered.', p => `${F.product(p)}${F.name}${F.contactRow}${F.city}`, 'Notify me'],
    quote: ['Request a quote', 'Share what you need and our team will reply with availability, pack details and pricing.', p => `<div class="field"><label>Organisation</label><input name="org" placeholder="Hospital, clinic or distributor"></div>${F.product(p)}<div class="field-row"><div class="field"><label>Quantity</label><input name="qty" type="number" min="1" value="100"></div><div class="field"><label>Unit</label><select name="unit"><option>Units</option><option>Boxes</option><option>Cartons</option></select></div></div>${F.name}${F.contactRow}${F.city}`, 'Request quote'],
    interest: ['Register your interest', 'For patients and families exploring PD at home. This is not a treatment booking.', () => `<div class="field"><label>I am</label><select name="who"><option>A patient</option><option>A family member or caregiver</option></select></div>${F.name}${F.contactRow}${F.city}<div class="field"><label>Preferred language</label><select name="lang"><option>English</option><option>हिंदी</option><option>Telugu</option><option>Tamil</option><option>Other</option></select></div>`, 'Register interest'],
    trial: ['Clinical collaboration', 'Interested in trial participation, feedback sessions or future evaluation? Tell us about your centre.', () => `${F.name}<div class="field-row"><div class="field"><label>Role</label><select name="role"><option>Nephrologist</option><option>PD nurse</option><option>Hospital administrator</option><option>Other</option></select></div><div class="field"><label>Hospital / centre</label><input name="centre"></div></div>${F.contactRow}${F.city}<div class="field"><label>Interested in</label><select name="interest"><option>Clinical trial site</option><option>Product feedback</option><option>Training &amp; education</option><option>Something else</option></select></div>`, 'Send interest'],
    deck: ['Request the investor deck', 'We share our deck personally after a short introduction.', () => `${F.name}<div class="field"><label>Fund or organisation</label><input name="org"></div>${F.contactRow}${F.message}`, 'Request deck'],
    brochure: ['Get the product brochure', 'The brochure is being prepared. Leave your email and we’ll send it when ready.', () => `${F.name}<div class="field"><label>Email</label><input name="email" type="email" required></div><div class="field"><label>Role</label><select name="role"><option>Doctor</option><option>PD nurse</option><option>Hospital buyer</option><option>Distributor</option><option>Other</option></select></div>`, 'Send me the brochure'],
    distributor: ['Become a distribution partner', 'Tell us about your company and the regions you cover.', () => `<div class="field"><label>Company</label><input name="company" required></div><div class="field"><label>States / regions covered</label><input name="regions"></div>${F.name}${F.contactRow}${F.message}`, 'Send enquiry']
  };
  const modal = document.getElementById('modal');
  const openModal = (type, product) => {
    const [title, sub, fields, submit] = MODALS[type] || MODALS.contact;
    modal.innerHTML = `<div class="modal-head"><div><h3 id="modal-title">${title}</h3><p>${sub}</p></div><button class="modal-close" type="button" aria-label="Close">×</button></div>
      <form novalidate>${fields(product)}<label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I agree that RYNOR may use these details to contact me, as described in the <a href="privacy.html" target="_blank">privacy notice</a>.</span></label><div class="honeypot" aria-hidden="true"><label>Leave empty<input name="_gotcha" tabindex="-1" autocomplete="off"></label></div><div class="form-error" role="alert" hidden></div><button class="btn" type="submit">${submit}${icon.arrow}</button><p class="form-note">One way to reach you is enough. Sent to the RYNOR team via <a href="https://formspree.io/legal/privacy-policy/" target="_blank" rel="noopener">Formspree</a>. Please don’t share medical records.</p></form>`;
    modal.querySelector('.modal-close').onclick = () => modal.close();
    modal.querySelector('form').onsubmit = async e => {
      e.preventDefault();
      const f = e.target, error = f.querySelector('.form-error'), button = f.querySelector('button[type=submit]');
      const fail = msg => { error.innerHTML = msg; error.hidden = false; };
      error.hidden = true;
      const missing = [...f.querySelectorAll('[required]')].find(i => i.type === 'checkbox' ? !i.checked : !i.value.trim());
      if (missing) { missing.focus(); fail(missing.type === 'checkbox' ? 'Please tick the consent box so we can contact you.' : 'Please fill in the highlighted field.'); return; }
      if (f.email && f.email.value && !f.email.checkValidity()) { f.email.focus(); fail('Please check your email address.'); return; }
      if (f.phone && f.email && !f.phone.value.trim() && !f.email.value.trim()) { f.phone.focus(); fail('Please add a phone number or email, so we can reply.'); return; }
      const data = Object.fromEntries(new FormData(f));
      if (data._gotcha) return;
      button.disabled = true;
      try {
        await send({ ...data, form_type: title, page: location.pathname, _subject: `[RYNOR website] ${title}${product ? ' · ' + product : ''}` });
        modal.innerHTML = `<div class="success"><div class="tick">${icon.tick}</div><h3 style="font-size:24px">Thank you!</h3><p style="margin-top:8px">Your message reached the RYNOR team. We’ll get back to you soon.</p><button class="btn light" type="button" style="margin-top:22px">Close</button></div>`;
        modal.querySelector('button').onclick = () => modal.close();
      } catch {
        button.disabled = false;
        fail(`Sorry, your message didn’t send. Your details are still here, so please try again, or email <a href="mailto:${EMAIL}">${EMAIL}</a>.`);
      }
    };
    modal.showModal();
  };
  modal.addEventListener('click', e => { if (e.target === modal) modal.close(); });
  document.addEventListener('click', e => { const t = e.target.closest('[data-modal]'); if (!t) return; e.preventDefault(); openModal(t.dataset.modal, t.dataset.product); });
  window.RYNOR.openModal = openModal;
  if (/[?&]contact\b/.test(location.search)) addEventListener('DOMContentLoaded', () => openModal('contact'));

  // --- Reveal on scroll, with gentle stagger inside [data-stagger] ---
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveal = () => {
    const els = document.querySelectorAll('[data-reveal]:not(.in)');
    if (reduced || !('IntersectionObserver' in window)) { els.forEach(el => el.classList.add('in')); return; }
    const io = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); } }), { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('[data-stagger]').forEach(group => [...group.querySelectorAll(':scope > [data-reveal]')].forEach((el, i) => { el.style.transitionDelay = `${i * 90}ms`; }));
    els.forEach(el => io.observe(el));
  };
  // Backup for browsers that delay IntersectionObserver: reveal anything already scrolled into or past view.
  const sweep = () => document.querySelectorAll('[data-reveal]:not(.in)').forEach(el => { if (el.getBoundingClientRect().top < innerHeight * .95) el.classList.add('in'); });
  addEventListener('scroll', sweep, { passive: true });
  window.RYNOR.reveal = reveal;
  addEventListener('DOMContentLoaded', () => { reveal(); applyLang(getLang()); setTimeout(sweep, 1200); });
})();
