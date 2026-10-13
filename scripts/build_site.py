#!/usr/bin/env python3
"""Build the small, dependency-free GitHub Pages site from shared templates."""
from html import escape
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMAIL = 'syedkamran@rynormedtech.com'
ORIGIN = 'https://www.rynormedtech.com'
NAV = [('index.html', 'Home'), ('machine.html', 'Our Machine'), ('supplies.html', 'Supplies'), ('about.html', 'About'), ('contact.html', 'Contact')]
TOPICS = ['General enquiry', 'Our machine', 'Dialysis fluid bags', 'APD / CAPD tubing', 'Peritoneal dialysis catheters', 'Mini-caps & disinfection accessories', 'Clinical collaboration', 'Distribution partnership', 'Investor enquiry']


def versioned_asset(path):
    version = sha256((ROOT / path).read_bytes()).hexdigest()[:12]
    return f'{path}?v={version}'


def icon(name):
    return f'<img class="icon" src="assets/icons/{name}.svg" width="20" height="20" alt="" aria-hidden="true">'


def brand():
    return '<a class="brand" href="./" aria-label="RYNOR Medtech home"><img src="assets/brand/rynor-logo.svg" width="6912" height="3456" alt="RYNOR Medtech"></a>'


def header(current):
    links = ''.join(f'<a class="nav-link{" nav-contact" if href == "contact.html" else ""}" href="{"./" if href == "index.html" else href}" {"aria-current=\"page\"" if href == current else ""}>{label}</a>' for href, label in NAV)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner">{brand()}
<button class="menu-toggle" type="button" data-menu-toggle aria-controls="primary-nav" aria-expanded="false" aria-label="Open navigation">{icon('list')}</button>
<nav class="primary-nav" id="primary-nav" aria-label="Primary navigation">{links}</nav></div></header>'''


def enquiry_link(label='Product enquiries', topic='General enquiry', css='text-link'):
    return f'<a class="{css}" href="contact.html" data-enquiry="{escape(topic, quote=True)}">{label}{icon("arrow-right")}</a>'


def status():
    return f'''<div class="status-strip"><div class="container status-inner"><p class="status-heading">{icon('hourglass-split')}<span>Preparing for clinical trials</span></p><p class="status-description">Machine and supplies in development. Not yet available for sale.</p></div></div>'''


def email_form(prefix):
    options = ''.join(f'<option value="{escape(topic, quote=True)}">{escape(topic)}</option>' for topic in TOPICS)
    return f'''<form data-email-form action="mailto:{EMAIL}" method="get">
<div class="field-row"><div class="field"><label for="{prefix}-name">Your name <span class="optional">(optional)</span></label><input id="{prefix}-name" name="name" autocomplete="name" maxlength="100"></div>
<div class="field"><label for="{prefix}-email">Your email <span class="optional">(optional)</span></label><input id="{prefix}-email" name="email" type="email" autocomplete="email" maxlength="180"></div></div>
<div class="field"><label for="{prefix}-topic">What would you like to discuss?</label><select id="{prefix}-topic" name="topic">{options}</select></div>
<div class="field"><label for="{prefix}-message">Your message</label><textarea id="{prefix}-message" name="message" rows="4" required maxlength="1800" placeholder="Tell us about your enquiry or organisation."></textarea></div>
<button class="button" type="submit">Open email draft{icon('arrow-up-right')}</button>
<p class="form-note">This opens your email app. Review the draft and send it there. Nothing is sent automatically.</p>
<div class="draft-status" data-draft-status role="status" hidden>Your email draft is ready. If your email app did not open, <a href="mailto:{EMAIL}" target="_blank" rel="noopener noreferrer">open the draft again</a> or email <strong>{EMAIL}</strong> directly.</div>
</form>'''


def footer():
    links = ''.join(f'<a href="{href}">{label}</a>' for href, label in NAV[1:])
    return f'''<section class="contact-band" aria-label="Contact Rynor"><div class="container contact-band-inner"><div><h2>Let’s start a conversation.</h2><p>For product enquiries, clinical collaboration and future partnerships.</p></div><a class="contact-email" href="mailto:{EMAIL}">{icon('envelope')}<span>{EMAIL}</span></a>{enquiry_link('Enquire', css='button button-light')}</div></section>
