// 이 파일은 tools/build-articles.py 가 만듭니다. 직접 고치지 마세요.
// 글은 content/articles/*.md 에서 고칩니다.
const ARTICLES = [
  { slug: "ai-design-tools-in-practice", title: "AI가 시안을 서른 장 뽑아 줘도 일이 줄지 않는 이유", desc: "탐색과 양산은 AI에게, 방향과 검수는 사람에게. 한동안 써 보고 나서야 보인 경계에 대하여.", date: "2026-09-25", tag: "AI 디자인", min: 3 },
  { slug: "describing-design-style", title: "‘느낌 있게’를 말로 옮기는 일", desc: "클라이언트에게도, 프롬프트 창에도 결국 말로 설명해야 한다. 스타일을 여섯 겹으로 쪼개서 말하는 방법.", date: "2026-09-25", tag: "디자인", min: 3 },
  { slug: "how-to-collect-references", title: "저장만 하고 다시 열지 않는 레퍼런스들", desc: "보드는 스무 개가 넘는데 작업할 땐 처음부터 다시 검색한다. 꺼내 쓸 수 있게 모으는 법.", date: "2026-09-25", tag: "디자인", min: 2 },
  { slug: "korean-design-community-map", title: "디자이너는 어디서 이야기를 나눌까", desc: "읽고 싶을 때, 만든 걸 보여 주고 싶을 때, 급하게 묻고 싶을 때. 국내 디자인 커뮤니티를 쓰임새대로 나눠 봤다.", date: "2026-09-25", tag: "커뮤니티", min: 2 },
  { slug: "ai-image-commercial-use", title: "AI로 만든 이미지, 클라이언트 작업에 써도 될까", desc: "저작권, 약관, 닮은꼴, 계약서. 실무에서 확인해야 할 것들을 순서대로 적었다.", date: "2026-09-25", tag: "AI 디자인", min: 3 },
];
