(function () {
  var root = document.documentElement;
  var body = document.body;
  var isItem = body.classList.contains('item-view');
  var isHome = location.pathname === '/' && !location.search.match(/[?&](q|updated-max|max-results)=/);

  // 다크 모드 버튼
  var top = document.querySelector('.centered-top');
  if (top && !document.querySelector('.theme-btn')) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'theme-btn'; b.setAttribute('aria-label', '다크 모드 전환');
    b.innerHTML = '<svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
    b.addEventListener('click', function () {
      var dark = root.getAttribute('data-theme') !== 'dark';
      if (dark) root.setAttribute('data-theme', 'dark'); else root.removeAttribute('data-theme');
      try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
    });
    top.appendChild(b);
  }

  // 홈 머리말 + '최근 글' 제목
  var main = document.querySelector('.centered-bottom .main');
  if (main && !isItem) {
    if (isHome) {
      var hero = document.createElement('section');
      hero.className = 'ah-hero';
      hero.innerHTML = '<h1>AI 한입<span>.</span></h1><p>하루 한입, 따라하면 끝나는 AI 활용법. 처음 써보는 분도 그대로 따라 하면 돼요.</p>';
      main.parentNode.insertBefore(hero, main);
    }
    var blog = main.querySelector('.widget.Blog');
    if (blog) {
      var label = document.createElement('h2');
      label.className = 'section__label';
      var q = new URLSearchParams(location.search).get('q');
      var m = location.pathname.match(/\/search\/label\/([^/?]+)/);
      label.textContent = m ? decodeURIComponent(m[1]) : (q ? '‘' + q + '’ 검색 결과' : '최근 글');
      blog.parentNode.insertBefore(label, blog);
    }
    var feat = main.querySelector('.widget.FeaturedPost');
    if (feat && isHome) {
      var fl = document.createElement('h2'); fl.className = 'section__label'; fl.textContent = '추천 글';
      feat.parentNode.insertBefore(fl, feat);
    }
  }

  // 프롬프트 복사 버튼
  if (isItem) {
    Array.prototype.forEach.call(document.querySelectorAll('.post-body blockquote'), function (q) {
      if (q.querySelector('.copy-btn')) return;
      var c = document.createElement('button');
      c.type = 'button'; c.className = 'copy-btn'; c.textContent = '복사';
      c.addEventListener('click', function () {
        var t = q.innerText.replace(/복사(됨)?\s*$/, '').trim();
        if (navigator.clipboard) navigator.clipboard.writeText(t).then(function () {
          c.textContent = '복사됨'; setTimeout(function () { c.textContent = '복사'; }, 1500);
        });
      });
      q.appendChild(c);
    });
  }
})();
