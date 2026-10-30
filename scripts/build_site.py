#!/usr/bin/env python3
"""Build the static GitHub Pages site from shared templates and local assets."""
from html import escape
from hashlib import sha256
from pathlib import Path
import json
import re
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
EMAIL = 'syedkamran@rynormedtech.com'
CONFIG = json.loads((ROOT / 'site-config.json').read_text())
FORM_ENDPOINT = CONFIG['formspree_endpoint'].strip()
if FORM_ENDPOINT and not re.fullmatch(r'https://formspree\.io/f/[A-Za-z0-9]+', FORM_ENDPOINT):
    raise ValueError('Use the public Formspree endpoint: https://formspree.io/f/FORM_ID')
ORIGIN = 'https://www.rynormedtech.com'
NAV = [('index.html', 'Home'), ('machine.html', 'Our Machine'), ('supplies.html', 'Supplies'), ('pd-at-home.html', 'PD at Home'), ('about.html', 'About'), ('contact.html', 'Contact')]
PRODUCTS = json.loads((ROOT/'content/products.json').read_text(encoding='utf-8'))
AVAILABILITY = {'unavailable': 'Not currently available', 'enquire': 'Check availability', 'planned': 'In development'}
assert len({p['category'] for p in PRODUCTS}) == len(PRODUCTS)
assert all(p['availability'] in AVAILABILITY for p in PRODUCTS)
TOPICS = ['General enquiry', 'Our machine'] + [p['topic'] for p in PRODUCTS] + ['Clinical collaboration', 'Distribution partnership', 'Investor enquiry']


def versioned_asset(path):
    version = sha256((ROOT / path).read_bytes()).hexdigest()[:12]
    return f'{path}?v={version}'


def icon(name):
    return f'<img class="icon" src="assets/icons/{name}.svg" width="20" height="20" alt="" aria-hidden="true">'


def brand():
    return '<a class="brand" href="./" aria-label="RYNOR Medtech home"><img src="assets/brand/rynor-logo.svg" width="6912" height="3456" alt="RYNOR Medtech"></a>'


def header(current):
    links = ''.join(f'<a class="nav-link{" nav-contact" if href == "contact.html" else ""}" href="{"./" if href == "index.html" else href}" {"aria-current=\"page\"" if href == current else ""}>{label}</a>' for href, label in NAV)
    return f'''<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute"><defs><filter id="rynor-logo-ink" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  -1 -1 -1 0 3"/></filter></defs></svg><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner">{brand()}
<button class="menu-toggle" type="button" data-menu-toggle aria-controls="primary-nav" aria-expanded="false" aria-label="Open navigation">{icon('list')}</button>
<nav class="primary-nav" id="primary-nav" aria-label="Primary navigation">{links}</nav></div></header>'''


def enquiry_link(label='Product enquiries', topic='General enquiry', css='text-link'):
    return f'<a class="{css}" href="contact.html?{urlencode({'topic': topic})}" data-enquiry="{escape(topic, quote=True)}">{label}{icon("arrow-right")}</a>'


def status(machine=False):
    label = 'APD machine in development' if machine else 'Supply availability'
    detail = 'Preparing for clinical trials. CAPD fluid bags and tubing are not currently available.' if machine else 'CAPD fluid bags and tubing are not currently available. RYNOR APD machine in development.'
    return f'''<div class="status-strip"><div class="container status-inner"><p class="status-heading">{icon('hourglass-split' if machine else 'check-lg')}<span>{label}</span></p><p class="status-description">{detail}</p></div></div>'''


