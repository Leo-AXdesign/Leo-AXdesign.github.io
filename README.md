# 디자인 허브

디자인 레퍼런스 사이트 주소모음. 빌드 없이 `index.html`을 열면 바로 동작하는 정적 사이트입니다.

## 구조

```
.
├── index.html                    # 마크업
├── css/style.css                 # 스타일 (라이트/다크 테마)
├── js/
│   ├── data.js                   # ★ 사이트 · 스타일 · 트렌드 · 용어 데이터 (여기만 수정하면 됨)
│   └── app.js                    # 검색 · 필터 · 즐겨찾기 · 테마 · 호버 미리보기
├── favicon.svg, favicon.ico      # 파비콘
├── og-image.png                  # 공유 미리보기 이미지 (1200×630)
├── .nojekyll                     # GitHub Pages 가 Jekyll 처리를 건너뛰도록
└── .github/workflows/deploy.yml  # main 에 push 하면 Pages 로 자동 배포
```

## 사이트 추가하기

`js/data.js`의 `SITES` 배열에 객체를 추가합니다.

```js
{ name: '사이트 이름', url: 'https://example.com', desc: '한 줄 설명', cat: 'uiux', tags: ['한국', '무료'] },
```

- `cat`: `CATEGORIES`의 `id` 중 하나 (`uiux`, `graphic`, `color`, `typo`, `asset`, `dev`, `tool`, `freelance`, `job`, `ai`, `community`, `creator`)
- `tags`: `한국`, `무료`, `유료`, `AI` 를 조합 (상단 필터 칩과 연동됨)

카테고리를 추가하려면 `CATEGORIES` 배열에 `{ id, label, desc }`를 추가하면 필터 필과 섹션이 자동으로 생깁니다.

## 인사이트 (스타일 사전 · 2026 트렌드)

사이드바 "인사이트" 그룹에서 볼 수 있습니다. 데이터는 모두 `js/data.js`에 있습니다.

- `STYLES`: 유명 그래픽 디자인 양식 34개. `{ name, en, era, desc, traits, people?, q, wiki?, img?, imgTitle? }` — `q`는 핀터레스트 검색어이며 이름 클릭 시 열립니다. `img`는 대표 이미지(위키미디어 공용의 퍼블릭 도메인·CC 이미지), `imgTitle`은 출처 표기로 마우스를 올리면 보입니다. 이미지가 없으면 스타일 이름 타일이 대신 표시됩니다.
- `GLOSSARY`: 용어 사전 155개. `{ term, en, group, desc }` — `group`은 `GLOSSARY_GROUPS`의 id(타이포그래피, 편집·인쇄, 컬러, 그래픽·브랜딩, UI 설계, UX·리서치, 개발 협업). 페이지 상단 필로 그룹을 골라 볼 수 있습니다.
- `TRENDS`: 2026 트렌드 키워드 15개. `{ name, area, desc, q, link? }` — 해마다 갱신하세요.
- `TREND_SOURCES`: 트렌드 페이지 하단에 표시되는 참고 리포트 링크.
- 검색창에 입력하면 사이트뿐 아니라 스타일·트렌드도 함께 검색됩니다.
- `#styles`, `#trends`, `#glossary`, `#uiux` 처럼 URL 해시로 특정 화면에 바로 접근할 수 있습니다.
- `index.html`을 서버 없이 더블클릭(`file://`)으로 열어도 모든 화면 전환이 동작합니다.

## 크리에이터 / 채널

`SITES`에 `cat: 'creator'`로 등록된 유튜브·인스타그램·팟캐스트 47개. 태그로 `유튜브`, `인스타그램`, `팟캐스트`, `한국`을 씁니다. 모든 채널 주소는 등록 시점에 실제 존재 여부를 확인했습니다.

## 로컬 실행

```bash
python3 -m http.server 5173
```

이후 http://localhost:5173 접속. 파일을 직접 더블클릭해서 열어도 됩니다.

## GitHub Pages 배포

빌드가 필요 없는 정적 사이트라 저장소에 올리기만 하면 됩니다. `.github/workflows/deploy.yml`이 들어 있어 `main` 브랜치에 push 하면 자동 배포됩니다.

**1. GitHub에서 빈 저장소를 만듭니다** (README·.gitignore 추가 없이). 이름은 예를 들어 `design-hub`.

**2. 이 폴더에서 원격 저장소를 연결하고 push 합니다.** `<깃허브아이디>`와 저장소 이름을 본인 것으로 바꾸세요.

```bash
git remote add origin https://github.com/<깃허브아이디>/design-hub.git
git push -u origin main
```

**3. 저장소 → Settings → Pages → Build and deployment → Source 를 "GitHub Actions" 로 바꿉니다.**

**4. 1~2분 뒤 아래 주소에서 열립니다.**

```
https://<깃허브아이디>.github.io/design-hub/
```

이후에는 파일을 고치고 `git add . && git commit -m "메시지" && git push` 하면 자동으로 다시 배포됩니다.

### 배포 후 한 번만 손볼 것

- `index.html` 상단의 `og:url`, `og:image`에 있는 `USERNAME`을 본인 깃허브 아이디로 바꾸면 카카오톡·슬랙 공유 시 미리보기 이미지(`og-image.png`)가 뜹니다.
- 커밋 작성자 정보는 이 저장소에만 적용해 두었습니다. 바꾸려면:

```bash
git config user.name "이름" && git config user.email "메일주소"
```

### 다른 배포 방법

- **Netlify · Vercel · Cloudflare Pages**: 저장소를 연결하고 빌드 명령은 비워 둔 채 배포 디렉터리만 루트(`.`)로 지정하면 됩니다.
- **직접 열기**: 서버 없이 `index.html`을 더블클릭해도 모든 기능이 동작합니다.

## 기능

- 카테고리별 탐색, 사이트명·설명·도메인·태그 통합 검색 (`/` 키로 검색창 포커스)
- 한국 / 무료 / 유료 / AI 태그 필터
- ★ 즐겨찾기 (localStorage 저장)
- 라이트 / 다크 테마 (시스템 설정 자동 감지), 목록 / 격자 보기 (선택 저장)
- 파비콘은 Google Favicon 서비스에서 자동 로드
- 스타일 사전 대표 이미지는 Wikimedia Commons에서 불러오며, 각 이미지의 출처·라이선스는 `imgTitle`에 기록되어 있습니다.
