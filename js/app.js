/* =========================================================
   디자인 허브 앱 로직
   ========================================================= */
(function () {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const STORAGE_BOOKMARKS = 'designhub:bookmarks';
  const STORAGE_THEME = 'designhub:theme';
  const STORAGE_VIEW = 'designhub:view';

  const state = {
    cat: 'all',      // 'all' | 'bookmarks' | category id
    query: '',
    tag: '',         // '' | '한국' | '무료' | '유료' | 'AI'
    view: 'list',    // 'list' | 'grid'
    ggroup: '',      // 용어 사전 그룹 필터
    bookmarks: new Set(),
  };

  const els = {
    nav: $('#nav'),
    content: $('#content'),
    search: $('#search'),
    stats: $('#stats'),
    tagFilters: $('#tag-filters'),
    hero: $('#hero'),
    themeToggle: $('#theme-toggle'),
    logo: $('#logo'),
    footerTop: $('#footer-top'),
    viewBtns: document.querySelectorAll('.view__btn'),
    preview: $('#preview'),
    previewImg: $('#preview-img'),
    previewName: $('#preview-name'),
    previewDomain: $('#preview-domain'),
  };

  const TAG_FILTERS = [
    { id: '', label: '전체' },
    { id: '한국', label: '한국' },
    { id: '무료', label: '무료' },
    { id: '유료', label: '유료' },
    { id: 'AI', label: 'AI' },
  ];

  const STAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="m12 2.5 2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.8Z"/></svg>';

  const PSEUDO = {
    all:       { id: 'all', label: '전체' },
    bookmarks: { id: 'bookmarks', label: '즐겨찾기', desc: '이 브라우저에 저장된 즐겨찾기' },
    styles:    { id: 'styles', label: '스타일 사전', desc: '유명 그래픽 디자인 양식과 흐름. 이름을 누르면 핀터레스트 레퍼런스가 열립니다.' },
    trends:    { id: 'trends', label: '2026 트렌드', desc: '트렌드 리포트와 커뮤니티에서 반복 언급되는 키워드 정리' },
    glossary:  { id: 'glossary', label: '용어 사전', desc: '디자인 · 편집/인쇄 · UI/UX 구축 시 자주 쓰는 용어' },
  };
  const INSIGHT_PAGES = ['styles', 'trends', 'glossary'];
  const pinUrl = q => 'https://www.pinterest.com/search/pins/?q=' + encodeURIComponent(q);
  const imgUrl = q => 'https://www.google.com/search?tbm=isch&q=' + encodeURIComponent(q);

  /* ---------- helpers ---------- */
  function hostOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); }
    catch { return url; }
  }
  function faviconUrl(url) {
    return 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(hostOf(url)) + '&sz=64';
  }
  /* 사이트 스크린샷 (무료 캡처 서비스, 서버 불필요)
     mShots 는 첫 요청 시 '생성 중' 이미지를 캐시 가능한 응답으로 돌려주므로
     세션 salt + 재시도 번호를 붙여 브라우저 캐시를 우회한다. */
  const SHOT_SALT = Date.now().toString(36);
  function shotUrl(url, fallback, n = 0) {
    return fallback
      ? 'https://image.thum.io/get/width/640/crop/400/noanimate/' + url
      : 'https://s0.wp.com/mshots/v1/' + encodeURIComponent(url) + '?w=640&h=400&r=' + SHOT_SALT + '-' + n;
  }
  const SHOT_RETRY_MS = [2500, 5000, 9000];
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function highlight(text, q) {
    const safe = escapeHtml(text);
    const words = (q || '').split(/\s+/).filter(Boolean);
    if (!words.length) return safe;
    const re = new RegExp('(' + words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'gi');
    return safe.replace(re, '<mark>$1</mark>');
  }
  function setHash(id) {
    // file:// 로 열었을 때 replaceState 가 SecurityError 를 던지므로 안전하게 처리
    try { history.replaceState(null, '', id ? '#' + id : location.pathname + location.search); }
    catch { try { location.hash = id; } catch { /* ignore */ } }
  }
  function catById(id) {
    return PSEUDO[id] || CATEGORIES.find(c => c.id === id);
  }

  /* ---------- storage ---------- */
  function load(key) { try { return localStorage.getItem(key); } catch { return null; } }
  function save(key, val) { try { localStorage.setItem(key, val); } catch { /* ignore */ } }
  function loadBookmarks() {
    try { const raw = load(STORAGE_BOOKMARKS); if (raw) state.bookmarks = new Set(JSON.parse(raw)); }
    catch { /* ignore */ }
  }
  function saveBookmarks() { save(STORAGE_BOOKMARKS, JSON.stringify([...state.bookmarks])); }

  /* ---------- theme / view ---------- */
  function applyTheme(theme) {
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
  }
  function initTheme() {
    let theme = load(STORAGE_THEME);
    if (!theme) theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(theme);
  }
  function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    save(STORAGE_THEME, next);
  }
  function applyView(view) {
    state.view = view;
    document.body.classList.toggle('grid-view', view === 'grid');
    els.viewBtns.forEach(b => b.classList.toggle('is-active', b.dataset.view === view));
  }

  /* ---------- filtering ---------- */
  function matches(site) {
    if (state.tag && !(site.tags || []).includes(state.tag)) return false;
    if (!state.query) return true;
    const words = state.query.toLowerCase().split(/\s+/).filter(Boolean);
    const hay = [site.name, site.desc, hostOf(site.url), ...(site.tags || []), (catById(site.cat) || {}).label || '']
      .join(' ').toLowerCase();
    return words.every(w => hay.includes(w));
  }
  function visibleSites() { return SITES.filter(matches); }
  function textMatches(fields) {
    if (!state.query) return true;
    const words = state.query.toLowerCase().split(/\s+/).filter(Boolean);
    const hay = fields.filter(Boolean).join(' ').toLowerCase();
    return words.every(w => hay.includes(w));
  }
  function visibleStyles() { return STYLES.filter(x => textMatches([x.name, x.en, x.era, x.desc, x.traits, x.people])); }
  function visibleTrends() { return TRENDS.filter(x => textMatches([x.name, x.area, x.desc])); }
  function visibleGlossary(ignoreGroup) {
    return GLOSSARY.filter(x => (ignoreGroup || !state.ggroup || x.group === state.ggroup) && textMatches([x.term, x.en, x.desc]));
  }

  /* ---------- render: nav / filters / stats ---------- */
  function renderNav() {
    const counts = {};
    SITES.forEach(s => { counts[s.cat] = (counts[s.cat] || 0) + 1; });

    const item = (id, label, count, icon = '') => `
      <button class="nav__item ${state.cat === id ? 'is-active' : ''}" data-cat="${id}" type="button">
        ${icon}<span class="nav__label">${escapeHtml(label)}</span>
        <span class="nav__count">${count}</span>
      </button>`;

    let html = '<div class="nav__group">라이브러리</div>';
    html += item('all', '전체', SITES.length);
    html += item('bookmarks', '즐겨찾기', state.bookmarks.size, STAR.replace('fill="none"', 'fill="currentColor"'));
    html += '<div class="nav__group">카테고리</div>';
    CATEGORIES.forEach(c => { html += item(c.id, c.label, counts[c.id] || 0); });
    html += '<div class="nav__group">인사이트</div>';
    html += item('styles', '스타일 사전', STYLES.length);
    html += item('trends', '2026 트렌드', TRENDS.length);
    html += item('glossary', '용어 사전', GLOSSARY.length);
    els.nav.innerHTML = html;
  }

  function renderFilters() {
    els.tagFilters.innerHTML = TAG_FILTERS.map(t =>
      `<button class="pill ${state.tag === t.id ? 'is-active' : ''}" data-tag="${t.id}" type="button" role="tab" aria-selected="${state.tag === t.id}">${t.label}</button>`
    ).join('');
  }

  function renderStats(shown) {
    const searching = !!state.query;
    if (searching) {
      els.stats.innerHTML = `"<b>${escapeHtml(state.query)}</b>" 검색 결과 <b>${shown}</b>개`;
    } else if (state.cat === 'all') {
      els.stats.innerHTML = '';
    } else if (state.cat === 'styles') {
      els.stats.innerHTML = `디자인 스타일 <b>${shown}</b>개 · 연대순`;
    } else if (state.cat === 'trends') {
      els.stats.innerHTML = `트렌드 키워드 <b>${shown}</b>개`;
    } else if (state.cat === 'glossary') {
      els.stats.innerHTML = `용어 <b>${shown}</b>개`;
    } else {
      els.stats.innerHTML = `<b>${escapeHtml(catById(state.cat).label)}</b> · <b>${shown}</b>개`;
    }
  }

  /* ---------- render: row / section ---------- */
  function renderRow(site, showCat) {
    const on = state.bookmarks.has(site.url);
    const host = hostOf(site.url);
    const cat = catById(site.cat) || PSEUDO.all;
    const initial = escapeHtml((site.name || '?').trim().charAt(0).toUpperCase());
    const parts = [];
    if (showCat) parts.push(`<b>${escapeHtml(cat.label)}</b>`);
    if (site.sub && (showCat || state.cat !== site.cat)) parts.push(escapeHtml(site.sub));
    (site.tags || []).forEach(t => parts.push(escapeHtml(t)));
    return `
      <a class="row" href="${escapeHtml(site.url)}" target="_blank" rel="noopener noreferrer" data-url="${escapeHtml(site.url)}">
        <span class="row__fav" data-initial="${initial}">
          <img src="${faviconUrl(site.url)}" alt="" loading="lazy" onerror="this.parentNode.textContent=this.parentNode.dataset.initial" />
        </span>
        <span class="row__main">
          <span class="row__name">${highlight(site.name, state.query)}</span>
          <span class="row__domain">${highlight(host, state.query)}</span>
        </span>
        <p class="row__desc">${highlight(site.desc, state.query)}</p>
        <span class="row__tags">${parts.join(' · ')}</span>
        <button class="row__star ${on ? 'is-on' : ''}" type="button" aria-label="${on ? '즐겨찾기 해제' : '즐겨찾기 추가'}" title="즐겨찾기">${STAR}</button>
        <span class="row__arrow" aria-hidden="true">↗</span>
      </a>`;
  }

  function renderRows(sites, showCat) {
    // sub 필드가 있으면 소분류로 묶어서 표시 (AI 카테고리 등)
    const hasSub = sites.some(s => s.sub);
    if (!hasSub || showCat) return `<div class="list">${sites.map(s => renderRow(s, showCat)).join('')}</div>`;
    const order = [...(typeof AI_SUBS !== 'undefined' ? AI_SUBS : [])];
    sites.forEach(s => { const k = s.sub || '기타'; if (!order.includes(k)) order.push(k); });
    return order.map(k => {
      const items = sites.filter(s => (s.sub || '기타') === k);
      if (!items.length) return '';
      return `
        <div class="subgroup">
          <header class="section__head section__head--sub">
            <h3 class="section__title section__title--sub">${escapeHtml(k)}</h3>
            <span class="section__count">${items.length}</span>
          </header>
          <div class="list">${items.map(s => renderRow(s, showCat)).join('')}</div>
        </div>`;
    }).join('');
  }

  function renderSection(cat, sites, showCat = false) {
    if (!sites.length) return '';
    return `
      <section class="section" id="cat-${cat.id}">
        <header class="section__head">
          <h2 class="section__title">${escapeHtml(cat.label)}</h2>
          <span class="section__count">${sites.length}</span>
          ${cat.desc ? `<p class="section__desc">${escapeHtml(cat.desc)}</p>` : ''}
        </header>
        ${renderRows(sites, showCat)}
      </section>`;
  }

  function styleThumb(x) {
    const en = escapeHtml(x.en);
    if (!x.img) {
      return `<a class="srow__thumbwrap is-text" href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer" tabindex="-1" data-en="${en}"></a>`;
    }
    // 이미지 로드 실패 시: img 를 제거하고 래퍼에 is-text 를 붙여 CSS 로 텍스트 타일 표시
    return `
      <a class="srow__thumbwrap" href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer" tabindex="-1" data-en="${en}" title="${escapeHtml(x.imgTitle || x.en)}">
        <img class="srow__thumb" src="${escapeHtml(x.img)}" alt="${en} 대표 이미지" loading="lazy"
             onerror="this.parentNode.classList.add('is-text'); this.remove();" />
      </a>`;
  }

  function renderStyleRow(x) {
    return `
      <div class="srow srow--style">
        ${styleThumb(x)}
        <span class="srow__main">
          <span class="srow__era">${escapeHtml(x.era)}</span>
          <a class="srow__name" href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer">${highlight(x.name, state.query)}</a>
          <span class="srow__en">${highlight(x.en, state.query)}</span>
        </span>
        <span class="srow__body">
          <p class="srow__desc">${highlight(x.desc, state.query)}</p>
          <span class="srow__traits">${highlight(x.traits, state.query)}${x.people ? ` <span class="srow__people">· ${highlight(x.people, state.query)}</span>` : ''}</span>
        </span>
        <span class="srow__links">
          <a href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer">Pinterest</a>
          <a href="${imgUrl(x.en + ' graphic design')}" target="_blank" rel="noopener noreferrer">이미지</a>
          ${x.wiki ? `<a href="${escapeHtml(x.wiki)}" target="_blank" rel="noopener noreferrer">Wiki</a>` : ''}
        </span>
      </div>`;
  }

  function renderTrendRow(x, i) {
    return `
      <div class="srow srow--trend">
        <span class="srow__era">${String(i + 1).padStart(2, '0')}</span>
        <span class="srow__main">
          <a class="srow__name" href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer">${highlight(x.name, state.query)}</a>
          <span class="srow__en">${escapeHtml(x.area)}</span>
        </span>
        <span class="srow__body"><p class="srow__desc">${highlight(x.desc, state.query)}</p></span>
        <span class="srow__links">
          <a href="${pinUrl(x.q)}" target="_blank" rel="noopener noreferrer">Pinterest</a>
          ${x.link ? `<a href="${escapeHtml(x.link)}" target="_blank" rel="noopener noreferrer">자세히</a>` : ''}
        </span>
      </div>`;
  }

  function renderInsightSection(cat, rowsHtml, count, extra = '') {
    if (!count) return '';
    return `
      <section class="section" id="cat-${cat.id}">
        <header class="section__head">
          <h2 class="section__title">${escapeHtml(cat.label)}</h2>
          <span class="section__count">${count}</span>
          ${cat.desc ? `<p class="section__desc">${escapeHtml(cat.desc)}</p>` : ''}
        </header>
        <div class="list list--insight">${rowsHtml}</div>
        ${extra}
      </section>`;
  }

  function renderGlossaryRow(x) {
    return `
      <div class="grow">
        <span class="grow__main">
          <span class="grow__term">${highlight(x.term, state.query)}</span>
          <span class="grow__en">${highlight(x.en, state.query)}</span>
        </span>
        <p class="grow__desc">${highlight(x.desc, state.query)}</p>
      </div>`;
  }

  function renderGlossaryFilter() {
    const counts = {};
    GLOSSARY.forEach(g => { counts[g.group] = (counts[g.group] || 0) + 1; });
    const pill = (id, label, n) => `<button class="pill ${state.ggroup === id ? 'is-active' : ''}" data-ggroup="${id}" type="button">${escapeHtml(label)} <span class="pill__count">${n}</span></button>`;
    return `<div class="gfilter pills">${pill('', '전체', GLOSSARY.length)}${GLOSSARY_GROUPS.map(g => pill(g.id, g.label, counts[g.id] || 0)).join('')}</div>`;
  }

  function renderGlossary(list, withFilter) {
    const groups = GLOSSARY_GROUPS.filter(g => !state.ggroup || g.id === state.ggroup);
    let html = withFilter ? renderGlossaryFilter() : '';
    groups.forEach(g => {
      const items = list.filter(x => x.group === g.id);
      if (!items.length) return;
      html += `
        <section class="section section--sub" id="g-${g.id}">
          <header class="section__head section__head--sub">
            <h3 class="section__title section__title--sub">${escapeHtml(g.label)}</h3>
            <span class="section__count">${items.length}</span>
          </header>
          <div class="list list--insight">${items.map(renderGlossaryRow).join('')}</div>
        </section>`;
    });
    return html;
  }

  function renderTrendSources() {
    return `
      <div class="sources">
        <span class="sources__label">참고 리포트</span>
        ${TREND_SOURCES.map(t => `<a class="sources__link" href="${escapeHtml(t.url)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(t.desc)}">${escapeHtml(t.name)} ↗</a>`).join('')}
      </div>`;
  }

  function renderEmpty(title, desc) {
    return `<div class="empty"><p class="empty__title">${escapeHtml(title)}</p><p>${escapeHtml(desc)}</p></div>`;
  }

  /* ---------- render: content ---------- */
  function renderContent() {
    const sites = visibleSites();
    const searching = !!state.query;
    let html = '';
    let shown = 0;

    const isInsight = INSIGHT_PAGES.includes(state.cat);
    document.querySelector('.meta').hidden = isInsight;

    if (state.cat === 'bookmarks') {
      const list = sites.filter(s => state.bookmarks.has(s.url));
      shown = list.length;
      html = list.length
        ? renderSection(PSEUDO.bookmarks, list, true)
        : renderEmpty('아직 즐겨찾기가 없습니다', '목록의 ☆ 버튼을 눌러 자주 쓰는 사이트를 모아보세요.');
    } else if (state.cat === 'styles') {
      const list = visibleStyles();
      shown = list.length;
      html = list.length
        ? renderInsightSection(PSEUDO.styles, list.map(renderStyleRow).join(''), list.length)
        : renderEmpty('검색 결과가 없습니다', `"${state.query}"에 해당하는 스타일이 없습니다.`);
    } else if (state.cat === 'trends') {
      const list = visibleTrends();
      shown = list.length;
      html = list.length
        ? renderInsightSection(PSEUDO.trends, list.map(renderTrendRow).join(''), list.length, renderTrendSources())
        : renderEmpty('검색 결과가 없습니다', `"${state.query}"에 해당하는 트렌드가 없습니다.`);
    } else if (state.cat === 'glossary') {
      const list = visibleGlossary();
      shown = list.length;
      html = list.length
        ? renderInsightSection(PSEUDO.glossary, renderGlossary(list, true), list.length)
        : renderInsightSection(PSEUDO.glossary, renderGlossaryFilter() + renderEmpty('검색 결과가 없습니다', `"${state.query}"에 해당하는 용어가 없습니다.`), 1);
    } else if (state.cat === 'all') {
      const starred = sites.filter(s => state.bookmarks.has(s.url));
      if (starred.length && !searching) html += renderSection(PSEUDO.bookmarks, starred, true);
      CATEGORIES.forEach(c => { html += renderSection(c, sites.filter(s => s.cat === c.id), searching); });
      shown = sites.length;
      if (searching && !state.tag) {
        const st = visibleStyles(), tr = visibleTrends();
        html += renderInsightSection(PSEUDO.styles, st.map(renderStyleRow).join(''), st.length);
        html += renderInsightSection(PSEUDO.trends, tr.map(renderTrendRow).join(''), tr.length);
        const gl = visibleGlossary(true);
        html += renderInsightSection(PSEUDO.glossary, gl.map(renderGlossaryRow).join(''), gl.length);
        shown += st.length + tr.length + gl.length;
      }
      if (!shown) html = renderEmpty('검색 결과가 없습니다', `"${state.query}"에 해당하는 항목을 찾지 못했습니다.`);
    } else {
      const cat = catById(state.cat);
      const list = sites.filter(s => s.cat === state.cat);
      shown = list.length;
      html = list.length
        ? renderSection(cat, list)
        : renderEmpty('검색 결과가 없습니다', searching ? `"${state.query}"에 해당하는 사이트가 이 카테고리에 없습니다.` : '조건에 맞는 사이트가 없습니다.');
    }

    els.content.innerHTML = html;
    els.hero.style.display = (state.cat === 'all' && !searching) ? '' : 'none';
    renderStats(shown);
  }

  function renderAll() {
    renderNav();
    renderFilters();
    renderContent();
  }

  /* ---------- events ---------- */
  function bindEvents() {
    els.nav.addEventListener('click', e => {
      const btn = e.target.closest('.nav__item');
      if (!btn) return;
      state.cat = btn.dataset.cat;
      setHash(state.cat === 'all' ? '' : state.cat);
      renderAll();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('hashchange', () => {
      const id = location.hash.slice(1);
      if (id && catById(id) && id !== state.cat) { state.cat = id; renderAll(); window.scrollTo(0, 0); }
    });

    els.tagFilters.addEventListener('click', e => {
      const btn = e.target.closest('.pill');
      if (!btn) return;
      state.tag = btn.dataset.tag;
      renderAll();
    });

    els.viewBtns.forEach(b => b.addEventListener('click', () => {
      applyView(b.dataset.view);
      save(STORAGE_VIEW, b.dataset.view);
    }));

    let timer;
    els.search.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        state.query = els.search.value.trim();
        renderNav();
        renderContent();
      }, 120);
    });
    els.search.addEventListener('keydown', e => {
      if (e.key === 'Escape') { els.search.value = ''; state.query = ''; renderContent(); els.search.blur(); }
    });
    document.addEventListener('keydown', e => {
      if (e.key === '/' && document.activeElement !== els.search && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        els.search.focus();
        els.search.select();
      }
    });

    els.content.addEventListener('click', e => {
      const gp = e.target.closest('[data-ggroup]');
      if (gp) { state.ggroup = gp.dataset.ggroup; renderContent(); return; }
      const star = e.target.closest('.row__star');
      if (!star) return;
      e.preventDefault();
      e.stopPropagation();
      const url = star.closest('.row').dataset.url;
      if (state.bookmarks.has(url)) state.bookmarks.delete(url);
      else state.bookmarks.add(url);
      saveBookmarks();
      if (state.cat === 'bookmarks' || (state.cat === 'all' && !state.query)) renderAll();
      else { star.classList.toggle('is-on'); renderNav(); }
    });

    els.themeToggle.addEventListener('click', toggleTheme);

    const goHome = e => {
      e.preventDefault();
      state.cat = 'all'; state.query = ''; state.tag = '';
      els.search.value = '';
      setHash('');
      renderAll();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    els.logo.addEventListener('click', goHome);
    els.footerTop.addEventListener('click', e => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------- hover preview ---------- */
  const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const shotState = new Map(); // url -> { tries, done, fallback }
  let hoverUrl = null;
  let hoverTimer = null;
  let retryTimer = null;

  function positionPreview(x, y) {
    const w = 320, h = els.preview.offsetHeight || 244, gap = 18;
    let left = x + gap;
    if (left + w > window.innerWidth - 12) left = x - w - gap;
    let top = y - h / 2;
    top = Math.max(12, Math.min(top, window.innerHeight - h - 12));
    els.preview.style.left = left + 'px';
    els.preview.style.top = top + 'px';
  }

  function loadShot(url) {
    const st = shotState.get(url) || { tries: 0, done: false, fallback: false };
    shotState.set(url, st);
    els.preview.classList.remove('is-loaded');
    els.previewImg.src = '';
    els.previewImg.src = shotUrl(url, st.fallback, st.tries);
  }

  let lastX = 0, lastY = 0;
  function showPreview(row) {
    const url = row.dataset.url;
    if (!url || url === hoverUrl) return;
    hoverUrl = url;
    clearTimeout(retryTimer);
    els.previewName.textContent = row.querySelector('.row__name').textContent;
    els.previewDomain.textContent = hostOf(url);
    els.preview.classList.add('is-visible');
    els.preview.setAttribute('aria-hidden', 'false');
    positionPreview(lastX, lastY);
    loadShot(url);
  }

  function hidePreview() {
    hoverUrl = null;
    clearTimeout(hoverTimer);
    clearTimeout(retryTimer);
    els.preview.classList.remove('is-visible');
    els.preview.setAttribute('aria-hidden', 'true');
  }

  function bindPreview() {
    if (!canHover) return;

    els.content.addEventListener('mouseover', e => {
      const row = e.target.closest('.row');
      if (!row) return;
      if (row.dataset.url === hoverUrl) return;
      clearTimeout(hoverTimer);
      lastX = e.clientX; lastY = e.clientY;
      hoverTimer = setTimeout(() => showPreview(row), 160);
    });
    els.content.addEventListener('mousemove', e => {
      lastX = e.clientX; lastY = e.clientY;
      if (hoverUrl) positionPreview(lastX, lastY);
    });
    els.content.addEventListener('mouseout', e => {
      const row = e.target.closest('.row');
      if (!row) return;
      if (e.relatedTarget && row.contains(e.relatedTarget)) return;
      hidePreview();
    });
    window.addEventListener('scroll', () => { if (hoverUrl) hidePreview(); }, { passive: true });

    els.previewImg.addEventListener('load', () => {
      const url = hoverUrl;
      if (!url) return;
      const st = shotState.get(url);
      if (!st) return;
      els.preview.classList.add('is-loaded');
      // mShots 는 첫 요청 시 '생성 중' 이미지를 먼저 돌려주므로 몇 차례 다시 받아 실제 캡처로 교체
      if (!st.done && !st.fallback && st.tries < SHOT_RETRY_MS.length) {
        const delay = SHOT_RETRY_MS[st.tries];
        st.tries += 1;
        clearTimeout(retryTimer);
        retryTimer = setTimeout(() => {
          if (hoverUrl !== url) return;
          els.previewImg.src = shotUrl(url, false, st.tries);
        }, delay);
      } else {
        st.done = true;
      }
    });
    els.previewImg.addEventListener('error', () => {
      const url = hoverUrl;
      if (!url) return;
      const st = shotState.get(url);
      if (!st || st.fallback) return;
      st.fallback = true;
      st.tries = 0;
      els.previewImg.src = shotUrl(url, true);
    });
  }

  /* ---------- init ---------- */
  (function initRoute() {
    const id = location.hash.slice(1);
    if (id && catById(id)) state.cat = id;
  })();
  initTheme();
  applyView(load(STORAGE_VIEW) === 'grid' ? 'grid' : 'list');
  loadBookmarks();
  bindEvents();
  bindPreview();
  renderAll();
})();