<footer class="site-footer"><div class="container"><div class="footer-top">{brand()}<nav class="footer-links" aria-label="Footer navigation">{links}</nav></div><div class="footer-bottom"><span>© 2026 RYNOR Medtech.</span><p>Machine and supplies are in development and are not yet available for sale. Product visuals are concept illustrations; final designs and specifications may change.</p></div></div></footer>
<a class="floating-enquiry" href="contact.html" data-enquiry="General enquiry" aria-label="Open email enquiry">{icon('chat-dots')}<span>Enquire</span></a>
<dialog class="enquiry-dialog" id="enquiry-dialog" aria-labelledby="enquiry-title"><div class="dialog-header"><div><p class="eyebrow">Contact RYNOR</p><h2 id="enquiry-title">Let’s talk.</h2></div><button type="button" class="dialog-close" data-dialog-close aria-label="Close enquiry">{icon('x-lg')}</button></div><p class="small-copy">Start a conversation with our team by email.</p><a class="dialog-address" href="mailto:{EMAIL}">{EMAIL}</a>{email_form('dialog')}</dialog>'''


def page(filename, title, description, content):
    canonical = ORIGIN + ('/' if filename == 'index.html' else '/' + filename)
    image_preload = '<link rel="preload" as="image" href="assets/images/machine-concept.webp" fetchpriority="high">' if filename == 'index.html' else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#06264b">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="RYNOR Medtech"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/images/machine-concept.webp"><meta property="og:image:alt" content="Exterior concept illustration of the RYNOR peritoneal dialysis machine">
<link rel="icon" type="image/svg+xml" href="assets/brand/rynor-logo-square.svg"><link rel="preload" href="assets/fonts/manrope-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>{image_preload}<link rel="stylesheet" href="{versioned_asset("assets/site.css")}"><script>document.documentElement.classList.add('js');</script><script src="{versioned_asset("assets/site.js")}" defer></script></head>
<body>{header(filename)}<main id="main">{content}</main>{footer()}</body></html>
'''


def heading(label, title, description):
    return f'''<section class="page-heading"><div class="container"><div class="breadcrumbs"><a href="./">Home</a>{icon('arrow-right')}<span>{label}</span></div><p class="eyebrow">{label}</p><h1>{title}</h1><p>{description}</p></div></section>'''


home = f'''<section class="home-hero" aria-labelledby="home-title"><div class="hero-grid"><div class="hero-copy"><h1 id="home-title"><span class="hero-line">Advancing</span> <span class="hero-line">the future of</span> <span class="hero-line">peritoneal dialysis<span class="accent">.</span></span></h1><p>We are developing an automated peritoneal dialysis system and a complete planned supply range, with a clear focus on the next stage: clinical trials.</p><div class="actions"><a class="button" href="machine.html">Explore our machine{icon('arrow-right')}</a>{enquiry_link()}</div></div><figure class="hero-figure"><img src="assets/images/machine-concept.webp" width="1374" height="1145" fetchpriority="high" alt="Exterior concept of the RYNOR machine, with a wide front display and closed lid"><figcaption>Concept illustration</figcaption></figure></div></section>
{status()}
<section class="section" aria-labelledby="range-title"><div class="container"><div class="section-top"><div><p class="eyebrow">Planned product range</p><h2 id="range-title">A planned range, designed around peritoneal dialysis.</h2></div><div class="section-intro"><p>Our machine and supplies are being developed as one future range. Fluid bags, tubing, catheters and accessories are planned to launch together with the machine.</p><a class="text-link" href="supplies.html">Explore supplies{icon('arrow-right')}</a></div></div><div class="home-products">
<a class="product-preview" href="supplies.html?category=bags"><div class="product-art"><img src="assets/images/bags-concept.webp" width="1448" height="1086" loading="lazy" alt="Concept RYNOR dialysis fluid bags in 2 litre and 5 litre sizes"></div><h3>Dialysis fluid bags</h3><p>2 L / 5 L</p></a>
<a class="product-preview" href="supplies.html?category=tubing"><div class="product-art"><img src="assets/images/tubing-concept.webp" width="1448" height="1086" loading="lazy" alt="Concept clear dialysis tubing with blue connector accents"></div><h3>APD / CAPD tubing</h3><p>Planned tubing range</p></a>
<a class="product-preview" href="supplies.html?category=catheters"><div class="product-art"><img src="assets/images/accessories-concept.webp" width="1448" height="1086" loading="lazy" alt="Concept RYNOR catheters, packaging and mini-caps"></div><h3>Catheters &amp; accessories</h3><p>Planned product range</p></a></div><p class="concept-note">Concept illustrations. Final product designs may change.</p></div></section>'''

