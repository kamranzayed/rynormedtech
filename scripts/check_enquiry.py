#!/usr/bin/env python3
"""Exercise real generated direct-send forms against intercepted responses; never send email."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='/tmp/rynor-enquiry-qa')
parser.add_argument('--axe', default='/workspace/rynor-design/qa/axe.min.js')
args = parser.parse_args()
output = Path(args.output)
output.mkdir(parents=True, exist_ok=True)


def check_accessibility(page):
    if Path(args.axe).is_file():
        page.add_script_tag(path=args.axe)
        violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
        assert not violations, violations
    else:
        print('SKIP: axe accessibility scan (local axe script unavailable)')


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


with tempfile.TemporaryDirectory(prefix='rynor-form-check-') as temp:
    fixture = Path(temp)
    (fixture / 'scripts').mkdir()
    shutil.copy(ROOT / 'scripts/build_site.py', fixture / 'scripts/build_site.py')
    (fixture / 'assets').symlink_to(ROOT / 'assets', target_is_directory=True)
    shutil.copytree(ROOT / 'content', fixture / 'content')
    (fixture / 'site-config.json').write_text(json.dumps({'formspree_endpoint': 'https://formspree.io/f/testfixture'}))
    subprocess.run(['python3', str(fixture / 'scripts/build_site.py')], check=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=temp))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True)
            context = browser.new_context(reduced_motion='reduce')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            requests = []
            outcome = {'status': 200, 'body': {'ok': True}, 'abort': False, 'hold': False}
            held = []

            def intercept(route):
                requests.append(route.request)
                if outcome['hold']:
                    held.append(route)
                elif outcome['abort']:
                    route.abort('failed')
                else:
                    route.fulfill(status=outcome['status'], json=outcome['body'])

            # All requests to the email provider are intercepted, including unexpected URLs.
            context.route('https://formspree.io/**', intercept)
            page.goto(f'{base}/contact.html')
            check_accessibility(page)
            page.screenshot(path=str(output / 'direct-contact.png'), full_page=True)
            form = page.locator('main [data-direct-send]')
            button = form.get_by_role('button', name='Send enquiry')
            status = form.locator('[role=status]')
            button.click()
            expect(form.locator('[name=email]')).to_be_focused()
            form.locator('[name=email]').fill('invalid')
            form.locator('[name=message]').fill('Hello')
            button.click()
            assert not requests
            form.locator('[name=email]').fill('check@example.com')
            form.locator('[name=message]').fill('  \n ')
            button.click()
            assert not requests
            expect(form.locator('[name=message]')).to_be_focused()
            print('PASS: required email, email format and whitespace-only message validation')

            message = 'Planned supplies & clinical discussions + ? # %\nSecond line.'
            form.locator('[name=name]').fill(' Test visitor ')
            form.locator('[name=message]').fill(message)
            form.locator('[name=topic]').select_option('Clinical collaboration')
            outcome['hold'] = True
            button.click()
            expect(form.locator('[type=submit]')).to_be_disabled()
            expect(status).to_contain_text('Sending your enquiry')
            form.evaluate("form => form.dispatchEvent(new Event('submit', {cancelable:true, bubbles:true}))")
            assert len(requests) == 1
            body = requests[0].post_data
            assert 'check@example.com' in body and 'Test visitor' in body
            assert 'Clinical collaboration' in body and 'Planned supplies & clinical discussions + ? # %' in body
            assert requests[0].method == 'POST'
            held.pop().fulfill(status=200, json={'ok': True})
            outcome['hold'] = False
            expect(status).to_contain_text('Your enquiry has been submitted')
            expect(form.locator('[name=message]')).to_have_value('')
            expect(button).to_be_enabled()
            assert len(context.pages) == 1
            print('PASS: inline submission, payload, loading state, duplicate prevention and confirmed success')

            for failure in ['server', 'rejected', 'network']:
                outcome.update(status=500 if failure == 'server' else 200,
                               body={'ok': False}, abort=failure == 'network')
                form.locator('[name=email]').fill('check@example.com')
                form.locator('[name=message]').fill(message)
                button.click()
                expect(status).to_contain_text('couldn’t confirm')
                expect(form.locator('[name=message]')).to_have_value(message)
                expect(form.locator('[name=email]')).to_have_value('check@example.com')
                expect(button).to_be_enabled()
            print('PASS: server rejection and connection failure retain the message and allow retry')
            outcome.update(status=200, body={'ok': True}, abort=False)
            button.click()
            expect(status).to_contain_text('Your enquiry has been submitted')
            print('PASS: retry succeeds without leaving the website')

            page.set_viewport_size({'width': 390, 'height': 844})
            page.goto(f'{base}/supplies.html?category=tubing')
            page.locator('[data-category=tubing] [data-enquiry]').click()
            dialog = page.locator('dialog')
            expect(dialog.locator('[name=topic]')).to_have_value('CAPD tubing')
            check_accessibility(page)
            page.screenshot(path=str(output / 'direct-mobile-dialog.png'))
            dialog.locator('[name=phone]').fill('+12025550123')
            dialog.locator('[name=message]').fill('A tubing enquiry')
            dialog.get_by_role('button', name='Send enquiry').click()
            expect(dialog.locator('[role=status]')).to_contain_text('Your enquiry has been submitted')
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            page.keyboard.press('Escape')
            expect(dialog).not_to_be_visible()
            print('PASS: mobile product enquiry sends with the correct topic and closes with Escape')
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()

print('All direct-send checks passed with simulated provider responses. No email was sent.')
