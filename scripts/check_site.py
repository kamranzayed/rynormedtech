#!/usr/bin/env python3
"""Meaningful browser smoke checks for the static site. Requires Playwright + Chromium."""
import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8001')
parser.add_argument('--output', default='/workspace/rynor-design/qa')
parser.add_argument('--axe', default='/workspace/rynor-design/qa/axe.min.js')
args = parser.parse_args()
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)
checks = []
axe_results = []
pages = ['index', 'machine', 'supplies', 'about', 'contact', 'pd-at-home', 'privacy']


def passed(name):
    checks.append(name)
    print('PASS:', name, flush=True)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True)
    context = browser.new_context(viewport={'width':1440,'height':1100})
    page = context.new_page()
    errors = []
    failed_http = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: failed_http.append((response.status,response.url)) if response.status>=400 else None)

    for name in pages:
        response = page.goto(f'{args.base_url}/{name}.html', wait_until='networkidle')
        assert response.status == 200
        expect(page.locator('main h1')).to_have_count(1)
        assert page.locator('html').get_attribute('lang') == 'en'
        assert page.locator('head meta[name="description"]').get_attribute('content')
        assert page.locator('img:not([loading=lazy])').evaluate_all('(items)=>items.every(i=>i.complete && i.naturalWidth>0)')
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
        nav_href = './' if name == 'index' else f'{name}.html'
        if name != 'privacy':
            expect(page.locator(f'.primary-nav a[href="{nav_href}"]')).to_have_attribute('aria-current','page')
        local_links = page.locator('a[href]').evaluate_all('(items)=>[...new Set(items.map(i=>i.getAttribute("href")).filter(h=>h && !/^(mailto:|https?:|#)/.test(h)))]')
        for href in local_links:
            assert context.request.get(f'{args.base_url}/{href}').status == 200, href
        page.screenshot(path=str(out/f'{name}-desktop.png'), full_page=True)
        if Path(args.axe).exists():
            page.add_script_tag(path=args.axe)
            result = page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}})')
            violations = [{'id':v['id'],'impact':v['impact'],'description':v['description'],'nodes':[{'target':n['target'],'summary':n.get('failureSummary')} for n in v['nodes']]} for v in result['violations']]
            axe_results.append({'page':name,'violations':violations,'passes':len(result['passes'])})
        passed(f'{name}: content, metadata, active navigation, loaded assets and local links')

    page.goto(f'{args.base_url}/machine.html')
    page.locator('.primary-nav').get_by_role('link', name='Home', exact=True).click()
    expect(page).to_have_url(f'{args.base_url}/')
    page.goto(f'{args.base_url}/contact.html')
    page.locator('.site-footer .brand').click()
    expect(page).to_have_url(f'{args.base_url}/')
    passed('Home and logo navigation use the clean homepage address')

    page.goto(f'{args.base_url}/supplies.html',wait_until='networkidle')
    expect(page.locator('[data-category]:visible')).to_have_count(5)
    for category in ['bags','tubing','transfer-sets','catheters','caps']:
        page.locator(f'[data-filter="{category}"]').click()
        expect(page.locator('[data-category]:visible')).to_have_count(1)
        expect(page.locator(f'[data-category="{category}"]')).to_be_visible()
    page.locator('[data-filter="all"]').click()
    page.get_by_label('Find a supply').fill('Swan-neck')
    expect(page.locator('[data-category]:visible')).to_have_count(1)
    expect(page.locator('[data-category="catheters"]')).to_be_visible()
    for query,category in [('swan neck','catheters'),('CAPD fluid','bags'),('transfer set','transfer-sets'),('CAPD tubing','tubing'),('  MINI CAPs  ','caps')]:
        page.get_by_label('Find a supply').fill(query)
        expect(page.locator('[data-category]:visible')).to_have_count(1)
        expect(page.locator(f'[data-category="{category}"]')).to_be_visible()
    page.get_by_label('Find a supply').fill('zzzz-no-product')
    expect(page.locator('[data-category]:visible')).to_have_count(0)
    expect(page.locator('[data-empty-state]')).to_be_visible()
    page.get_by_role('button',name='Show all supplies').click()
    expect(page.locator('[data-category]:visible')).to_have_count(5)
    passed('Catalog category filters, search, empty state and reset')

    page.goto(f'{args.base_url}/supplies.html?category=tubing',wait_until='networkidle')
    expect(page.locator('[data-category]:visible')).to_have_count(1)
    page.locator('[data-category="tubing"] [data-enquiry]').click()
    expect(page.locator('dialog')).to_be_visible()
    expect(page.locator('#dialog-topic')).to_have_value('CAPD tubing')
    for _ in range(12):
        page.keyboard.press('Tab')
        assert page.evaluate('!!document.activeElement.closest("dialog")')
    page.keyboard.press('Escape')
    expect(page.locator('dialog')).not_to_be_visible()
    expect(page.locator('[data-category="tubing"] [data-enquiry]')).to_be_focused()
    passed('Category deep link and product-specific enquiry; modal keyboard trapping and Escape')

    page.goto(f'{args.base_url}/contact.html',wait_until='networkidle')
    form = page.locator('main [data-email-form]')
    if form.get_attribute('data-direct-send') is not None:
        submitted = []
        def accept_enquiry(route):
            submitted.append(route.request.post_data)
            route.fulfill(status=200, json={'ok': True})
        context.route('https://formspree.io/**', accept_enquiry)
        expect(form.locator('[name=email]')).to_have_attribute('required', '')
        form.locator('[name=email]').fill('check@example.com')
        form.locator('[name=message]').fill('   ')
        form.get_by_role('button', name='Send enquiry').click()
        assert not submitted
        form.locator('[name=message]').fill('A planned supply enquiry')
        form.get_by_role('button', name='Send enquiry').click()
        expect(form.locator('[role=status]')).to_contain_text('Your enquiry has been submitted')
        assert len(submitted) == 1 and 'check@example.com' in submitted[0]
        expect(form.locator('[name=message]')).to_have_value('')
        passed('Direct enquiry validation and inline success with simulated provider; no email sent')
    else:
        form.get_by_role('button',name='Open email draft').click()
        expect(page.locator('#contact-message')).to_be_focused()
        expect(form.locator('[data-draft-status]')).not_to_be_visible()
        page.locator('#contact-message').fill('   \n   ')
        form.get_by_role('button',name='Open email draft').click()
        expect(form.locator('[data-draft-status]')).not_to_be_visible()
        assert page.locator('#contact-message').evaluate('(field)=>!field.validity.valid')
        page.locator('#contact-message').fill('A product enquiry')
        assert page.locator('#contact-message').evaluate('(field)=>field.validity.valid')
        page.locator('#contact-email').fill('invalid-address')
        form.get_by_role('button',name='Open email draft').click()
        expect(page.locator('#contact-email')).to_be_focused()
        expect(form.locator('[data-draft-status]')).not_to_be_visible()
        page.locator('#contact-name').fill('Website smoke check')
        page.locator('#contact-email').fill('check@example.com')
        page.locator('#contact-topic').select_option('Distribution partnership')
        message = 'Please discuss the planned range. Special text: & + ? # %\nSecond line.'
        page.locator('#contact-message').fill(message)
        form.get_by_role('button',name='Open email draft').click()
        expect(form.locator('[data-draft-status]')).to_be_visible()
        mailto=form.locator('[data-draft-status] a').get_attribute('href')
        uri=urlsplit(mailto)
        assert uri.scheme=='mailto' and uri.path=='syedkamran@rynormedtech.com'
        query=parse_qs(uri.query)
        assert query['subject']==['RYNOR Medtech — Distribution partnership']
        assert message in query['body'][0] and 'check@example.com' in query['body'][0]
        assert 'Nothing is sent automatically.' in form.inner_text()
        page.locator('#contact-message').fill('Updated enquiry')
        expect(form.locator('[data-draft-status]')).not_to_be_visible()
        passed('Contact validation and correctly encoded email draft; no message sent')

    page.goto(f'{args.base_url}/about.html')
    page.get_by_text('Can I order the supplies separately now?',exact=True).click()
    expect(page.locator('details[open]')).to_contain_text('CAPD fluid bags and tubing are available for sale separately.')
    passed('FAQ disclosure interaction')

    for width,height in [(1024,768),(768,1024),(414,896),(390,844),(375,812),(320,700)]:
        page.set_viewport_size({'width':width,'height':height})
        for name in pages:
            page.goto(f'{args.base_url}/{name}.html',wait_until='networkidle')
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),f'{name}: overflow at {width}'
            if width==390:
                page.screenshot(path=str(out/f'{name}-mobile.png'),full_page=True)
        passed(f'All seven pages fit {width}px viewport without horizontal overflow')
    page.set_viewport_size({'width':390,'height':844})
    page.goto(f'{args.base_url}/index.html')
    toggle=page.get_by_role('button',name='Open navigation')
    expect(page.locator('.primary-nav')).not_to_be_visible()
    toggle.click()
    expect(page.locator('.primary-nav')).to_be_visible()
    page.locator('.primary-nav').get_by_role('link',name='Supplies',exact=True).click()
    expect(page).to_have_url(f'{args.base_url}/supplies.html')
    expect(page.locator('.primary-nav')).not_to_be_visible()
    page.get_by_role('link',name='Open enquiry').click()
    expect(page.locator('dialog')).to_be_visible()
    assert page.locator('dialog').bounding_box()['width'] <= 390
    page.screenshot(path=str(out/'enquiry-mobile.png'),full_page=False)
    page.get_by_role('button',name='Close enquiry').click()
    passed('Mobile navigation, page transition and enquiry dialog')

    for device in ['iPhone 13', 'Pixel 7']:
        phone_context = browser.new_context(**p.devices[device])
        phone_page = phone_context.new_page()
        phone_page.goto(f'{args.base_url}/',wait_until='networkidle')
        expect(phone_page.locator('main h1')).to_be_visible()
        phone_page.get_by_role('button',name='Open navigation').tap()
        phone_page.locator('.primary-nav').get_by_role('link',name='Supplies',exact=True).tap()
        expect(phone_page).to_have_url(f'{args.base_url}/supplies.html')
        phone_page.locator('[data-filter="bags"]').tap()
        expect(phone_page.locator('[data-category]:visible')).to_have_count(1)
        phone_page.locator('[data-category="bags"] [data-enquiry]').tap()
        expect(phone_page.locator('dialog')).to_be_visible()
        expect(phone_page.locator('#dialog-topic')).to_have_value('CAPD fluid bags')
        phone_page.get_by_role('button',name='Close enquiry').tap()
        expect(phone_page.locator('dialog')).not_to_be_visible()
        phone_context.close()
        passed(f'{device}: touch navigation, product filters and enquiry (Chromium emulation)')

    page.goto(f'{args.base_url}/catalog.html',wait_until='networkidle')
    expect(page).to_have_url(f'{args.base_url}/supplies.html')
    passed('Legacy catalog URL reaches the new supplies page')

    assert not errors, errors
    assert not failed_http, failed_http
    passed('No JavaScript runtime errors or failed HTTP requests')
    report={'checks_passed':len(checks),'checks':checks,'axe':axe_results,'javascript_errors':errors,'failed_http':failed_http}
    (out/'checks.json').write_text(json.dumps(report,indent=2))
    browser.close()
    violations=sum(len(r['violations']) for r in axe_results)
    accessibility_summary = f'{violations} accessibility rule violations across {len(axe_results)} pages' if axe_results else 'accessibility scan not run (axe-core not supplied)'
    print(f'{len(checks)} functional checks passed; {accessibility_summary}.')
    assert not violations, 'See checks.json for accessibility findings'