machine = heading('Our machine', 'A new perspective on peritoneal dialysis.', 'Meet the RYNOR automated peritoneal dialysis system: a device in development, with clinical trials as the next major milestone.') + f'''
{status()}<section class="section"><div class="container machine-intro"><figure class="machine-photo"><img src="assets/images/machine-concept.webp" width="1374" height="1145" alt="RYNOR machine exterior concept, showing a wide LCD and a closed front lid"><figcaption>Exterior concept illustration. Final design may change.</figcaption></figure><div class="copy-stack"><p class="eyebrow">The RYNOR system</p><h2>A clear vision.<br>A considered exterior.</h2><p>Our development programme brings together an automated peritoneal dialysis machine and a planned range of supporting supplies.</p><p>The exterior concept features a wide front display and a closed front lid. This preview introduces the product’s visual direction while development continues.</p><dl class="detail-rows"><div class="detail-row"><dt>Development stage</dt><dd>Preparing for clinical trials</dd></div><div class="detail-row"><dt>Product range</dt><dd>Machine, fluid bags, tubing, catheters and accessories</dd></div><div class="detail-row"><dt>Availability</dt><dd>Planned future launch; not currently available for sale</dd></div></dl>{enquiry_link('Enquire about the machine','Our machine')}</div></div></section>
<section class="section tint-section"><div class="container two-column"><div class="copy-stack"><p class="eyebrow">Our development journey</p><h2>Progress, with a clear view of what comes next.</h2><p>We will share verified updates as the programme moves forward. A launch date and final product information will be announced when they are ready.</p>{enquiry_link('Discuss clinical collaboration','Clinical collaboration')}</div><ol class="stage-list"><li class="current"><span class="pill">Current stage</span><br><strong>Preparation for clinical trials</strong><p>The machine is in development and the team is preparing for the next stage of clinical evaluation.</p></li><li><strong>Clinical and regulatory milestones</strong><p>Evaluation and the required regulatory steps come before commercial availability. No certifications or approvals are claimed.</p></li><li><strong>A coordinated future launch</strong><p>The machine and planned supply range are intended to launch together. Timing will be communicated as the programme progresses.</p></li></ol></div></section>
<section class="section"><div class="container two-column"><div><p class="eyebrow">The supporting range</p><h2>One machine.<br>A complete planned range.</h2></div><div class="copy-stack"><p>Explore 2 L and 5 L dialysis fluid bags, APD and CAPD tubing, peritoneal dialysis catheters, mini-caps and disinfection accessories.</p><a class="button" href="supplies.html">Explore planned supplies{icon('arrow-right')}</a></div></div></section>'''

PRODUCTS = [
    dict(category='bags', title='Dialysis fluid bags', image='bags', alt='Concept RYNOR 2 L and 5 L dialysis fluid bags', description='Two planned bag sizes within the RYNOR peritoneal dialysis range. Product details and final packaging will be shared before launch.', variants=['2 L','5 L'], topic='Dialysis fluid bags'),
    dict(category='tubing', title='APD & CAPD tubing', image='tubing', alt='Concept coiled peritoneal dialysis tubing', description='A planned tubing range covering automated peritoneal dialysis (APD) and continuous ambulatory peritoneal dialysis (CAPD). Final configurations will be confirmed during development.', variants=['APD tubing','CAPD tubing'], topic='APD / CAPD tubing'),
    dict(category='catheters', title='Peritoneal dialysis catheters', image='accessories', alt='Concept catheter range with RYNOR packaging and accessories', description='The planned catheter portfolio includes swan-neck and curled variants. Final combinations, sizes and product specifications will be confirmed before launch.', variants=['Swan-neck variants','Curled variants'], topic='Peritoneal dialysis catheters'),
    dict(category='caps', title='Mini-caps & disinfection accessories', image='accessories', alt='Concept RYNOR accessory range, including blue and white caps', description='Mini-caps and related disinfection accessories are part of the planned supporting range. Final products and packaging remain in development.', variants=['Mini-caps','Disinfection accessories'], topic='Mini-caps & disinfection accessories'),
]


