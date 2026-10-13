# RYNOR Medtech website

A responsive, static website for RYNOR Medtech, prepared for GitHub Pages. The machine and every supply category are presented as a planned range, preparing for clinical trials and not yet available for sale.

## Run locally

```bash
cd /workspace/rynormedtech
python3 -m http.server 8000 --bind 127.0.0.1
```

No package installation, database, API keys, or frontend build is required to serve the committed pages. Fonts, icons, illustrations and logos are served locally.

## Edit and rebuild the pages

- `scripts/build_site.py` contains the page content and shared HTML templates.
- `assets/site.css` contains desktop, tablet and mobile layouts.
- `assets/site.js` contains navigation, supply filters, search and email enquiry interactions.

After changing the templates, regenerate the committed HTML:

```bash
python3 scripts/build_site.py
```

The generated pages are `index.html`, `machine.html`, `supplies.html`, `about.html` and `contact.html`. The old `catalog.html` address redirects to `supplies.html`. The generator also updates `sitemap.xml` and `robots.txt`.

## Contact behaviour

The contact form and enquiry dialog prepare a correctly encoded email draft addressed to `syedkamran@rynormedtech.com`. The visitor's email application is responsible for sending it. The site has no messaging backend, live agent, or form database, and does not automatically send messages. A direct email address and draft link remain available when an email application does not open.

## Check the website

The prepared cloud environment includes Python Playwright and Chromium. With the server running:

```bash
python3 scripts/check_site.py --base-url http://127.0.0.1:8000 --output /tmp/rynor-qa
```

The smoke checks cover page/asset links, catalog category filters and search, empty-state recovery, product enquiry topics, keyboard modal behaviour, required fields, encoded email drafts, mobile navigation, responsive widths, FAQ disclosures and the legacy catalog redirect. Email delivery is not tested or performed. Screenshots and a JSON report are written to the output directory.

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
