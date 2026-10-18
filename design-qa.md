# RYNOR Medtech design QA

final result: passed

Reviewed 13 October 2026 in Chromium using the served website, not static HTML alone.

## Design reference and implementation

The selected direction is **Clinical Precision**: white and ice-blue surfaces, navy typography, teal accents, a closed-exterior machine hero, three product groups and a navy contact strip. The supplied SVG logos are preserved.

The selected reference is `/workspace/generated_images/exec-e2cd771b-2294-4b23-a3c9-1767f8609973.png`. A browser capture at its 1190 × 1322 viewport is `/workspace/rynor-design/qa/home-reference-viewport.png`. Visual comparison confirms the same content hierarchy, palette, two-column desktop hero, product sequence and contact treatment. The implementation is an adaptation rather than a pixel-identical rendering: it uses independently generated concept assets, factual development-stage copy, more spacious sections and an additional navigation/disclosure footer. On mobile the hero and product groups stack, and navigation collapses into a menu.

Reviewed desktop captures for all five pages and phone captures of the homepage, contact page and enquiry dialog. Supply imagery fits its containers without the oversized blank areas found during the first review. The machine image shows only the exterior. All concept imagery is labelled; none of the machine or supplies are represented as currently available for sale.

## Interaction and responsive verification

`scripts/check_site.py` completed **15 functional check groups** covering:

- All five pages, their metadata, active navigation, loaded images and local links.
- Every supply filter, text search, empty results and reset.
- Category deep links and the matching product enquiry topic.
- Dialog keyboard focus cycling, Escape dismissal and focus restoration.
- Required message validation and correctly encoded email draft contents.
- FAQ disclosure, mobile navigation and the legacy catalog redirect.
- All five pages at 320, 390 and 768 CSS pixels without horizontal overflow.
- No JavaScript runtime errors or failed HTTP responses.

Desktop screenshots were captured at 1440 × 1100 and full-page phone screenshots at 390 × 844. Evidence is in `/workspace/rynor-design/qa/`, including `checks.json`, each page's desktop/mobile screenshots and `enquiry-mobile.png`. The README gives the commands to reproduce the checks.

Axe-core 4.14.0 reported **zero WCAG 2 A/AA and WCAG 2.1 AA rule violations across the five desktop pages**. After adding an email-address wrap opportunity, the contact page was checked again at 320, 390 and 1440 pixels: the address and mailto target remained correct, with no horizontal overflow and no axe violations. JavaScript syntax checking also passed.

## Resolved findings

- Product image sizing no longer inherits an excessive intrinsic height.
- Teal labels and development-status text meet the checked contrast rules.
- Keyboard focus cycles within the enquiry dialog and returns to its trigger.
- Opening an email draft preserves the website and exposes a direct draft/address fallback.
- The contact email wraps at the address/domain boundary when necessary on phones.

No remaining blocking visual or interaction findings were identified in the reviewed states.

## Follow-up testing and fixes — 13 October 2026

After the owner confirmed the site opens on their phone, a second pass covered copy, spacing, additional screen sizes and form/search edge cases. The expanded suite passed **21 functional check groups**, with **zero automated accessibility violations across the five pages**. Results and screenshots are in `/workspace/rynor-design/qa-round2/`.

Confirmed issues fixed:

- Searches such as `2L`, `swan neck`, `APD CAPD` and `MINI CAPs` now find the corresponding supplies despite spacing, punctuation or capitalisation differences.
- A message containing only spaces cannot open an email draft. Editing the message or other form values hides an outdated draft link until the draft is prepared again.
- At tablet widths, the machine exterior is fully visible and the headline/section alignment is more balanced. Before/after captures at 768 and 1024 pixels were visually compared.
- Home, logo and breadcrumb links use the homepage directory URL, without adding `index.html` to the address.
- The bag-size label uses normal spacing; catheter terminology and brand/email consistency were proofread. British spellings such as “enquiries” and “programme” are intentional.
- Stylesheet and script URLs include content versions so browsers request changed assets after a rebuild.

Additional verification covered invalid email addresses, corrected form input after validation errors, 320/375/390/414/768/1024 pixel layouts, and touch navigation/filter/enquiry interactions using Chromium's iPhone 13 and Pixel 7 emulation settings. All five pages also passed checks for unique IDs, valid label/control references, local resource paths and the contact email address. Sitemap XML and the custom-domain file remain valid. Versioned assets were separately loaded and exercised through mobile navigation on each page.

## Verification limits

Email draft creation was checked; no email was sent and mailbox delivery was not tested. Automated accessibility checks supplement the visual and keyboard checks, and are not an accessibility certification. Safari, Firefox and physical devices were not tested. Public GitHub Pages deployment is a separate publishing check; this result covers the built website served in the development environment.

## Motion enhancement verification — October 18, 2026

