# RYNOR Medtech website

A responsive, static website for RYNOR Medtech, prepared for GitHub Pages. CAPD fluid bags and tubing are not currently available, as clarified by the owner. Transfer sets have an availability-enquiry route. The APD machine and dedicated range remain in development.

## Run locally

```bash
cd /workspace/rynormedtech
python3 -m http.server 8000 --bind 127.0.0.1
```

No package installation, database, API keys, or frontend build is required to serve the committed pages. Fonts, icons, illustrations and logos are served locally.

## Animation and visitor preferences

`assets/motion.js` progressively adds GSAP entrances and section reveals across the five pages. The desktop homepage headline enters line by line, the machine image rises into place, and product cards and development stages reveal in sequence. Hovering a product gently enlarges its image; button arrows move to acknowledge interaction. These effects follow the visitor’s motion preference. The header logo blends into its background and fits its container without cropping. On fine-pointer desktops it has a short 3D entrance and a gentle pointer-following tilt; mobile and reduced-motion visitors see a static logo. Logo event listeners and transforms are removed when motion is paused or the layout changes. On fine-pointer desktops at least 900px wide, Lenis smooths wheel scrolling; mobile and touch scrolling remain native. The homepage adds a visible, translucent Vanta Waves background behind its copy, with the matching Three.js r134 renderer loaded only when needed. Browser data-saving mode skips that background, and failures leave the original static hero usable.

The footer's **Pause motion** button stops animations and smooth scrolling, restores visible content, and remembers the visitor's choice when local storage is available. The operating system's reduced-motion preference takes precedence. Open enquiry dialogs stop background smooth scrolling, and page lifecycle cleanup releases animations and WebGL resources.

The hero checks WebGL support before downloading its renderer. An IntersectionObserver releases the wave renderer while the hero is offscreen and recreates it when the visitor returns, avoiding continuous GPU work below the hero.

Run `node scripts/check_motion.mjs` to check reduced-motion, saved opt-out, and missing-library fallback paths. Browser QA should also check the homepage canvas, the pause/resume control, mobile native scrolling, product filters, and enquiry dialog behavior.

All runtime files are self-hosted in `assets/vendor/`: GSAP/ScrollTrigger 3.15.0, Lenis 1.3.27, Vanta Waves 0.5.24, and Three.js 0.134.0. `assets/vendor/versions.json` records source packages and file hashes. MIT notices for Lenis, Vanta, and Three.js are in `assets/licenses/`; GSAP uses its standard no-charge license at https://gsap.com/standard-license, with its copyright and license header retained in both distribution files. These libraries do not require a build step on GitHub Pages. Keep versions and notices together when updating.

## Edit and rebuild the pages

The homepage hero and Our Machine page progressively replace its static machine image with a self-hosted Three.js concept viewer. Visitors can rotate the enclosure, open the lower front lid independently of the fixed screen, open the top heating lid, select front/right/rear/top views, and zoom using labelled buttons. A clean loading panel is shown while the 3D view starts; the original photo is hidden until an actual fallback is needed. The original image remains the fallback for disabled JavaScript, unavailable WebGL, failed model loading or a missing viewer script. Data-saving mode waits for an explicit request to load the viewer. Touch scrolling remains native; horizontal dragging rotates the machine. Rendering stops when idle, offscreen, or the page is hidden, and resources are disposed on page exit. Reduced-motion and the footer motion preference make requested transitions immediate.

The model is `assets/models/rynor-machine-concept.glb`; the viewer's isolated styles and behaviour are `assets/machine-viewer.css` and `assets/machine-viewer.js`. The matching r134 GLTFLoader is self-hosted in `assets/vendor/gltf-loader-0.134.0.js` and shares the site's existing Three.js runtime. This is a visual enclosure concept with proposed side/rear/internal details, not a production CAD assembly. Both lids have independent pivots and embedded opening clips. Nominal closed enclosure dimensions are 457.2 × 254 × 254 mm.

- `scripts/build_site.py` contains the page content and shared HTML templates.
- `assets/site.css` contains desktop, tablet and mobile layouts.
- `assets/site.js` contains navigation, supply filters, search and email enquiry interactions.

After changing the templates, CSS or JavaScript, regenerate the committed HTML. The generator includes a content version in the stylesheet and script URLs so browsers request the updated assets:

```bash
python3 scripts/build_site.py
```

The generated pages are `index.html`, `machine.html`, `supplies.html`, `pd-at-home.html`, `privacy.html`, `about.html` and `contact.html`. The PD page and privacy notice are maintained in `content/`. The old `catalog.html` address redirects to `supplies.html`. The generator also updates `sitemap.xml` and `robots.txt`.

## Contact behaviour

The contact page and enquiry dialog submit directly through the owner-provided Formspree endpoint `https://formspree.io/f/mbgdblpw`. Inbox delivery must be verified in the owner’s Formspree account. To configure a replacement form:

1. Create a Formspree form with destination `syedkamran@rynormedtech.com` and verify the destination in the owner's account.
2. Put its public endpoint (for example, `https://formspree.io/f/FORM_ID`) in `site-config.json` under `formspree_endpoint`. Never add an API key or password.
3. Run `python3 scripts/build_site.py`, commit the generated HTML and publish to `main`.
4. Submit an enquiry and verify it arrives in the destination inbox. Check the provider's spam settings and account usage limits as needed.