def product_card(product):
    variants=''.join(f'<li>{escape(item)}</li>' for item in product['variants'])
    return f'''<article class="catalog-card" data-category="{product['category']}" id="{product['category']}"><figure><img src="assets/images/{product['image']}-concept.webp" width="1448" height="1086" loading="lazy" alt="{escape(product['alt'],quote=True)}"><figcaption>Concept illustration</figcaption></figure><p class="eyebrow">Planned for launch with the machine</p><h2>{escape(product['title'])}</h2><p>{product['description']}</p><ul class="variant-list" aria-label="Planned variants">{variants}</ul><div class="catalog-card-foot">{enquiry_link('Product enquiry',product['topic'])}</div></article>'''


filters=''.join(f'<button class="filter-button" type="button" data-filter="{value}" aria-pressed="{"true" if value=="all" else "false"}">{label}</button>' for value,label in [('all','All supplies'),('bags','Fluid bags'),('tubing','Tubing'),('catheters','Catheters'),('caps','Caps & accessories')])
supplies=heading('Supplies', 'A complete planned range.', 'Dialysis fluid bags, tubing, catheters and accessories—planned to launch together with the RYNOR machine.')+f'''
<section class="section"><div class="container"><div class="catalog-tools"><div class="filters" role="group" aria-label="Filter supplies by category">{filters}</div><div class="search-field"><label class="sr-only" for="catalog-search">Search planned supplies</label>{icon('search')}<input id="catalog-search" type="search" placeholder="Search supplies" autocomplete="off"></div></div><p class="catalog-meta" data-catalog-count aria-live="polite">4 planned product categories</p><div class="catalog-grid">{''.join(product_card(p) for p in PRODUCTS)}</div><div class="empty-state" data-empty-state hidden><h2>No matching supplies.</h2><p>Try a different search or view the complete planned range.</p><button class="button" type="button" data-reset-filters>Show all supplies</button></div><div class="future-range"><div><p class="eyebrow">Looking ahead</p><h2>Other medical devices</h2><p>We are also exploring future medical device categories. We will introduce new products when there are confirmed details to share.</p></div>{enquiry_link('Discuss the future range')}</div><p class="small-copy">The complete range is in development and is not yet available for sale. Illustrations show design concepts, not final product specifications or compatibility guidance.</p></div></section>'''

about=heading('About RYNOR', 'A shared purpose.<br>A considered path forward.', 'RYNOR Medtech is developing a peritoneal dialysis machine and supporting supplies, with a focus on the next stage of clinical evaluation.')+f'''
<section class="section"><div class="container"><p class="eyebrow">Our purpose</p><p class="about-statement">We are working towards a future where peritoneal dialysis technology and its supporting supplies are considered together, around the people who will use them.</p><div class="principles"><article class="principle"><h3>A complete perspective</h3><p>Our development plans bring the machine, dialysis fluid bags, tubing, catheters and accessories into one coordinated future range.</p></article><article class="principle"><h3>A responsible progression</h3><p>Preparing for clinical trials is our current priority. Verified progress, clinical evaluation and regulatory milestones will guide the path to launch.</p></article><article class="principle"><h3>An open conversation</h3><p>We welcome questions and conversations with clinicians, hospitals, patients, distributors and prospective investors.</p></article></div></div></section>
<section class="section tint-section" id="partnerships"><div class="container two-column"><div class="copy-stack"><p class="eyebrow">Future partnerships</p><h2>Let’s build the right conversations.</h2><p>Every audience brings a different perspective. Contact us about the development programme, planned products or a potential future partnership.</p>{enquiry_link('Connect with RYNOR',css='button')}</div><ul class="audience-list"><li><strong>Doctors &amp; hospitals</strong><p>Discuss the programme, clinical collaboration and future product information.</p></li><li><strong>Patients &amp; families</strong><p>Ask about our development plans. Products are not yet available; personal treatment questions should be discussed with your care team.</p></li><li><strong>Distributors</strong><p>Introduce your organisation and discuss the planned range and potential future distribution.</p></li><li><strong>Investors</strong><p>Connect with the team for an introductory conversation about RYNOR Medtech.</p></li></ul></div></section>
<section class="section"><div class="container faq"><p class="eyebrow">A few clear answers</p><h2>Where we are today.</h2><details><summary>Is the RYNOR machine available to buy?</summary><p>No. The machine is in development and we are preparing for clinical trials. Commercial availability has not been announced.</p></details><details><summary>Can I order the supplies separately now?</summary><p>The entire supply range is planned to launch together with the machine. None of the products shown are currently offered for sale.</p></details><details><summary>Do the images show the final products?</summary><p>The product images on this website are concept illustrations. The final appearance, packaging and specifications may change during development.</p></details><details><summary>How can I contact the team?</summary><p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>, or use the enquiry button to prepare an email draft.</p></details></div></section>'''

