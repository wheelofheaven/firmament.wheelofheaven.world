(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const presets = {
    sentence: 'Under the same sky,\nanother way to read.',
    pangram: 'Sphinx of black quartz, judge my vow.',
    scholarly: 'ʾĕlōhīm · šāmayim · ḥayyīm\nṣedeq · ṭôḇ · ḫ · ṛ · ʿ',
    cyrillic: 'Слова соединяют\nвремена и культуры.'
  };
  const styles = {regular: [400, 'normal'], italic: [400, 'italic'], bold: [700, 'normal'], bolditalic: [700, 'italic']};
  const text = $('#type-text');
  const mobile = matchMedia('(max-width:720px)').matches;
  if (mobile) $('#type-size').value = '42';
  let supported = null;
  function reportCoverage() {
    if (!supported) return;
    const missing = [...new Set([...text.value].filter(ch => !supported.has(ch) && !/\s/.test(ch)))];
    $('#coverage-notice').textContent = missing.length ? `Outside this release’s coverage: ${missing.join(' ')}. Your browser may use a fallback font for these characters.` : '';
  }
  function updateType() {
    const [weight, style] = styles[$('#type-style').value];
    const size = Number($('#type-size').value);
    const tracking = Number($('#type-tracking').value) / 100;
    const leading = Number($('#type-leading').value) / 100;
    Object.assign(text.style, {fontWeight: weight, fontStyle: style, fontSize: `${size}px`, letterSpacing: `${tracking}em`, lineHeight: leading});
    $('#type-size-label').textContent = `${size} px`;
    $('#type-tracking-label').textContent = `${tracking.toFixed(2).replace('-', '−')} em`;
    $('#type-leading-label').textContent = leading.toFixed(2);
    reportCoverage();
  }
  ['#type-style', '#type-size', '#type-tracking', '#type-leading'].forEach(id => $(id).addEventListener('input', updateType));
  text.addEventListener('input', () => { $$('[data-preset]').forEach(b => b.setAttribute('aria-pressed', 'false')); reportCoverage(); });
  $$('[data-preset]').forEach(button => button.addEventListener('click', () => {
    text.value = presets[button.dataset.preset];
    $$('[data-preset]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    reportCoverage();
  }));
  $$('[data-paper]').forEach(button => button.addEventListener('click', () => {
    $('#type-canvas').dataset.paper = button.dataset.paper;
    $$('[data-paper]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  }));
  $('#reset-type').addEventListener('click', () => {
    text.value = presets.sentence;
    $('#type-style').value = 'regular';
    $('#type-size').value = mobile ? '42' : '76';
    $('#type-tracking').value = '-2';
    $('#type-leading').value = '115';
    $('[data-paper="paper"]').click();
    $$('[data-preset]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.preset === 'sentence')));
    updateType();
  });
  updateType();

  let inventory = [];
  let filter = 'added';
  let selected = null;
  const displayChar = glyph => glyph.combining ? `◌${glyph.char}` : glyph.char;
  function selectGlyph(glyph) {
    selected = glyph;
    ['#glyph-large', '#glyph-regular', '#glyph-italic', '#glyph-bold', '#glyph-bolditalic'].forEach(id => $(id).textContent = displayChar(glyph));
    $('#glyph-code').textContent = glyph.code;
    $('#glyph-name').textContent = glyph.name.toLowerCase();
    $('#glyph-badge').hidden = !glyph.added;
    $('#copy-status').textContent = '';
    $$('.glyph-tile').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.code === glyph.code)));
  }
  function renderGlyphs() {
    const query = $('#glyph-search').value.trim().toLowerCase();
    const found = inventory.filter(g => (filter === 'all' || (filter === 'added' ? g.added : g.group === filter)) && (!query || g.char === query || g.name.toLowerCase().includes(query) || g.code.toLowerCase().includes(query)));
    const grid = $('#glyph-grid');
    grid.replaceChildren();
    const fragment = document.createDocumentFragment();
    found.forEach(glyph => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `glyph-tile${glyph.added ? ' glyph-tile--added' : ''}`;
      button.textContent = displayChar(glyph);
      button.dataset.code = glyph.code;
      button.setAttribute('aria-label', `${glyph.name}, ${glyph.code}${glyph.added ? ', new in Firmament' : ''}`);
      button.setAttribute('aria-pressed', String(selected?.code === glyph.code));
      button.addEventListener('click', () => selectGlyph(glyph));
      fragment.append(button);
    });
    if (!found.length) {
      const empty = document.createElement('p');
      empty.className = 'glyph-empty';
      empty.textContent = 'No matching characters in this category. Try “All” or another search.';
      fragment.append(empty);
    }
    grid.append(fragment);
    grid.scrollTop = 0;
    $('#glyph-count').textContent = `${found.length} ${found.length === 1 ? 'character' : 'characters'} shown · select to inspect`;
  }
  $$('[data-filter]').forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.filter;
    $$('[data-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    renderGlyphs();
  }));
  $('#glyph-search').addEventListener('input', renderGlyphs);
  $('#copy-glyph').addEventListener('click', async () => {
    if (!selected) return;
    try {
      await navigator.clipboard.writeText(selected.char);
      $('#copy-status').textContent = `Copied ${selected.code}.`;
    } catch {
      $('#copy-status').textContent = `Select and copy this character: ${selected.char}`;
    }
  });
  fetch('/assets/glyphs.json').then(r => {
    if (!r.ok) throw new Error('Could not load the inventory');
    return r.json();
  }).then(data => {
    inventory = data;
    supported = new Set(data.map(g => g.char));
    selectGlyph(data.find(g => g.char === 'ḥ') || data[0]);
    renderGlyphs();
    reportCoverage();
  }).catch(() => {
    $('#glyph-count').textContent = 'The character inventory could not load. Please refresh to try again.';
    $('#copy-glyph').disabled = true;
  });
})();