The configured endpoint enables both direct-send forms and their explanatory text together. Clearing the endpoint and rebuilding restores the email-draft fallback.

The direct enquiry form requires either phone or email, plus a message. CAPD and transfer-set links select the relevant topic, default to phone for an empty form, and provide an editable quote request. General enquiries default to email. Topic links also work when opened as a separate contact page. The non-JavaScript direct form accepts email and a message. It submits via HTTPS without opening an email app; Formspree processes the message and routes it to the configured destination. Visitors see a link to Formspree's privacy policy and a reminder not to share sensitive medical information. Loading, success and failure states are announced inline. Failed or unconfirmed requests retain the message for retry. Buttons and fields are disabled during sending to prevent duplicate clicks. A hidden honeypot complements Formspree's spam protection. Direct email remains available as an alternative. With JavaScript disabled, a configured form posts to Formspree using the browser's native form submission.

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
- The machine photo is the original exterior concept. Supply pages now use original SVG technical concepts in `assets/illustrations/`, generated by `scripts/build_supply_art.py`. They are labelled illustrations and do not establish final specifications or compatibility. The older supply concept images are retained as unused source assets.
- The homepage has an interactive enclosure concept, with independently opening front and heating lids. Unseen side, rear and internal details are proposed; final designs and specifications may change. The machine detail page uses the same model and controls as the homepage; the original image remains the fallback.
- CAPD fluid bags and tubing are not currently available. Transfer-set stock must be confirmed with RYNOR; catheters and caps retain their development status. There is no online checkout, invented price, unverified brand or pack-strength claim.
- No certifications, approvals, clinical outcomes, institutional endorsements, telephone number, launch date, or legal company suffix are invented.
- Manrope 5.3.0 is self-hosted under its SIL Open Font License. Bootstrap Icons 1.13.2 is used under the MIT License. Package integrity was verified before extracting assets. Licenses are in `assets/licenses/`.

`design-qa.md` records the design and verification outcome for this implementation.

## PD education and interest registration

`pd-at-home.html` offers a 36-second captioned H.264 animation, transcript, an interactive fill/dwell/drain diagram, three memory-only learning questions, and a patient-first interest form. `assets/pd-community.js` handles these features. `assets/pd-community.css` adds responsive layouts, technical supply presentation, and the shared logo fix. A native SVG colour matrix removes white from the displayed logo alpha; the supplied logo asset and its geometry remain unchanged.

The video is prebuilt and self-hosted; no video service, account or runtime build is needed. To recreate it on Windows with Arial installed, install `scripts/requirements-media.txt` in a development environment and run `python scripts/build_apd_video.py`. It is an original schematic educational animation, not an illustration of operating the RYNOR device. Content references are linked on the page. It makes no claim of guaranteed painlessness, savings, approval or current availability.

The interest form uses the same public Formspree endpoint as existing enquiries. It requires name, one contact method (phone OR email), audience, and explicit adult contact consent. City, language, professional organisation and development updates are optional. It does not collect medical records, diagnoses, quiz answers or a free-text medical history. The doctor link selects the professional route. Requests are never stored in browser storage or the public repository.

In the existing Formspree dashboard, identify these submissions by `form_type=pd_interest` and `audience=patient_or_caregiver` or `doctor`. Subject/topic fields also distinguish the audience. Consent notice version, consent text, client timestamp and the separate update choice travel with the request. Handle contact/deletion requests via the email in `privacy.html`; remove corresponding notifications/exports when appropriate. Archive availability and exports depend on the current Formspree plan and settings. Keep provider credentials out of the website.

Local mock tests checked required fields, invalid phone rejection, provider rejection with retained details, retry success, patient phone-only and doctor email-only payloads, separate optional consent, and exclusion of quiz answers. No live submissions were sent; the owner must verify delivery and retention in the Formspree account. Responsive browser checks covered the learning page, video, quiz, catalogue and machine controls. These are functional checks, not a clinical, regulatory or accessibility certification.

## Catalogue source and checks

`content/products.json` is the catalogue source for product descriptions, availability, illustrations, enquiry topics and homepage supply cards. Status values are `unavailable`, `enquire` and `planned`. Update this file when product information is verified, then rebuild the site. Do not infer that every product is for sale from the machine's development status or vice versa. The owner clarified that CAPD bags and tubing are not currently available; no live inventory feed is connected. Exact brands, pack sizes, strengths, prices and delivery options are confirmed through enquiries.

Run `python scripts/build_site.py`, `python scripts/check_catalog.py`, and `node scripts/check_motion.mjs`. The catalogue check covers all seven pages, local assets/links, duplicate IDs, product status/topic consistency, removal of obsolete blanket availability copy, loading-panel markup and the unchanged model hash. Browser checks must still cover the mobile menu, combined category/availability/search filtering, empty-state reset, quote modal dismissal, phone/email validation, local mocked submission errors/retry, the loading state and model/no-script fallbacks. Never send test patient information to the live form provider.

Supply enquiries are tagged `form_type=supply_enquiry`; general enquiries use `general_enquiry`; the patient/doctor page retains `pd_interest`. Only the selected contact field is submitted. The client preserves a failed enquiry and disables the form while sending. Formspree delivery, retention, account access and quota settings need verification by the owner in the existing account. No new account or database was created.
