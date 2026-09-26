/* 디자인 허브 — 정적 페이지(카테고리 · 읽을거리 · 디자인 잡담 등) 공통 스크립트.
   메인 화면은 app.js 가 같은 일을 합니다.

   - 메뉴의 즐겨찾기 개수를 브라우저 저장소에서 읽어 채웁니다
   - 좁은 화면에서 햄버거 버튼으로 메뉴 서랍을 엽니다
   - 상단과 서랍 안의 테마 전환 · 목록/격자 버튼 (메인 화면과 같은 저장소 값을 씁니다)
   - 검색창 단축키(/), 맨 위로 버튼
   검색은 폼이라 엔터를 치면 메인 화면(?q=)으로 넘어갑니다. */
(function () {
  'use strict';

  /* ---------- 즐겨찾기 개수 ---------- */
  try {
    const raw = localStorage.getItem('designhub:bookmarks');
    const n = raw ? JSON.parse(raw).length : 0;
    document.querySelectorAll('[data-bm-count]').forEach(el => { el.textContent = n; });
  } catch (e) { /* 저장소를 못 쓰는 환경이면 0 으로 둡니다 */ }

  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 무시 */ } }

  /* ---------- 테마 ---------- */
  function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    if (next === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    save('designhub:theme', next);
  }
  ['theme-toggle', 'drawer-theme'].forEach(id => {
    const b = document.getElementById(id);
    if (b) b.addEventListener('click', toggleTheme);
  });

  /* ---------- 검색 단축키 ---------- */
  const search = document.getElementById('search');
  if (search) {
    document.addEventListener('keydown', e => {
      if (e.key === '/' && document.activeElement !== search && !e.metaKey && !e.ctrlKey) {
        const tag = (document.activeElement || {}).tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA') return;   // 글을 쓰는 중이면 그대로 둡니다
        e.preventDefault();
        search.focus();
      }
    });
    search.addEventListener('keydown', e => { if (e.key === 'Escape') { search.value = ''; search.blur(); } });
  }

  /* ---------- 맨 위로 ---------- */
  const toTop = document.getElementById('to-top');
  const footTop = document.getElementById('footer-top');
  const up = e => { if (e) e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  if (footTop) footTop.addEventListener('click', up);
  if (toTop) {
    toTop.addEventListener('click', () => up());
    const onScroll = () => toTop.classList.toggle('is-visible', window.scrollY > 700);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- 글 공유 ----------
     폰에서는 운영체제 공유 창(카카오톡 등)이 열리고, 안 되는 환경에서는 링크를 복사합니다.
     공유된 링크에는 utm 꼬리표를 붙여, 공유로 들어온 방문이 애널리틱스에서 따로 보이게 합니다. */
  function track(name, params) {
    try { if (typeof gtag === 'function') gtag('event', name, params); } catch (e) { /* 무시 */ }
  }
  const canonical = (document.querySelector('link[rel=canonical]') || {}).href || location.href.split('?')[0];
  const shareMsg = document.querySelector('.share__msg');
  function say(text) {
    if (!shareMsg) return;
    shareMsg.textContent = text;
    clearTimeout(say.t);
    say.t = setTimeout(() => { shareMsg.textContent = ''; }, 2500);
  }
  function copy(medium) {
    const url = canonical + '?utm_source=share&utm_medium=' + medium;
    const done = () => { say('링크를 복사했습니다'); track('share', { method: 'copy', content_type: 'article', item_id: location.pathname }); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, () => say('복사하지 못했습니다. 주소창의 주소를 복사해 주세요'));
    } else {
      say('복사하지 못했습니다. 주소창의 주소를 복사해 주세요');
    }
  }
  const shareBtn = document.querySelector('[data-share]');
  const copyBtn = document.querySelector('[data-copy]');
  if (shareBtn) shareBtn.addEventListener('click', () => {
    if (navigator.share) {
      navigator.share({ title: document.title, url: canonical + '?utm_source=share&utm_medium=native' })
        .then(() => track('share', { method: 'native', content_type: 'article', item_id: location.pathname }))
        .catch(() => { /* 사용자가 닫은 경우 */ });
    } else {
      copy('link');
    }
  });
  if (copyBtn) copyBtn.addEventListener('click', () => copy('link'));

  /* ---------- 모바일 메뉴 ---------- */
  const drawer = document.getElementById('drawer');
  const openBtn = document.getElementById('menu-open');
  const closeBtn = document.getElementById('menu-close');
  if (!drawer || !openBtn || !closeBtn) return;

  let lastFocus = null;

  function open() {
    lastFocus = document.activeElement;
    drawer.hidden = false;
    // 다음 프레임에 클래스를 붙여야 열리는 움직임이 보입니다
    requestAnimationFrame(() => drawer.classList.add('is-open'));
    document.body.classList.add('drawer-open');
    openBtn.setAttribute('aria-expanded', 'true');
    closeBtn.focus();
  }

  function close() {
    if (drawer.hidden) return;
    drawer.classList.remove('is-open');
    document.body.classList.remove('drawer-open');
    openBtn.setAttribute('aria-expanded', 'false');
    setTimeout(() => { drawer.hidden = true; }, 260);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* ---------- 보기: 목록/격자 ---------- */
  // 목록/격자는 메인 화면의 보기 방식이라, 고르면 저장하고 메인으로 갑니다
  const view = load('designhub:view') === 'list' ? 'list' : 'grid';
  drawer.querySelectorAll('.drawer__opt[data-view]').forEach(b => {
    b.classList.toggle('is-active', b.dataset.view === view);
    b.addEventListener('click', () => {
      save('designhub:view', b.dataset.view);
      location.href = 'https://designrefs.com/';
    });
  });

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  document.getElementById('drawer-backdrop').addEventListener('click', close);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