contact=heading('Contact', 'The right conversation<br>starts here.', 'For product enquiries, clinical collaboration, future distribution or investment conversations, connect with the RYNOR Medtech team by email.')+f'''
<section class="section"><div class="container contact-layout"><aside class="contact-card"><p class="eyebrow">Email RYNOR</p><h2>Let’s stay in touch.</h2><a class="email-display" href="mailto:{EMAIL}">{EMAIL.replace("@", "@<wbr>")}</a><button class="copy-email" type="button" data-copy-email>{icon('copy')}<span aria-live="polite">Copy email address</span></button><p class="small-copy">Our machine and supplies are in development. We welcome enquiries about the planned range and future partnerships.</p><div class="contact-context"><p><strong>Product information</strong><br>Machine, dialysis fluid bags, APD / CAPD tubing, catheters and accessories.</p><p><strong>Collaboration</strong><br>Clinical discussions, distribution partnerships and investor enquiries.</p></div></aside><div><h2 class="form-title">What’s on your mind?</h2><p class="form-intro">Choose a topic and write a short message. We’ll prepare a draft in your own email app.</p>{email_form('contact')}<p class="contact-context">This website does not store your form entries. Your message is shared with RYNOR only when you send it through your email service. Please keep enquiries general and avoid including medical records or sensitive health information.</p><noscript><p>You can contact us directly at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></noscript></div></div></section>'''

pages = [
('index.html','RYNOR Medtech | Advancing peritoneal dialysis','Discover the RYNOR peritoneal dialysis machine and planned supply range. Preparing for clinical trials. Product and partnership enquiries by email.',home),
('machine.html','Our Machine | RYNOR Medtech','Explore the exterior concept and development stage of the RYNOR automated peritoneal dialysis machine, now preparing for clinical trials.',machine),
('supplies.html','Planned Supplies | RYNOR Medtech','Explore planned 2 L and 5 L dialysis fluid bags, APD and CAPD tubing, catheters, mini-caps and accessories from RYNOR Medtech.',supplies),
('about.html','About RYNOR | RYNOR Medtech','Meet RYNOR Medtech: developing a peritoneal dialysis machine and planned supplies, with clinical trials ahead.',about),
('contact.html','Contact | RYNOR Medtech','Contact RYNOR Medtech by email for product enquiries, clinical collaboration, distribution partnerships and investor discussions.',contact),
]

if __name__ == '__main__':
    for filename,title,description,content in pages:
        (ROOT/filename).write_text(page(filename,title,description,content),encoding='utf-8')
    (ROOT/'catalog.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Supplies | RYNOR Medtech</title><meta http-equiv="refresh" content="0;url=supplies.html"><link rel="canonical" href="https://www.rynormedtech.com/supplies.html"></head><body><p>Our catalog is now available on the <a href="supplies.html">planned supplies page</a>.</p></body></html>\n')
    urls=''.join(f'<url><loc>{ORIGIN}{"/" if filename=="index.html" else "/"+filename}</loc></url>' for filename,*_ in pages)
    (ROOT/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    (ROOT/'.nojekyll').touch()
    print('Built 5 website pages, catalog redirect, sitemap and robots.txt.')
