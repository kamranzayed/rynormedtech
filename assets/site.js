(() => {
  'use strict';
  const email = 'syedkamran@rynormedtech.com';
  const menuButton = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('#primary-nav');
  const closeMenu = () => {
    if (!menuButton || !nav) return;
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open navigation');
    nav.classList.remove('is-open');
  };
  menuButton?.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav?.classList.contains('is-open')) {
      closeMenu();
      menuButton.focus();
    }
  });
  matchMedia('(min-width: 721px)').addEventListener('change', closeMenu);
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));

  const dialog = document.querySelector('#enquiry-dialog');
  let enquiryTrigger;
  const openEnquiry = (trigger) => {
    if (!dialog || typeof dialog.showModal !== 'function') {
      window.location.href = 'contact.html';
      return;
    }
    enquiryTrigger = trigger;
    const topic = dialog.querySelector('[name="topic"]');
    if (trigger.dataset.enquiry && [...topic.options].some(option => option.value === trigger.dataset.enquiry)) topic.value = trigger.dataset.enquiry;
    else topic.value = 'General enquiry';
    dialog.querySelector('[data-draft-status]').hidden = true;
    closeMenu();
    dialog.showModal();
    document.body.classList.add('dialog-open');
  };
  document.querySelectorAll('[data-enquiry]').forEach(trigger => trigger.addEventListener('click', event => {
    event.preventDefault();
    openEnquiry(trigger);
  }));
  dialog?.querySelector('[data-dialog-close]').addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog?.addEventListener('close', () => {
    document.body.classList.remove('dialog-open');
    enquiryTrigger?.focus();
  });
  dialog?.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const items = [...dialog.querySelectorAll('a[href],button:not([disabled]),input,select,textarea')].filter(item => item.getClientRects().length);
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  document.querySelectorAll('[data-email-form]').forEach(form => {
    const message = form.querySelector('[name="message"]');
    form.addEventListener('input', () => {
      message.setCustomValidity('');
      form.querySelector('[data-draft-status]').hidden = true;
    });
    form.addEventListener('submit', event => {
      event.preventDefault();
      message.setCustomValidity(message.value.trim() ? '' : 'Please enter a message before opening your email draft.');
      if (!form.reportValidity()) return;
      const fields = new FormData(form);
      const subject = `RYNOR Medtech — ${fields.get('topic')}`;
      const lines = [String(fields.get('message')).trim(), '', `Name: ${String(fields.get('name') || '').trim() || 'Not provided'}`, `Reply email: ${String(fields.get('email') || '').trim() || 'Use my sending address'}`];
      const href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
      const status = form.querySelector('[data-draft-status]');
      status.querySelector('a').href = href;
      status.hidden = false;
      window.open(href, '_blank', 'noopener,noreferrer');
    });
  });
  document.querySelectorAll('[data-copy-email]').forEach(button => button.addEventListener('click', async () => {
    const label = button.querySelector('span');
    try {
      await navigator.clipboard.writeText(email);
      label.textContent = 'Email address copied';
    } catch {
      label.textContent = 'Select the email address above to copy it';
    }
  }));

  const cards = [...document.querySelectorAll('[data-category]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const search = document.querySelector('#catalog-search');
  if (cards.length && filters.length) {
    let category = 'all';
    const normaliseSearch = value => value.toLowerCase().normalize('NFKC').replace(/[^\p{L}\p{N}]/gu, '');
    const applyFilters = () => {
      const query = normaliseSearch(search?.value || '');
      let count = 0;
      cards.forEach(card => {
        const show = (category === 'all' || card.dataset.category === category) && normaliseSearch(card.textContent).includes(query);
        card.hidden = !show;
        if (show) count++;
      });
      filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
      document.querySelector('[data-catalog-count]').textContent = `${count} planned product ${count === 1 ? 'category' : 'categories'}`;
      document.querySelector('[data-empty-state]').hidden = count !== 0;
    };
    filters.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.filter;
      applyFilters();
    }));
    search?.addEventListener('input', applyFilters);
    document.querySelector('[data-reset-filters]')?.addEventListener('click', () => {
      category = 'all';
      search.value = '';
      applyFilters();
      search.focus();
    });
    const initial = new URLSearchParams(window.location.search).get('category');
    if (filters.some(button => button.dataset.filter === initial)) category = initial;
    applyFilters();
  }
})();
