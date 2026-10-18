import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../assets/motion.js', import.meta.url), 'utf8');
for (const scenario of ['reduced-motion', 'saved-opt-out', 'missing-libraries']) {
  const toggle = { hidden: true, setAttribute() {}, addEventListener() {} };
  const root = { dataset: {} };
  let libraryWork = 0;
  const window = { addEventListener() {} };
  if (scenario !== 'missing-libraries') Object.assign(window, {
    gsap: { registerPlugin() {}, context() { libraryWork++; throw new Error('Animation should not start'); } },
    ScrollTrigger: {}, Lenis: class { constructor() { libraryWork++; } }
  });
  vm.runInNewContext(source, {
    URL, window, document: {
      currentScript: { src: 'https://example.test/assets/motion.js' },
      documentElement: root, hidden: false, addEventListener() {},
      querySelector: selector => selector === '[data-motion-toggle]' ? toggle : null
    },
    localStorage: { getItem: () => scenario === 'saved-opt-out' ? 'off' : null },
    matchMedia: query => ({ matches: scenario === 'reduced-motion' && query.includes('prefers-reduced-motion'), addEventListener() {} })
  });
  assert.equal(libraryWork, 0, `${scenario}: no animation or scroll engine should start`);
  if (scenario === 'missing-libraries') assert.equal(toggle.hidden, true);
  else {
    assert.equal(root.dataset.motion, 'off');
    assert.equal(toggle.disabled, scenario === 'reduced-motion');
    assert.equal(toggle.textContent, scenario === 'reduced-motion' ? 'Reduced motion enabled' : 'Enable motion');
  }
  console.log(`PASS: ${scenario} leaves content static without starting animation engines`);
}