def email_form(prefix):
    options = ''.join(f'<option value="{escape(topic, quote=True)}">{escape(topic)}</option>' for topic in TOPICS)
    if FORM_ENDPOINT:
        return f'''<form data-email-form data-direct-send action="{FORM_ENDPOINT}" method="post">
<div class="field-row"><div class="field"><label for="{prefix}-name">Your name <span class="optional">(optional)</span></label><input id="{prefix}-name" name="name" autocomplete="name" maxlength="100"></div><div class="field" data-enquiry-contact-choice hidden><label for="{prefix}-method">Contact me by</label><select id="{prefix}-method" name="contact_method" data-enquiry-method><option value="email">Email</option><option value="phone">Phone</option></select></div></div>
<div class="field"><label for="{prefix}-email" data-enquiry-contact-label>Your email</label><input id="{prefix}-email" data-enquiry-contact name="email" type="email" autocomplete="email" required maxlength="180" placeholder="you@example.com"></div>
<div class="field"><label for="{prefix}-topic">Topic <span class="optional">(optional)</span></label><select id="{prefix}-topic" name="topic">{options}</select></div>
<div class="field"><label for="{prefix}-message">Your message</label><textarea id="{prefix}-message" name="message" rows="4" required maxlength="1800" placeholder="How can we help?"></textarea></div>
<div class="form-honeypot" aria-hidden="true"><label for="{prefix}-website">Leave this field empty</label><input id="{prefix}-website" name="_gotcha" tabindex="-1" autocomplete="off"></div>
<button class="button" type="submit"><span data-submit-label>Send enquiry</span>{icon('arrow-right')}</button>
<p class="form-note">Your message goes to the RYNOR team via <a href="https://formspree.io/legal/privacy-policy/" target="_blank" rel="noopener noreferrer">Formspree</a>. We’ll use the contact method you choose to respond. Please don’t include medical records or sensitive health information. <a href="privacy.html">Contact privacy</a>.</p>
<div class="form-status" data-draft-status role="status" aria-live="polite" aria-atomic="true" hidden></div>
<p class="form-note">Prefer email? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</form>'''
    return f'''<form data-email-form action="mailto:{EMAIL}" method="get">
<div class="field-row"><div class="field"><label for="{prefix}-name">Your name <span class="optional">(optional)</span></label><input id="{prefix}-name" name="name" autocomplete="name" maxlength="100"></div>
<div class="field"><label for="{prefix}-email">Your email <span class="optional">(optional)</span></label><input id="{prefix}-email" name="email" type="email" autocomplete="email" maxlength="180"></div></div>
<div class="field"><label for="{prefix}-topic">What would you like to discuss?</label><select id="{prefix}-topic" name="topic">{options}</select></div>
<div class="field"><label for="{prefix}-message">Your message</label><textarea id="{prefix}-message" name="message" rows="4" required maxlength="1800" placeholder="Tell us about your enquiry or organisation."></textarea></div>
<button class="button" type="submit">Open email draft{icon('arrow-up-right')}</button>
<p class="form-note">This opens your email app. Review the draft and send it there. Nothing is sent automatically.</p>
<div class="draft-status" data-draft-status role="status" hidden>Your email draft is ready. If your email app did not open, <a href="mailto:{EMAIL}" target="_blank" rel="noopener noreferrer">open the draft again</a> or email <strong>{EMAIL}</strong> directly.</div>
</form>'''


def footer(current=''):
    links = ''.join(f'<a href="{href}">{label}</a>' for href, label in NAV[1:]) + '<a href="privacy.html">Privacy</a>'
    floating = '<a class="floating-enquiry" href="pd-at-home.html#connect" aria-label="Register PD interest">'+icon('chat-dots')+'<span>Connect</span></a>' if current == 'pd-at-home.html' else '<a class="floating-enquiry" href="contact.html" data-enquiry="General enquiry" aria-label="Open enquiry">'+icon('chat-dots')+'<span>Enquire</span></a>'
    if current == 'contact.html':
        floating = ''
    return f'''<section class="contact-band" aria-label="Contact Rynor"><div class="container contact-band-inner"><div><h2>Let’s start a conversation.</h2><p>For product enquiries, clinical collaboration and future partnerships.</p></div><a class="contact-email" href="mailto:{EMAIL}">{icon('envelope')}<span>{EMAIL}</span></a>{enquiry_link('Enquire', css='button button-light')}</div></section>
<footer class="site-footer"><div class="container"><div class="footer-top">{brand()}<nav class="footer-links" aria-label="Footer navigation">{links}</nav></div><div class="footer-bottom"><div class="footer-preferences"><span>© 2026 RYNOR Medtech.</span><button class="motion-toggle" type="button" data-motion-toggle aria-pressed="false" hidden>Pause motion</button></div><p>CAPD fluid bags and tubing are not currently available. The RYNOR APD machine and its dedicated range remain in development. Supply visuals are technical illustrations; confirm the actual product and packaging with our team.</p></div></div></footer>
{floating}
<dialog class="enquiry-dialog" id="enquiry-dialog" aria-labelledby="enquiry-title"><div class="dialog-header"><div><p class="eyebrow">Contact RYNOR</p><h2 id="enquiry-title">Let’s talk.</h2></div><button type="button" class="dialog-close" data-dialog-close aria-label="Close enquiry">{icon('x-lg')}</button></div><p class="small-copy">Tell us what you need. One contact method is enough.</p><a class="dialog-address" href="mailto:{EMAIL}">{EMAIL}</a>{email_form('dialog')}</dialog>'''


