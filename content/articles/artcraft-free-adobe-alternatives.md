---
slug: artcraft-free-adobe-alternatives
title: AI로 다시 만든 무료 '포토샵' 일곱 개, 디자이너는 갈아탈 수 있을까
desc: 한 개발자가 AI로 어도비 앱 일곱 개를 대신할 무료 오픈소스 앱을 만들고 있다. 포토샵 대체 앱은 PSD를 열고 저장하지만 아직 초기 알파다. 지금 어디까지 왔는지, 디자이너가 볼 것은 무엇인지 정리했다.
date: 2026-10-09
order: 1
tag: AI 디자인
related: ai, tools
---

이번 주 디자인 쪽에서 화제가 된 소식이 있다. 한 개발자가 포토샵, 일러스트레이터, 프리미어, 라이트룸, 애프터 이펙트, 인디자인, 애크로뱃을 대신할 앱 일곱 개를 무료로 공개했다. 이름은 ArtCraft. 그리고 이걸 AI로 만들었다고 했다.

"어도비 구독을 끊을 수 있다"는 제목이 여기저기 붙었다. 실제로 그런지, 지금 어디까지 왔는지 차분히 들여다봤다.

**먼저 밝혀 둘 것.** 이 앱들은 Anthropic의 Claude Opus 5.5로 만들어졌다고 알려졌다. 나는 이 사이트를 같은 회사의 클로드 코드로 만들고 있다. 그래서 개발자의 주장보다 저장소에 적힌 내용과 다른 매체의 확인을 중심으로 옮겼다. 앱은 직접 설치해 보지 않았다.

## 누가, 왜, 어떻게

만든 사람은 소프트웨어 엔지니어 브랜든 토마스(Brandon Thomas)다. 계기는 어도비의 해지 수수료였다고 밝혔다. 어도비의 '연간 약정, 월 결제' 요금제는 1년을 채우기 전에 해지하면 남은 금액의 절반을 위약금으로 낸다. 미국 연방거래위원회(FTC)가 2024년 이 문제로 어도비를 고소했고, 합의로 끝났다.

만드는 방식은 이렇다.

- **AI로 짰다.** 코드는 Claude Opus 5.5를 써서 썼다고 했다.
- **러스트(Rust)로 새로 만들었다.** 어도비 코드를 가져온 게 아니라, 쓰는 법과 생김새만 보고 처음부터 다시 만드는 '클린룸' 방식이라고 설명했다.
- **무료, 오픈소스.** MIT와 Apache 2.0 라이선스로 공개해서 누구나 내려받고 고칠 수 있다.

## 일곱 개, 지금 어디까지 왔나

