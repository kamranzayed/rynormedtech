# RYNOR Medtech website

A responsive, static website for RYNOR Medtech, served by GitHub Pages from `main`. RYNOR is an Indian company developing an automated peritoneal dialysis (APD) machine and a PD supply range. The APD machine is preparing for clinical trials and is not for sale. Each supply shows its own availability status.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Home: interactive 3D machine, "I am a…" audience switcher, PD video teaser, supplies preview, road ahead |
| `supplies.html` | Supply catalogue with category/availability filters, search, product details panel, Notify me and Request a quote |
| `pd-at-home.html` | Patient education: the animated PD journey video (before PD → doctor eligibility → catheter → healing & training → overnight APD cycles), journey and exchange cards, night timeline, "Is PD right for me?" check, FAQ and references |
| `doctors.html` | Clinical collaboration, brochure request, clinician FAQ |
| `investors.html` | Vision, how machine, supplies and support fit together, road ahead, investor deck request |
| `about.html` | Purpose, principles and audience routes |
| `privacy.html` | Privacy notice (previous design) |
| `machine.html`, `contact.html`, `catalog.html` | Redirects from old addresses |

## Run locally

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

No build step, package installation or API key is needed. Edit the HTML files directly.

## Shared kit

- `assets/proto.css` – design kit: brand colours (navy, teal, aqua), Manrope, buttons, cards, status chips, mobile bottom bar, forms.
- `assets/proto.js` – injects the header, mobile menu, footer, floating action button and mobile bottom bar on every page; English/Hindi switch (`data-i18n` keys; the Hindi text should be reviewed by a native speaker); reveal-on-scroll; and the smart enquiry forms.
- `assets/products.js` – the single product list. Change a product's `status` (`available`, `enquire`, `unavailable`, `planned`) and every page updates.
- `assets/machine-viewer.*`, `assets/models/`, `assets/vendor/` – the interactive 3D machine (Three.js r134 + GLTF loader).

## Owner settings in `assets/proto.js`

- `WHATSAPP` – add the business number (country code and digits, e.g. `919XXXXXXXXX`). WhatsApp buttons, the floating button and the mobile bar's WhatsApp tab appear only once this is set; until then the mobile bar shows Contact.
- `FORM_ENDPOINT` – the owner's Formspree endpoint. Every form (contact, quote, notify, interest, clinical collaboration, investor deck, brochure, distributor, updates sign-up) posts here with a form type and subject. Forms require consent, include a honeypot and keep the visitor's details if sending fails.

## Content still to add

Team names, roles and photos; verified milestones with dates; news posts; real product photos; the WhatsApp number. Sections for team and news were left out of the published pages until real details are available.

## Testing

Open any page with `?qa` (forms then never send), then in the browser console load and run the harness:

```js
await new Promise(r => { const s = document.createElement('script'); s.src = '/scripts/qa.js'; s.onload = r; document.head.append(s); });
await runQA();
```

It checks sideways scrolling, images, internal links, reveal animations, tap-target and text sizes on phones, the mobile menu and bar, the language switch, every form (consent, phone-or-email, success), and page features (audience tabs, catalogue filters/search/drawer, quiz, video and chapters). Run it at desktop width and at 375px.

## Publish

Commit to `main`. GitHub Pages updates www.rynormedtech.com. `CNAME` must remain `www.rynormedtech.com`.

## Assets and factual constraints

- No certifications, approvals, clinical outcomes, prices, launch dates or statistics are claimed.
- Supply images are technical illustrations until real photos are added; the 3D machine is a concept.
- Manrope is self-hosted under the SIL Open Font License; Three.js under MIT. Licenses are in `assets/licenses/`.