def page(filename, title, description, content):
    canonical = ORIGIN + ('/' if filename == 'index.html' else '/' + filename)
    image_preload = ''
    viewer_assets = f'<link rel="stylesheet" href="{versioned_asset("assets/machine-viewer.css")}"><script src="{versioned_asset("assets/machine-viewer.js")}" defer></script>' if filename in ('index.html', 'machine.html') else ''
    community_assets = f'<link rel="stylesheet" href="{versioned_asset("assets/pd-community.css")}">'
    if filename == 'pd-at-home.html':
        community_assets += f'<script src="{versioned_asset("assets/pd-community.js")}" defer></script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#06264b">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="RYNOR Medtech"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/images/machine-concept.webp"><meta property="og:image:alt" content="Exterior concept illustration of the RYNOR peritoneal dialysis machine">
<link rel="icon" type="image/svg+xml" href="assets/brand/rynor-logo-square.svg"><link rel="preload" href="assets/fonts/manrope-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>{image_preload}<link rel="stylesheet" href="{versioned_asset("assets/site.css")}"><link rel="stylesheet" href="assets/vendor/lenis-1.3.27.css"><script>document.documentElement.classList.add('js');</script><script src="{versioned_asset("assets/site.js")}" defer></script><script src="assets/vendor/gsap-3.15.0.min.js" defer></script><script src="assets/vendor/scroll-trigger-3.15.0.min.js" defer></script><script src="assets/vendor/lenis-1.3.27.min.js" defer></script><script src="{versioned_asset("assets/motion.js")}" defer></script>{viewer_assets}{community_assets}</head>
<body data-page="{Path(filename).stem}">{header(filename)}<main id="main">{content}</main>{footer(filename)}</body></html>
'''


def heading(label, title, description):
    return f'''<section class="page-heading"><div class="container"><div class="breadcrumbs"><a href="./">Home</a>{icon('arrow-right')}<span>{label}</span></div><p class="eyebrow">{label}</p><h1>{title}</h1><p>{description}</p></div></section>'''


machine_preview = f'''<figure class="hero-figure machine-hero"><div class="machine-viewer" data-machine-viewer data-state="idle" data-model="{versioned_asset('assets/models/rynor-machine-concept.glb')}">
<div class="machine-viewer__stage" data-viewer-stage><img class="machine-viewer__poster" src="assets/images/machine-concept.webp" width="1374" height="1145" fetchpriority="low" loading="lazy" alt="Exterior concept of the RYNOR machine, with a fixed wide front touchscreen and closed lids"><div class="machine-viewer__loading" role="status"><strong>Interactive 3D preview</strong><span>Rotate, zoom and explore both opening lids.</span></div><span class="machine-viewer__badge">Interactive concept</span><button class="machine-viewer__start" type="button" data-viewer-start hidden>Explore in 3D</button></div>
<div class="machine-viewer__controls" data-viewer-controls hidden><button type="button" data-lid="front" aria-label="Open front lid" aria-pressed="false">Front lid</button><button type="button" data-lid="heat" aria-label="Open heating lid" aria-pressed="false">Heating lid</button><select class="machine-viewer__view" data-viewer-view aria-label="Machine view"><option value="perspective">Three-quarter</option><option value="front">Front</option><option value="right">Right · power</option><option value="rear">Rear · vent</option><option value="top">Above · heater</option></select><button class="machine-viewer__zoom" type="button" data-viewer-zoom="1.12" aria-label="Zoom out">−</button><button class="machine-viewer__zoom" type="button" data-viewer-zoom="0.89" aria-label="Zoom in">+</button></div>
<div class="machine-viewer__help" data-viewer-help id="machine-viewer-help" hidden>Drag to rotate · Use + / − to zoom<span class="sr-only" data-viewer-status role="status" aria-live="polite"></span></div></div><figcaption>3D concept · Final design and specifications may change.</figcaption></figure>'''

def home_product(product):
    return f'''<a class="product-preview" href="supplies.html?category={product['category']}"><div class="product-art"><img src="{versioned_asset('assets/illustrations/'+product['image']+'.svg')}" width="800" height="580" loading="lazy" alt="{escape(product['alt'],quote=True)}"></div><span class="supply-status" data-availability="{product['availability']}">{AVAILABILITY[product['availability']]}</span><h3>{escape(product['title'])}</h3><p>{escape(product['cta'])}</p></a>'''


home = f'''<section class="home-hero" aria-labelledby="home-title"><div class="hero-motion" data-hero-motion aria-hidden="true"></div><div class="hero-grid"><div class="hero-copy"><h1 id="home-title"><span class="hero-line">Advancing</span> <span class="hero-line">the future of</span> <span class="hero-line">peritoneal dialysis<span class="accent">.</span></span></h1><p>Explore the RYNOR automated peritoneal dialysis (APD) system in development, learn about home dialysis and check availability across our supply range.</p><div class="actions"><a class="button" href="machine.html">Explore our machine{icon('arrow-right')}</a><a class="text-link" href="supplies.html">View PD supplies{icon('arrow-right')}</a></div></div>{machine_preview}</div></section>
{status()}
<section class="section" aria-labelledby="range-title"><div class="container"><div class="section-top"><div><p class="eyebrow">The supply catalogue</p><h2 id="range-title">Explore our dialysis supply range.</h2></div><div class="section-intro"><p>CAPD fluid bags and tubing are not currently available. Explore transfer sets and the wider PD range, with each category’s status clearly labelled.</p><a class="text-link" href="supplies.html">Explore all supplies{icon('arrow-right')}</a></div></div><div class="home-products">{''.join(home_product(p) for p in PRODUCTS[:3])}</div><p class="concept-note">Technical illustrations. Actual products and packaging may vary. Confirm stock, specifications and pricing with RYNOR.</p></div></section>'''


home += '''
<section class="section tint-section" id="dialysis-at-home" aria-labelledby="home-dialysis-title"><div class="container two-column"><div class="copy-stack"><p class="eyebrow">For patients &amp; families</p><h2 id="home-dialysis-title">Understanding dialysis at home</h2><a class="button" href="pd-at-home.html">Learn about home dialysis →</a><p class="small-copy">The RYNOR APD machine is in development. CAPD fluid bags and tubing are not currently available.</p></div><div class="copy-stack"><p>Peritoneal dialysis can allow suitable patients to receive treatment at home. After a procedure to place a soft tube called a catheter in the abdomen, patients receive training to manage treatment themselves or with a caregiver. With ongoing support from their kidney-care team, many people can continue working and taking part in everyday activities.</p><p class="small-copy">Your kidney-care team will guide treatment suitability, diet, fluid limits and support needs.</p></div></div></section>'''

machine_detail_preview = machine_preview.replace('hero-figure machine-hero', 'hero-figure machine-hero machine-detail-viewer')
machine = heading('Our machine', 'A new perspective on peritoneal dialysis.', 'Meet the RYNOR automated peritoneal dialysis system: a device in development, with clinical trials as the next major milestone.') + f'''
{status(machine=True)}<section class="section"><div class="container machine-intro">{machine_detail_preview}<div class="copy-stack"><p class="eyebrow">The RYNOR system</p><h2>Explore the RYNOR machine concept.</h2><p>Our APD development programme brings together an automated peritoneal dialysis machine and dedicated supporting supplies. CAPD fluid bags and tubing are not currently available.</p><p>Rotate and zoom the 3D concept, open the front and heating lids, or select the side and rear views. The wide touchscreen stays fixed while each lid opens independently.</p><dl class="detail-rows"><div class="detail-row"><dt>Development stage</dt><dd>Preparing for clinical trials</dd></div><div class="detail-row"><dt>Product range</dt><dd>APD machine and dedicated supplies; PD supply catalogue</dd></div><div class="detail-row"><dt>Availability</dt><dd>APD machine: not currently for sale</dd></div></dl>{enquiry_link('Enquire about the machine','Our machine')}</div></div></section>
<section class="section tint-section"><div class="container two-column"><div class="copy-stack"><p class="eyebrow">Our development journey</p><h2>Progress, with a clear view of what comes next.</h2><p>We will share verified updates as the programme moves forward. A launch date and final product information will be announced when they are ready.</p>{enquiry_link('Discuss clinical collaboration','Clinical collaboration')}</div><ol class="stage-list"><li class="current"><span class="pill">Current stage</span><br><strong>Preparation for clinical trials</strong><p>The machine is in development and the team is preparing for the next stage of clinical evaluation.</p></li><li><strong>Clinical and regulatory milestones</strong><p>Evaluation and the required regulatory steps come before commercial availability. No certifications or approvals are claimed.</p></li><li><strong>A coordinated future launch</strong><p>The APD machine and its dedicated supply range are intended to launch together. CAPD fluid bags and tubing are not currently available.</p></li></ol></div></section>
<section class="section"><div class="container two-column"><div><p class="eyebrow">The supporting range</p><h2>A PD supply catalogue.<br>An APD system in development.</h2></div><div class="copy-stack"><p>CAPD fluid bags and tubing are not currently available. Explore transfer sets and the wider PD supply catalogue, or ask about our planned APD range.</p><a class="button" href="supplies.html">Explore supplies{icon('arrow-right')}</a></div></div></section>'''

def product_card(product):
    variants=''.join(f'<li>{escape(item)}</li>' for item in product['variants'])
    return f'''<article class="catalog-card" data-category="{product['category']}" data-availability="{product['availability']}" id="{product['category']}"><figure><img src="{versioned_asset('assets/illustrations/'+product['image']+'.svg')}" width="800" height="580" loading="lazy" alt="{escape(product['alt'],quote=True)}"><figcaption>Technical illustration · Actual packaging may vary</figcaption></figure><span class="supply-status" data-availability="{product['availability']}">{AVAILABILITY[product['availability']]}</span><h2>{escape(product['title'])}</h2><p>{escape(product['description'])}</p><ul class="variant-list" aria-label="Product details">{variants}</ul><div class="catalog-card-foot">{enquiry_link(escape(product['cta']),product['topic'])}</div></article>'''


filters=''.join(f'<button class="filter-button" type="button" data-filter="{value}" aria-pressed="{"true" if value=="all" else "false"}">{label}</button>' for value,label in [('all','All supplies'),('bags','Fluid bags'),('tubing','Tubing'),('transfer-sets','Transfer sets'),('catheters','Catheters'),('caps','Caps & accessories')])
supplies=heading('Supplies', 'Peritoneal dialysis supplies.', 'CAPD fluid bags and tubing are not currently available. Explore the catalogue or contact us to ask about future availability and other supply categories.')+f'''
<section class="section supply-catalog"><div class="container"><div class="catalog-tools"><div class="filters" role="group" aria-label="Filter supplies by category">{filters}</div><div class="catalog-search-row"><div class="field"><label for="catalog-availability">Availability</label><select id="catalog-availability" data-availability-filter><option value="all">All availability</option><option value="unavailable">Not currently available</option><option value="enquire">Check availability</option><option value="planned">In development</option></select></div><div class="field"><label for="catalog-search">Find a supply</label><input id="catalog-search" type="search" placeholder="Try fluid bags, tubing or transfer sets" autocomplete="off" aria-controls="supply-results"></div></div></div><p class="catalog-meta" data-catalog-count role="status">{len(PRODUCTS)} supply categories</p><div class="catalog-grid" id="supply-results">{''.join(product_card(p) for p in PRODUCTS)}</div><div class="empty-state" data-empty-state hidden><h2>No matching supplies.</h2><p>Clear your search or change the category and availability filters.</p><button class="button" type="button" data-reset-filters>Show all supplies</button></div><div class="supply-help"><div><p class="eyebrow">A little clarity</p><h2>Supply information.</h2><p>CAPD fluid bags and tubing are not currently available. Our team can answer availability questions; the website does not accept orders or payment.</p></div><div class="faq"><details><summary>Are CAPD bags and tubing available?</summary><p>No. CAPD fluid bags and tubing are not currently available. Use “Enquire about future availability” to ask RYNOR for updates; this is not an order or reservation.</p></details><details><summary>How do I confirm the right product?</summary><p>Ask your PD team to confirm the product and configuration you need, then check the exact pack details with RYNOR. The illustrations are not compatibility guides.</p></details><details><summary>Are transfer sets and the APD machine available?</summary><p>Contact us to confirm transfer-set availability. The RYNOR APD machine and its dedicated range remain in development and are not for sale.</p></details></div></div><p class="small-copy">CAPD fluid bags and tubing are not currently available. Other categories show their own status. Illustrations do not establish specifications or compatibility.</p></div></section>'''

about=heading('About RYNOR', 'Developing peritoneal dialysis technology.', 'RYNOR Medtech is developing an automated peritoneal dialysis machine and its dedicated supply range. CAPD fluid bags and tubing are listed in the catalogue but are not currently available.')+f'''
<section class="section"><div class="container"><p class="eyebrow">Our purpose</p><p class="about-statement">We are working towards a future where peritoneal dialysis technology and its supporting supplies are considered together, around the people who will use them.</p><div class="principles"><article class="principle"><h3>A complete perspective</h3><p>We support CAPD supply enquiries today while developing an APD machine and dedicated range for the future. Availability is stated separately for each product category.</p></article><article class="principle"><h3>A responsible progression</h3><p>Preparing for clinical trials is our current priority. Verified progress, clinical evaluation and regulatory milestones will guide the path to launch.</p></article><article class="principle"><h3>An open conversation</h3><p>We welcome questions and conversations with clinicians, hospitals, patients, distributors and prospective investors.</p></article></div></div></section>
<section class="section tint-section" id="partnerships"><div class="container two-column"><div class="copy-stack"><p class="eyebrow">Future partnerships</p><h2>Let’s build the right conversations.</h2><p>Every audience brings a different perspective. Contact us about the development programme, planned products or a potential future partnership.</p>{enquiry_link('Connect with RYNOR',css='button')}</div><ul class="audience-list"><li><strong>Doctors &amp; hospitals</strong><p>Discuss the programme, clinical collaboration and future product information.</p></li><li><strong>Patients &amp; families</strong><p>Ask about CAPD fluid bags and tubing, learn about PD, or follow our APD development plans. Personal treatment decisions belong with your care team.</p></li><li><strong>Distributors</strong><p>Introduce your organisation and discuss the planned range and potential future distribution.</p></li><li><strong>Investors</strong><p>Connect with the team for an introductory conversation about RYNOR Medtech.</p></li></ul></div></section>
<section class="section"><div class="container faq"><p class="eyebrow">A few clear answers</p><h2>Where we are today.</h2><details><summary>Is the RYNOR machine available to buy?</summary><p>No. The machine is in development and we are preparing for clinical trials. Commercial availability has not been announced.</p></details><details><summary>Can I order the supplies separately now?</summary><p>No. CAPD fluid bags and tubing are not currently available. Contact us for future availability updates. Transfer sets have a separate availability enquiry. The APD machine and its dedicated range remain in development.</p></details><details><summary>Do the images show the final products?</summary><p>Supply images are technical illustrations, not photographs of stock. Ask us for the actual product and pack details. The APD machine is a development concept and its final design may change.</p></details><details><summary>How can I contact the team?</summary><p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>, or use the enquiry button to {'send us a message' if FORM_ENDPOINT else 'prepare an email draft'}.</p></details></div></section>'''

CONTACT_INTRO = 'Choose phone or email, tell us what you need, and we’ll reply using that contact method.' if FORM_ENDPOINT else 'Choose a topic and write a short message. We’ll prepare a draft in your own email app.'
CONTACT_PRIVACY = '' if FORM_ENDPOINT else '<p class="contact-context">This website does not store your form entries. Your message is shared with RYNOR only when you send it through your email service. Please keep enquiries general and avoid including medical records or sensitive health information.</p>'

contact=heading('Contact', 'The right conversation<br>starts here.', 'For product enquiries, clinical collaboration, future distribution or investment conversations, connect with the RYNOR Medtech team.')+f'''
<section class="section"><div class="container contact-layout"><aside class="contact-card"><p class="eyebrow">Email RYNOR</p><h2>Let’s stay in touch.</h2><a class="email-display" href="mailto:{EMAIL}">{EMAIL.replace("@", "@<wbr>")}</a><button class="copy-email" type="button" data-copy-email>{icon('copy')}<span aria-live="polite">Copy email address</span></button><p class="small-copy">CAPD fluid bags and tubing are not currently available. Contact us for future availability updates, or ask about our APD development programme.</p><div class="contact-context"><p><strong>Product information</strong><br>CAPD fluid bags, CAPD tubing, transfer sets and the planned APD range.</p><p><strong>Collaboration</strong><br>Clinical discussions, distribution partnerships and investor enquiries.</p></div></aside><div><h2 class="form-title">What’s on your mind?</h2><p class="form-intro">{CONTACT_INTRO}</p>{email_form('contact')}{CONTACT_PRIVACY}<noscript><p>You can contact us directly at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></noscript></div></div></section>'''

pd_at_home = (ROOT/'content/pd-at-home.html').read_text(encoding='utf-8').replace('{{FORM_ENDPOINT}}', escape(FORM_ENDPOINT, quote=True))
privacy = (ROOT/'content/privacy.html').read_text(encoding='utf-8')

pages = [
('pd-at-home.html','PD at Home | Learn & Connect | RYNOR Medtech','Learn how APD works with a short animation and interactive guide. Patients, caregivers and doctors can register interest using one contact method.',pd_at_home),
('privacy.html','Contact Privacy | RYNOR Medtech','How RYNOR handles contact details submitted through supply enquiries, general messages and patient or doctor PD interest forms.',privacy),
('index.html','RYNOR Medtech | Advancing peritoneal dialysis','Explore the PD supply catalogue, enquire about transfer sets, learn about PD at home and explore the RYNOR APD machine in development. CAPD bags and tubing are not currently available.',home),
('machine.html','Our Machine | RYNOR Medtech','Explore the exterior concept and development stage of the RYNOR automated peritoneal dialysis machine, now preparing for clinical trials.',machine),
('supplies.html','CAPD Supplies & Transfer Sets | RYNOR Medtech','CAPD fluid bags and tubing are not currently available. Explore transfer sets and the wider PD catalogue, with clear availability information.',supplies),
('about.html','About RYNOR | RYNOR Medtech','Meet RYNOR Medtech and its APD machine development programme. CAPD fluid bags and tubing are not currently available.',about),
('contact.html','Contact | RYNOR Medtech','Contact RYNOR Medtech by email for product enquiries, clinical collaboration, distribution partnerships and investor discussions.',contact),
]

if __name__ == '__main__':
    for filename,title,description,content in pages:
        (ROOT/filename).write_text(page(filename,title,description,content),encoding='utf-8',newline='\r\n')
    (ROOT/'catalog.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Supplies | RYNOR Medtech</title><meta http-equiv="refresh" content="0;url=supplies.html"><link rel="canonical" href="https://www.rynormedtech.com/supplies.html"></head><body><p>Our catalog is now available on the <a href="supplies.html">supplies page</a>.</p></body></html>\n')
    urls=''.join(f'<url><loc>{ORIGIN}{"/" if filename=="index.html" else "/"+filename}</loc></url>' for filename,*_ in pages)
    (ROOT/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    (ROOT/'.nojekyll').touch()
    print(f'Built {len(pages)} website pages, catalog redirect, sitemap and robots.txt.')