- Homepage checked in the Codex in-app browser at desktop size: GSAP/Lenis initialized, Vanta created one canvas, no horizontal overflow, and no warning/error console entries were reported.
- Pause control: canvas removed, Lenis scrolling removed, animated content restored to full visibility; re-enabling motion worked.
- Enquiry dialog: opened normally, Lenis stopped while open, Escape closed the dialog and restored focus to the trigger. No email was sent.
- Mobile viewport 390 x 844: Vanta canvas removed, smooth scrolling disabled in favor of native scrolling, no horizontal overflow; mobile menu opened and navigation to Supplies worked.
- Supplies Tubing filter: only the tubing category remained visible and count updated to one.
- Node fallback checks: reduced-motion preference, saved opt-out, and unavailable libraries do not initialize animation engines.
- Generated pages rebuilt successfully and git diff whitespace checks passed.
- Browser checks cover the motion changes and representative existing interactions, not a full rerun of scripts/check_site.py or an accessibility certification. Browser WebGL support and device performance still vary; the static fallback remains available.

## Sandbox regression pass — October 18, 2026

Two performance/fallback defects were reproduced and fixed: Vanta continued rendering after the hero scrolled offscreen, and unsupported WebGL still downloaded the renderer and logged an avoidable error. The corrected motion runtime probes WebGL before loading Three.js and releases/recreates its renderer on hero intersection changes.

Retests passed: offscreen zero-canvas state, one-canvas restoration, pause cleanup, reduced-motion/missing-library/blocked-storage/data-saving fallbacks, all five pages at six verified widths (1024, 768, 414, 390, 375 and 320px), modal focus trapping/Escape, invalid contact inputs, email draft encoding without sending, filters/search/reset, mobile navigation, FAQ and legacy catalog redirect. All five main-content comparisons against the original pre-animation site and local asset reference checks passed.

axe-core 4.14.0 found zero automated WCAG A/AA violations across the five stable pages with motion paused. Homepage image-caption contrast required visual review; no accessibility certification or physical-device/browser-matrix claim is made. The independent local sandbox and its failure simulations are not deployed with the website.


## Styling refinement and direct enquiry preparation — October 18, 2026

Retained the navy hero, sticky navigation and development timeline. Reduced desktop section spacing and heading weight, simplified product cards, and removed the conflicting Contact underline. GSAP entrances are shorter and gentler. The desktop wave layer is visible at low opacity, and its renderer is skipped when CSS hides it. Mobile, reduced-motion, pause and data-saving fallbacks remain supported. Generated pages were rebuilt to refresh CSS and JavaScript cache versions.

A configurable Formspree integration now supports direct web enquiries. The destination account's public endpoint is still required in `site-config.json`; while empty, the existing email-draft flow remains active. No dummy endpoint is published. Direct forms require a reply email and a nonblank message, carry the chosen product topic, disable repeated submission while sending, and retain input after an unsuccessful or unconfirmed request. Privacy information and a direct email alternative are included.

Verification: 21 existing functional check groups passed, with zero automated accessibility violations across all five pages. Three motion fallback checks passed. The direct-form fixture passed validation, payload, inline success, duplicate prevention, server rejection, connection failure, retry and mobile dialog checks, with zero axe violations on its contact page and open mobile dialog. Every Formspree request in these checks was intercepted: no real email was sent, and inbox delivery is not yet verified. Desktop wave rendering was separately confirmed with one visible canvas; desktop and mobile screenshots were inspected.

Evidence is saved in `/workspace/rynor-review/refined/`, including `form-qa/` for the prepared direct forms. Tests used local Chromium; physical phones and Safari were not tested. Public-domain verification remains unavailable through this environment's network proxy.


## Formspree endpoint activation — October 18, 2026

Configured the owner-provided public endpoint `https://formspree.io/f/mbgdblpw` and regenerated all five pages. Both the contact form and shared enquiry dialog now use direct POST submission, with required reply email, automatic subject, inline feedback and no email-app redirect. All six generated forms were checked for the exact endpoint and POST method; the obsolete email-draft instructions are absent.

The full configured-site suite passed 21 functional check groups and reported zero automated accessibility violations across all five pages. The submission check intercepted the provider request, so no real message was sent and inbox receipt remains unverified. Evidence is in `/workspace/rynor-review/form-activated/`. The owner should submit one enquiry on the deployed website and confirm receipt in the configured Formspree destination inbox.


## More noticeable motion — October 18, 2026

At the owner’s request, strengthened the installed animation effects: desktop headline lines enter in sequence, the hero machine rises and scales into place, product cards and timeline stages reveal with a stagger, the Vanta wave layer is clearer, and desktop product/button hover effects acknowledge interaction. Mobile uses a shorter single headline entrance and native scrolling without WebGL. All effects respect reduced-motion and the saved Pause motion preference. Content and the configured Formspree endpoint are unchanged.

Three Node fallback checks passed. Chromium browser checks confirmed the visible desktop wave canvas, finished hero/card/timeline entrances, hover scaling, pause cleanup and persistence, enquiry dialog operation, mobile layout without horizontal overflow, and restoration of all content on a live reduced-motion preference change. No JavaScript runtime errors were observed. An initial test asserted the media preference before the browser dispatched its change event; waiting for the observable state change resolved the test timing issue. Desktop/mobile captures were saved under `/workspace/rynor-review/stronger-motion/`, and the desktop wave screenshot was visually inspected. This targeted pass did not repeat the full form-delivery or accessibility suites; live deployment and physical devices remain unverified.
