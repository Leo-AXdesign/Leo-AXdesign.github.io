// 이 파일은 tools/build-articles.py 가 만듭니다. 직접 고치지 마세요.
// 글은 content/articles/*.md 에서 고칩니다.
const ARTICLES = [
  { slug: "open-image-model-license", title: "투명 배경까지 뽑아 주는 무료 이미지 모델, 일에 써도 될까", desc: "기업들이 값싼 오픈 모델로 옮겨 가는 사이, 알리바바의 새 이미지 모델 Qwen-Image-2.1은 상업적 이용을 막았다. 내려받을 수 있다는 것과 일에 써도 된다는 것의 차이를 정리했다.", date: "2026-09-28", tag: "AI 디자인", min: 3 },
  { slug: "ai-price-cut-week", title: "한 주 만에 반값이 된 AI, 디자인 툴 값도 내려갈까", desc: "9월 22일 하루에 Opus 5.5, GPT-6 Sol, Luna가 한꺼번에 나오며 가격표가 크게 바뀌었다. 디자이너가 내는 크레딧과 구독료에는 어떻게 이어질지 숫자로 짚었다.", date: "2026-09-27", tag: "AI 디자인", min: 4 },
  { slug: "claude-fable-5-1-vs-gpt-6-astra", title: "Claude Fable 5.1 vs GPT-6 아스트라, 숫자로 비교해 보면", desc: "이틀 차이로 나온 두 최상위 모델. 공식 사양, 제3자 평가, 디자이너들의 초기 반응을 출처와 함께 나란히 놓았다.", date: "2026-09-26", tag: "AI 디자인", min: 4 },
  { slug: "ai-design-tools-in-practice", title: "AI가 시안을 서른 장 뽑아 줘도 일이 줄지 않는 이유", desc: "탐색과 양산은 AI에게, 방향과 검수는 사람에게. 한동안 써 보고 나서야 보인 경계에 대하여.", date: "2026-09-25", tag: "AI 디자인", min: 3 },
  { slug: "describing-design-style", title: "‘느낌 있게’를 말로 옮기는 일", desc: "클라이언트에게도, 프롬프트 창에도 결국 말로 설명해야 한다. 스타일을 여섯 겹으로 쪼개서 말하는 방법.", date: "2026-09-25", tag: "디자인", min: 3 },
  { slug: "how-to-collect-references", title: "저장만 하고 다시 열지 않는 레퍼런스들", desc: "보드는 스무 개가 넘는데 작업할 땐 처음부터 다시 검색한다. 꺼내 쓸 수 있게 모으는 법.", date: "2026-09-25", tag: "디자인", min: 2 },
  { slug: "korean-design-community-map", title: "디자이너는 어디서 이야기를 나눌까", desc: "읽고 싶을 때, 만든 걸 보여 주고 싶을 때, 급하게 묻고 싶을 때. 국내 디자인 커뮤니티를 쓰임새대로 나눠 봤다.", date: "2026-09-25", tag: "커뮤니티", min: 2 },
  { slug: "ai-image-commercial-use", title: "AI로 만든 이미지, 클라이언트 작업에 써도 될까", desc: "저작권, 약관, 닮은꼴, 계약서. 실무에서 확인해야 할 것들을 순서대로 적었다.", date: "2026-09-25", tag: "AI 디자인", min: 3 },
];
