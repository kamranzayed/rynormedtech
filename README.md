# RYNOR Medtech website

A responsive, static website for RYNOR Medtech, prepared for GitHub Pages. The machine and every supply category are presented as a planned range, preparing for clinical trials and not yet available for sale.

## Run locally

```bash
cd /workspace/rynormedtech
python3 -m http.server 8000 --bind 127.0.0.1
```

No package installation, database, API keys, or frontend build is required to serve the committed pages. Fonts, icons, illustrations and logos are served locally.

## Animation and visitor preferences

`assets/motion.js` progressively adds GSAP entrances and section reveals across the five pages. On fine-pointer desktops at least 900px wide, Lenis smooths wheel scrolling; mobile and touch scrolling remain native. The homepage adds a low-opacity Vanta Waves background behind its copy, with the matching Three.js r134 renderer loaded only when needed. Browser data-saving mode skips that background, and failures leave the original static hero usable.

The footer's **Pause motion** button stops animations and smooth scrolling, restores visible content, and remembers the visitor's choice when local storage is available. The operating system's reduced-motion preference takes precedence. Open enquiry dialogs stop background smooth scrolling, and page lifecycle cleanup releases animations and WebGL resources.

The hero checks WebGL support before downloading its renderer. An IntersectionObserver releases the wave renderer while the hero is offscreen and recreates it when the visitor returns, avoiding continuous GPU work below the hero.

Run `node scripts/check_motion.mjs` to check reduced-motion, saved opt-out, and missing-library fallback paths. Browser QA should also check the homepage canvas, the pause/resume control, mobile native scrolling, product filters, and enquiry dialog behavior.

All runtime files are self-hosted in `assets/vendor/`: GSAP/ScrollTrigger 3.15.0, Lenis 1.3.27, Vanta Waves 0.5.24, and Three.js 0.134.0. `assets/vendor/versions.json` records source packages and file hashes. MIT notices for Lenis, Vanta, and Three.js are in `assets/licenses/`; GSAP uses its standard no-charge license at https://gsap.com/standard-license, with its copyright and license header retained in both distribution files. These libraries do not require a build step on GitHub Pages. Keep versions and notices together when updating.

## Edit and rebuild the pages

- `scripts/build_site.py` contains the page content and shared HTML templates.
- `assets/site.css` contains desktop, tablet and mobile layouts.
- `assets/site.js` contains navigation, supply filters, search and email enquiry interactions.

After changing the templates, CSS or JavaScript, regenerate the committed HTML. The generator includes a content version in the stylesheet and script URLs so browsers request the updated assets:

```bash
python3 scripts/build_site.py
```

The generated pages are `index.html`, `machine.html`, `supplies.html`, `about.html` and `contact.html`. The old `catalog.html` address redirects to `supplies.html`. The generator also updates `sitemap.xml` and `robots.txt`.

## Contact behaviour

The contact page and enquiry dialog submit directly through the owner-provided Formspree endpoint `https://formspree.io/f/mbgdblpw`. Inbox delivery must be verified in the owner’s Formspree account. To configure a replacement form:

1. Create a Formspree form with destination `syedkamran@rynormedtech.com` and verify the destination in the owner's account.
2. Put its public endpoint (for example, `https://formspree.io/f/FORM_ID`) in `site-config.json` under `formspree_endpoint`. Never add an API key or password.
3. Run `python3 scripts/build_site.py`, commit the generated HTML and publish to `main`.
4. Submit an enquiry and verify it arrives in the destination inbox. Check the provider's spam settings and account usage limits as needed.

The configured endpoint enables both direct-send forms and their explanatory text together. Clearing the endpoint and rebuilding restores the email-draft fallback.

The direct form requires an email address and message, supplies a default topic, and preserves product-specific topics. It submits via HTTPS without opening an email app; Formspree processes the message and routes it to the configured destination. Visitors see a link to Formspree's privacy policy and a reminder not to share sensitive medical information. Loading, success and failure states are announced inline. Failed or unconfirmed requests retain the message for retry. Buttons and fields are disabled during sending to prevent duplicate clicks. A hidden honeypot complements Formspree's spam protection. Direct email remains available as an alternative. With JavaScript disabled, a configured form posts to Formspree using the browser's native form submission.

`python3 scripts/check_enquiry.py` builds an isolated fixture with a dummy endpoint and intercepts every provider request. It checks validation, submitted fields, duplicate prevention, success, server rejection, network failure, retry and the mobile enquiry dialog. It never sends real email and does not establish live delivery.

## Check the website

The prepared cloud environment includes Python Playwright and Chromium. With the server running:

```bash
python3 scripts/check_site.py --base-url http://127.0.0.1:8000 --output /tmp/rynor-qa
```

The smoke checks cover page/asset links, clean homepage navigation, catalog category filters and flexible search, empty-state recovery, product enquiry topics, keyboard modal behaviour, blank-message and invalid-email validation, email drafts or simulated direct submission (depending on configuration), mobile navigation, six responsive widths, touch controls in Chromium phone emulation, FAQ disclosures and the legacy catalog redirect. Email delivery is not tested or performed. Screenshots and a JSON report are written to the output directory.

For WCAG A/AA automated checks, also supply a local copy of `axe.min.js` with `--axe /path/to/axe.min.js`. When axe-core is missing, the runner explicitly reports that the accessibility scan did not run. These automated checks supplement visual and keyboard review; they are not an accessibility certification.

## Publish

GitHub Pages is configured to serve `main` from the repository root. Publishing the generated pages and assets to that branch updates the website through the existing Pages deployment. `CNAME` must remain `www.rynormedtech.com`.

Publishing a Codex development environment is separate from publishing these website files to GitHub Pages.

## Assets and factual constraints

- The original RYNOR SVG logos were supplied by the owner.
- The four machine and supply images are generated exterior/product concepts, visibly labelled on the website. They are not photographs of finished products. Lossless WebP conversion preserves their pixels.
- The public machine preview shows its closed exterior only.
- All supplies are planned to launch with the machine. No checkout or current stock claim is present.
- No certifications, approvals, clinical outcomes, institutional endorsements, telephone number, launch date, or legal company suffix are invented.
- Manrope 5.3.0 is self-hosted under its SIL Open Font License. Bootstrap Icons 1.13.2 is used under the MIT License. Package integrity was verified before extracting assets. Licenses are in `assets/licenses/`.

`design-qa.md` records the design and verification outcome for this implementation.