![ArtCraft 일곱 개 앱의 현재 상태. 실선은 초기 알파, 점선은 개발 중이다.](https://designrefs.com/articles/img/artcraft-suite.svg)

쓸 수 있는 단계에 온 건 두 개뿐이다. 포토샵을 대신하는 PhotoCraft와 애크로뱃을 대신하는 앱이 '초기 알파'고, 나머지 다섯 개는 아직 '개발 중'이다. 개발자는 처음에 한 달 안에 기능을 맞추겠다고 했다가 "몇 년이 아니라 몇 달"로 말을 바꿨다.

## PhotoCraft는 PSD를 연다

가장 앞선 PhotoCraft는 디자이너에게 가장 중요한 걸 먼저 챙겼다. PSD 파일이다. 8비트, 16비트, 32비트 PSD와 큰 파일용 PSB를 열고 저장할 수 있다고 저장소에 적혀 있다.

![PhotoCraft로 시험 파일 309개를 열었다 다시 저장했더니 307개가 제대로 그려졌다. 개발자 자체 시험이다.](https://designrefs.com/articles/img/photocraft-psd.svg)

공개된 PSD 시험 파일 309개를 열었다 다시 저장했을 때, 307개가 제대로 그려졌다고 한다. 숫자만 보면 높다. 다만 이건 개발자가 직접 돌린 시험이고, 다시 저장한 파일은 원본과 바이트까지 같지는 않다. 레이어 정보와 합쳐진 이미지를 새로 쓰기 때문이다.

그리고 빠진 것도 분명하다.

| | 지금 PhotoCraft에서는 |
|---|---|
| PSD·PSB 열기와 저장 | 됨 (8·16·32비트) |
| 생성형 AI 기능 | 없음 |
| 도구 | 포토샵 대비 20개쯤 빠짐 |
| 글자 다루기 | 아직 약함 |
| 플러그인 | 쓸 수 없음 |
| 애프터 이펙트 파일(AEP) | EffectCraft에서 못 엶 |
※ 출처: [PhotoCraft 저장소](https://github.com/storytold/photocraft), [Windows Forum 정리](https://windowsforum.com/news/artcrafts-open-source-adobe-alternatives-on-windows-what-works-in-alpha.447649/), [Cybernews](https://cybernews.com/ai-news/ai-adobe-alternatives-open-source/). 일찍 써 본 사람들은 아직 실제 작업을 대신할 수준은 아니라고 했다.

법적인 걱정도 남아 있다. 코드를 베끼지 않았더라도, 화면 생김새가 너무 비슷하면 '트레이드 드레스' 문제가 될 수 있고, 어도비는 기능 동작 방식에 관한 특허도 많이 갖고 있다는 지적이 나왔다.

## 디자이너가 볼 것은 '앱'이 아니라 '파일'

이 소식에서 디자이너가 챙길 건, 당장 어도비를 끊을 수 있느냐가 아니다. 지금 답은 분명히 "아니요"다. 클라이언트 작업을 알파 버전 앱에 맡길 수는 없다.

오히려 볼 것은 두 가지다.

**하나, 우리를 붙잡고 있는 건 파일 형식이다.** 디자이너가 어도비를 못 떠나는 이유는 앱이 좋아서이기도 하지만, 주고받는 파일이 PSD, AI, INDD, AEP이기 때문이기도 하다. PhotoCraft가 가장 먼저 PSD 호환에 힘을 쏟은 것도 그래서다. 대체 앱이 진짜로 위협이 되는 순간은 기능이 많아질 때가 아니라, 클라이언트가 보낸 파일을 그대로 열고 그대로 돌려줄 수 있을 때다.

**둘, 소프트웨어를 만드는 값이 내려가고 있다.** 사람 한 명이 AI와 함께 일곱 개 앱의 뼈대를 내놓았다. 완성도는 아직 멀지만, 앞으로 이런 시도는 더 많아질 거다. 어도비 입장에서는 기능 경쟁보다 가격과 해지 조건에 대한 압박이 먼저 올 가능성이 크다. 디자이너에게는 나쁘지 않은 일이다.

## 그래서 지금은

갈아타지는 말고, 지켜보면서 한 가지만 해 보자.

1. **작업 파일의 사본으로 시험하기.** 평소 쓰는 PSD 하나를 복사해서 PhotoCraft로 열어 보자. 레이어, 마스크, 조정 레이어, 글자 레이어 중 어디가 깨지는지 보면, 이 앱이 내 작업에 얼마나 가까운지 감이 온다. 원본은 절대 덮어쓰지 말자.
2. **구독 조건 다시 보기.** 어도비를 '연간 약정, 월 결제'로 쓰고 있다면, 해지 시점과 위약금 조건을 한 번 확인해 두자. 1년을 채운 뒤에는 위약금 없이 해지할 수 있다.
3. **이미 있는 무료 대안도 함께.** 오래된 무료 도구(김프, 잉크스케이프, 다빈치 리졸브 등)는 완성도에서 아직 한참 앞서 있다. 새 소식에 들뜨기 전에 비교 기준으로 삼기 좋다.

AI 시대에 디자인 도구가 어떻게 바뀌는지는 [AI가 시안을 서른 장 뽑아 줘도 일이 줄지 않는 이유](https://designrefs.com/articles/ai-design-tools-in-practice/)에, 디자인 툴 모음은 [디자인 툴](https://designrefs.com/tools/)에 정리해 두었다.

※ 출처: [Cybernews](https://cybernews.com/ai-news/ai-adobe-alternatives-open-source/), [GIGAZINE](https://gigazine.net/gsc_news/en/20261005-artcraft-crafting-apps/), [PhotoCraft 저장소](https://github.com/storytold/photocraft), [Windows Forum](https://windowsforum.com/news/artcrafts-open-source-adobe-alternatives-on-windows-what-works-in-alpha.447649/), [Softonic](https://en.softonic.com/articles/artcraft-is-now-a-seven-app-open-source-creative-cloud-alternative), [Engadget (FTC 합의)](https://www.engadget.com/big-tech/adobe-agrees-to-pay-settlement-for-making-its-subscriptions-hard-to-cancel-210336635.html).
