// Stamp ?v=<hash> on shared assets so browsers fetch new versions after a publish.
// Run from the repo root before every publish: node scripts/version_assets.cjs
const fs = require('fs');
const crypto = require('crypto');

// Hash LF-normalised content so Windows and GitHub checkouts agree.
const hash = file => crypto.createHash('sha1').update(fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n')).digest('hex').slice(0, 10);
const write = (file, next, prev) => { if (next !== prev) { fs.writeFileSync(file, next); console.log('stamped', file); } };

// proto.js carries the Hindi dictionary version, so stamp that first.
const js = fs.readFileSync('assets/proto.js', 'utf8');
write('assets/proto.js', js.replace(/const I18N_V = '[^']*'/, `const I18N_V = '${hash('assets/i18n-hi.js')}'`), js);

const assets = ['proto.css', 'proto.js', 'products.js'].map(name => [name, hash(`assets/${name}`)]);
for (const page of fs.readdirSync('.').filter(f => f.endsWith('.html'))) {
  const html = fs.readFileSync(page, 'utf8');
  let next = html;
  for (const [name, v] of assets) next = next.replace(new RegExp(`(assets/${name.replace('.', '\\.')})\\?v=[0-9a-f]+`, 'g'), `$1?v=${v}`);
  write(page, next, html);
}
