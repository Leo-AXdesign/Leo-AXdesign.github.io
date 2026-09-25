// 이 파일은 tools/build-articles.py 가 만듭니다. 직접 고치지 마세요.
// 글은 content/articles/*.md 에서 고칩니다.
const ARTICLES = [
  { slug: "ai-design-tools-in-practice", title: "AI 디자인 툴, 실무에서 갈리는 지점", desc: "프롬프트 한 줄로 시안이 서른 장 나오는데 정작 일은 안 줄어드는 이유. AI가 대신해 주는 구간과 여전히 손으로 해야 하는 구간을 나눠 봤습니다.", date: "2026-09-25", tag: "AI 디자인", min: 3 },
  { slug: "describing-design-style", title: "디자인 스타일을 말로 옮기는 법", desc: "\"느낌 있게 해주세요\"를 받았을 때, 그리고 프롬프트를 쓸 때 필요한 어휘. 스타일을 여섯 겹으로 쪼개서 말하는 방법을 정리했습니다.", date: "2026-09-25", tag: "디자인", min: 4 },
  { slug: "how-to-collect-references", title: "레퍼런스를 모으기만 하고 못 쓰는 이유", desc: "북마크 폴더와 핀터레스트 보드가 쌓이는데 정작 작업할 때 못 꺼내 쓰는 문제. 꺼내 쓸 수 있게 모으는 방법을 정리했습니다.", date: "2026-09-25", tag: "디자인", min: 3 },
  { slug: "korean-design-community-map", title: "국내 디자인 커뮤니티, 어디서 뭘 얻나", desc: "서핏부터 디스콰이엇, 커리어리, 노트폴리오까지. 성격이 다 다른 국내 디자인 커뮤니티를 목적별로 나눠 정리했습니다.", date: "2026-09-25", tag: "커뮤니티", min: 3 },
  { slug: "ai-image-commercial-use", title: "AI로 만든 이미지, 클라이언트 작업에 써도 되나", desc: "저작권이 생기는지, 약관은 뭘 보는지, 계약서에 뭘 적어야 하는지. 실무에서 확인해야 할 순서대로 정리했습니다.", date: "2026-09-25", tag: "AI 디자인", min: 4 },
];
