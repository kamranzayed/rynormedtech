// QA harness for the RYNOR website (not loaded by pages). Open a page with ?qa (forms then never send), load this file, run: await window.runQA()
window.runQA = async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const out = { page: location.pathname, width: innerWidth, pass: [], fail: [] };
  const ok = (cond, label, detail) => (cond ? out.pass : out.fail).push(detail ? `${label}: ${detail}` : label);
  const mobile = innerWidth < 900;
  const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && !el.closest('dialog:not([open]), [hidden], .mobile-menu:not(.is-open), .drawer:not(.open)'); };

  // Scroll through to trigger reveals and lazy images.
  for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * .8) { scrollTo(0, y); await wait(120); }
  await wait(900); scrollTo(0, 0); await wait(200);

  ok(document.documentElement.scrollWidth <= innerWidth + 1, 'No sideways scroll', `${document.documentElement.scrollWidth}px vs ${innerWidth}px`);
  const hiddenReveal = [...document.querySelectorAll('[data-reveal]')].filter(e => !e.classList.contains('in') && !e.closest('[hidden]'));
  ok(hiddenReveal.length === 0, 'All sections revealed on scroll', hiddenReveal.length ? `${hiddenReveal.length} still hidden` : '');
  const badImgs = [...document.images].filter(i => !i.closest('[hidden]') && i.complete && i.naturalWidth === 0).map(i => i.src.split('/').pop());
  ok(badImgs.length === 0, 'All images load', badImgs.join(', '));

  // Internal links resolve.
  const hrefs = [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => h && !/^(https?:|mailto:|tel:|#$)/.test(h)))];
  const broken = [];
  for (const h of hrefs) {
    const [path, hash] = h.split('#');
    if (path) { const r = await fetch(path, { method: 'HEAD' }); if (!r.ok) broken.push(h); }
    else if (hash && !document.getElementById(hash)) broken.push(h);
  }
  ok(broken.length === 0, `Internal links work (${hrefs.length})`, broken.join(', '));
  const anchorTargets = hrefs.filter(h => h.includes('#') && h.split('#')[0]).map(h => h.split('#'));
  for (const [p, hash] of anchorTargets) { const html = await (await fetch(p)).text(); if (!html.includes(`id="${hash}"`)) broken.push(`${p}#${hash}`); }
  ok(!anchorTargets.length || broken.length === 0, 'Cross-page section links land on a section', broken.join(', '));

  // Tap targets and text size on phones.
  if (mobile) {
    const small = [...document.querySelectorAll('a, button, input, select, summary')].filter(visible).filter(e => { const r = e.getBoundingClientRect(); return r.height < 40 && !e.closest('p, li, .footer-bottom, .chap, .tags, figcaption') && !e.closest('.scene-wrap'); });
    ok(small.length === 0, 'Tap targets at least 40px', small.slice(0, 6).map(e => `${(e.innerText || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 24)} ${Math.round(e.getBoundingClientRect().height)}px`).join(' · '));
    const tiny = [...document.querySelectorAll('main p, main li, main h3')].filter(visible).filter(e => parseFloat(getComputedStyle(e).fontSize) < 12);
    ok(tiny.length === 0, 'Body text at least 12px', tiny.slice(0, 4).map(e => e.innerText.slice(0, 20)).join(' · '));
    ok(visible(document.querySelector('.bottom-bar')), 'Mobile bottom bar shown');
    const tgl = document.querySelector('.header-inner .menu-toggle'); tgl.click(); await wait(500);
    ok(document.querySelector('.mobile-menu').classList.contains('is-open'), 'Mobile menu opens');
    document.querySelector('[data-close-menu]').click(); await wait(450);
    ok(!document.querySelector('.mobile-menu').classList.contains('is-open'), 'Mobile menu closes');
  } else {
    ok(visible(document.querySelector('.nav')), 'Desktop navigation shown');
    ok(!visible(document.querySelector('.bottom-bar')), 'Bottom bar hidden on desktop');
  }

  // Language switch.
  const navLink = document.querySelector('.nav [data-i18n="nav.supplies"]');
  document.querySelector('.lang button[data-lang="hi"]').click(); await wait(100);
  ok(navLink.textContent === 'सप्लाई' && document.documentElement.lang === 'hi', 'Hindi switch translates navigation');
  document.querySelector('.lang button[data-lang="en"]').click(); await wait(100);
  ok(navLink.textContent === 'Supplies' && document.documentElement.lang === 'en', 'English switch restores text');

  // Every form type on the page opens, validates and succeeds.
  const modal = document.getElementById('modal');
  const types = [...new Set([...document.querySelectorAll('[data-modal]')].map(b => b.dataset.modal))];
  for (const type of types) {
    const trigger = [...document.querySelectorAll(`[data-modal="${type}"]`)].find(visible) || document.querySelector(`[data-modal="${type}"]`);
    trigger.click(); await wait(150);
    const form = modal.querySelector('form');
    if (!modal.open || !form) { ok(false, `Form "${type}" opens`); continue; }
    form.querySelectorAll('input[required]').forEach(i => { if (i.type === 'checkbox') i.checked = true; else i.value = i.type === 'email' ? 'test@example.com' : 'Test'; });
    if (form.name && !form.name.value) form.name.value = 'Test';
    const consent = form.querySelector('[name=consent]');
    if (consent) { consent.checked = false; form.querySelector('button[type=submit]').click(); await wait(80); ok(!form.querySelector('.form-error').hidden && !modal.querySelector('.success'), `Form "${type}" requires consent`); consent.checked = true; }
    if (form.phone && form.email && !form.phone.value && !form.email.value) {
      form.querySelector('button[type=submit]').click(); await wait(80);
      ok(modal.querySelector('form') && !form.querySelector('.form-error').hidden, `Form "${type}" asks for phone or email`);
      form.phone.value = '+91 90000 00000';
    }
    form.querySelector('button[type=submit]').click(); await wait(150);
    ok(!!modal.querySelector('.success'), `Form "${type}" submits and thanks`);
    modal.close(); await wait(50);
  }
  ok(!modal.open, 'Forms close');

  // Page-specific features.
  if (document.querySelector('.aud')) {
    for (const tab of document.querySelectorAll('[data-tab]')) { tab.click(); await wait(40); ok(!document.querySelector(`[data-panel="${tab.dataset.tab}"]`).hidden, `Audience tab "${tab.dataset.tab}" shows its panel`); }
    document.querySelector('[data-tab="patient"]').click();
    ok(document.querySelectorAll('#homeProducts .prod').length === 3, 'Homepage shows 3 supply cards');
  }
  if (document.getElementById('catalog')) {
    const count = () => document.querySelectorAll('#catalog .item').length;
    ok(count() === window.RYNOR_PRODUCTS.length, `Catalogue shows all ${window.RYNOR_PRODUCTS.length} products`);
    document.querySelector('[data-cat="catheters"]').click(); await wait(50); ok(count() === 1, 'Category filter works');
    document.querySelector('[data-cat="all"]').click();
    const avail = document.getElementById('avail'); avail.value = 'planned'; avail.dispatchEvent(new Event('change')); await wait(50);
    ok(count() === window.RYNOR_PRODUCTS.filter(p => p.status === 'planned').length, 'Availability filter works');
    avail.value = 'all'; avail.dispatchEvent(new Event('change'));
    const search = document.getElementById('search'); search.value = 'transfer'; search.dispatchEvent(new Event('input')); await wait(50); ok(count() === 1, 'Search works');
    search.value = 'zzzz'; search.dispatchEvent(new Event('input')); await wait(50); ok(count() === 0 && !document.getElementById('empty').hidden, 'Empty state shows');
    document.getElementById('reset').click(); await wait(50); ok(count() === window.RYNOR_PRODUCTS.length, 'Reset shows everything');
    document.querySelector('#catalog .item').click(); await wait(600);
    ok(document.getElementById('drawer').classList.contains('open'), 'Product details drawer opens');
    document.querySelector('#drawer .close').click(); await wait(500);
    ok(!document.getElementById('drawer').classList.contains('open'), 'Product details drawer closes');
    history.replaceState(null, '', location.pathname);
  }
  if (document.getElementById('quizBody')) {
    for (let i = 0; i < 5; i++) { document.querySelector('#quizBody [data-i="0"]').click(); await wait(30); }
    ok(/PD may be worth discussing/.test(document.getElementById('quizBody').innerText), 'Quiz completes with a result');
    document.getElementById('quizAgain').click(); await wait(30);
    ok(/Question 1 of 5/i.test(document.getElementById('quizBody').innerText), 'Quiz restarts');
  }
  if (document.querySelector('[data-week-rows]')) {
    document.querySelector('[data-mode=pd]').click(); await wait(50);
    ok(document.querySelector('[data-stat=days]').textContent === '7' && document.querySelectorAll('[data-week-rows] .week-row').length === 7, 'PD week view shows 7 nights');
    document.querySelector('[data-mode=hd]').click(); await wait(50);
    ok(document.querySelector('[data-stat=visits]').textContent === '3', 'HD week view shows 3 centre visits');
  }
  if (window.__seek) {
    const play = document.getElementById('play'); window.__seek(41); await wait(60);
    ok(/Dwell/.test(document.getElementById('badgeText').textContent), 'Video seek lands on Dwell');
    const t0 = document.getElementById('time').textContent; if (play.getAttribute('aria-label') === 'Play') play.click(); await wait(1300);
    ok(document.getElementById('time').textContent !== t0, 'Video plays');
    play.click();
    document.querySelectorAll('#chapters button')[0].click(); await wait(60); play.click();
    ok(/Before/.test(document.getElementById('badgeText').textContent), 'Chapter buttons jump');
  }
  scrollTo(0, 0);
  return out;
};
