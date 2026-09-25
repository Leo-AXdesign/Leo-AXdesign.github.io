/* 디자인 허브 — 정적 페이지(카테고리 · 읽을거리 · 디자인 잡담 등) 공통 스크립트.
   메인 화면은 app.js 가 같은 일을 합니다.

   - 메뉴의 즐겨찾기 개수를 브라우저 저장소에서 읽어 채웁니다
   - 좁은 화면에서 햄버거 버튼으로 메뉴 서랍을 엽니다 */
(function () {
  'use strict';

  /* ---------- 즐겨찾기 개수 ---------- */
  try {
    const raw = localStorage.getItem('designhub:bookmarks');
    const n = raw ? JSON.parse(raw).length : 0;
    document.querySelectorAll('[data-bm-count]').forEach(el => { el.textContent = n; });
  } catch (e) { /* 저장소를 못 쓰는 환경이면 0 으로 둡니다 */ }

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
    // 지금 보고 있는 항목이 보이도록 서랍 안에서 스크롤
    const active = drawer.querySelector('.nav__item.is-active');
    if (active) active.scrollIntoView({ block: 'center' });
  }

  function close() {
    if (drawer.hidden) return;
    drawer.classList.remove('is-open');
    document.body.classList.remove('drawer-open');
    openBtn.setAttribute('aria-expanded', 'false');
    setTimeout(() => { drawer.hidden = true; }, 260);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  document.getElementById('drawer-backdrop').addEventListener('click', close);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
