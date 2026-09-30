---
slug: openai-devday-2026-designers
title: 챗GPT 안으로 들어온 캔바·피그마·어도비, 데브데이에서 디자이너가 볼 것
desc: 오늘 새벽 오픈AI 데브데이에서 발표가 스무 개 넘게 쏟아졌다. 그중 디자인 작업과 닿는 것만 골라, 그림과 숫자로 정리했다.
date: 2026-09-30
order: 1
tag: AI 디자인
related: ai, tools
---

오늘 새벽 2시, 오픈AI의 개발자 행사 데브데이가 샌프란시스코에서 열렸다. 발표만 스무 개가 넘었다.

제일 크게 다뤄진 건 '닷(dots)'이다. 앱을 닫아도 뒤에서 계속 일하는 에이전트다. 그런데 디자이너 입장에서 오래 들여다본 건 다른 쪽이었다. 캔바, 피그마, 어도비가 챗GPT 화면 안으로 들어왔다.

**먼저 밝혀 둘 것.** 발표 직후라 아직 직접 써 본 사람의 후기가 거의 없다. 아래 내용은 오픈AI 발표와 행사를 정리한 기사들을 바탕으로 했다. 나는 이 사이트를 클로드 코드로 만들고 있다는 것도 함께 적어 둔다.

## 플러그인이 들어가는 세 자리

새로 나온 건 '플러그인 익스텐션'이다. 대화창 안에서 링크만 건네던 예전 방식과 달리, 앱 화면 자체를 챗GPT 안에 띄운다. 들어가는 자리는 세 군데다.

![챗GPT 화면에서 플러그인이 들어가는 세 자리. 발표를 바탕으로 그린 구조도이고 실제 화면과는 다르다.](https://designrefs.com/articles/img/chatgpt-plugin-extensions.svg)

첫째는 대화 옆 사이드 패널. 캔바가 여기에 디자인 도구를 넣었다. 시안을 뽑아 달라고 한 다음, 대화를 닫지 않고 옆에서 바로 고치는 흐름이다.

둘째는 파일 뷰어. 대화에 올라온 파일을 앱으로 연다. 어도비는 PDF는 애크로뱃으로, 이미지는 포토샵으로 열리게 했다.

셋째는 입력창의 @호출이다. 피그마는 파일 검색을 여기에 넣었다. "@Figma 지난주 랜딩 시안" 하는 식으로 불러낸다.

플러그인은 무료를 포함한 모든 요금제에서 설치할 수 있다. 다만 파일 뷰어와 @호출은 데스크톱 앱에서만 된다. 무료·Go 요금제의 웹 버전은 "곧"이라고만 했다. 기업용으로는 어도비, 피그마를 포함한 32개 회사가 들어간 마켓플레이스도 열었다.

## 네 번째 시도라는 것

반가운 소식인데, 한 가지는 알고 가는 게 좋다. 챗GPT에 남의 앱을 들이려는 시도가 이번이 처음이 아니다.

![챗GPT 앱 플랫폼이 3년 동안 네 번 바뀌었다. 첫 플러그인은 1년 만에 닫혔고, GPT 스토어는 올해 12월에 닫는다.](https://designrefs.com/articles/img/openai-app-platforms.svg)

2023년 3월의 플러그인은 1년 남짓 만에 닫혔다. 같은 해 11월에 나온 GPTs와 GPT 스토어는 12월 11일에 문을 닫는다. 2025년 10월에 Apps SDK가 나왔고, 이번이 네 번째다. 브라질의 한 기술 매체는 이걸 두고 "3년 사이 네 번째"라고 꼬집었다.

그러니 작업 흐름을 통째로 여기에 걸기보다는, 자주 쓰는 한두 개를 먼저 써 보는 정도가 알맞다. 플랫폼이 또 바뀌어도 원본 파일은 늘 피그마와 어도비에 남아 있다는 점도 기억해 두자.

## 디자인 작업과 닿는 다른 발표들

**페이지(Pages).** 사람과 에이전트가 함께 쓰는 새 문서 형식이다. 리서치, 도표, 데이터 시각화를 한 문서 안에서 같이 만든다. 기획서나 리서치 정리를 자주 쓰는 사람이라면 볼 만하다.

**함께 고치는 슬라이드.** 여러 사람이 한 덱을 동시에 고친다. 파워포인트와 구글 슬라이드로 내보낼 수 있고, 몇 주 안에 나온다고 했다.

**스페이스(Spaces).** 팀이 대화와 에이전트를 한곳에 모아 두는 공간이다. 슬랙과 팀즈에서 @ChatGPT로 부르는 기능도 같이 나왔다.

**닷(dots).** 목표를 주면 자기 클라우드 컴퓨터와 브라우저로 계속 일하는 에이전트다. GPT-6 아스트라로 돌고, 4,000개가 넘는 앱에 연결된다. 프로와 비즈니스 프리미엄 요금제에서 첫 번째 닷이 포함된다.

## 그리고 가격

모델 쪽에서는 GPT-6.1 Sol이 나왔다. 오픈AI는 최상위 모델인 GPT-6 아스트라와 거의 비슷한 성능을 5분의 1 값에 낸다고 했다. 100만 토큰에 입력 2달러, 출력 10달러다.

![독립 평가 기관의 종합 지수와 과제 하나당 비용. 점수 차이는 1점인데 비용은 4분의 1도 안 된다.](https://designrefs.com/articles/img/devday-sol-cost.svg)

Artificial Analysis 종합 지수로 보면 GPT-6.1 Sol은 52점으로 아스트라(53점)와 1점 차이다. 지수 과제 하나당 비용은 0.72달러로 아스트라의 4분의 1이 안 된다. 1위는 여전히 Claude Opus 5.5(58점)다.

오픈AI가 직접 낸 표에서는 차이가 좀 더 벌어진다. 과학 분야 터미널 작업 평가에서 Sol은 57.0%, 아스트라는 68.1%였다. 모든 일에서 아스트라를 대신하지는 못한다는 뜻이다.

흥미로운 건 2달러·10달러라는 값이다. 하루 전에 나온 [Claude Sonnet 5.5](https://designrefs.com/articles/claude-sonnet-5-5-design/)와 정확히 같다. 중간 칸에서 두 회사가 같은 값으로 맞붙었다.

구독 요금제도 바뀌었다. 월 500달러짜리 최상위 요금제(Pro 500)가 새로 생겼고, 월 200달러 요금제는 새로 가입하는 사람의 사용량이 절반으로 줄었다. 기존 가입자는 그대로다. 발표 직후부터 이 부분을 두고 말이 많다.

## 그래서 지금은

오늘 당장 할 일은 많지 않다. 데스크톱 챗GPT 앱을 쓰고 있다면, 평소 쓰는 캔바·피그마·어도비 플러그인을 하나 설치해서 대화 옆에서 얼마나 쓸 만한지 보는 정도면 된다.

더 중요한 건 흐름이다. 디자인 툴이 챗GPT 안으로 들어오고, 챗GPT는 디자인 툴 안으로 들어간다. 어디서 시작하든 같은 파일에 닿게 되는 쪽으로 가고 있다. 그 사이에서 원본을 어디에 두고, 마지막 확인을 누가 하는지는 여전히 사람이 정할 일이다. 이 경계에 대해서는 [AI가 시안을 서른 장 뽑아 줘도 일이 줄지 않는 이유](https://designrefs.com/articles/ai-design-tools-in-practice/)에 따로 적었다.

※ 출처: [OpenAI DevDay 2026 정리](https://openai.com/index/devday-2026-recap/), [the-decoder](https://the-decoder.com/openais-reveals-a-new-chatgpt-that-looks-less-like-a-chatbot-and-more-like-an-operating-system/), [antihype.com.br](https://antihype.com.br/c/software/plugin-extensions-chatgpt-apps-na-barra-lateral/), [DEV Community 발표 정리](https://dev.to/axrisi/openai-devday-2026-every-announcement-with-prices-and-availability-1mbh), [The Next Web](https://thenextweb.com/news/openai-devday-pro-200-usage-cut-pro-500-plan), [THE DAILY BRIEF](https://www.beri.net/article/gpt-6-1-sol-devday-2026-astra-fifth-price-terminal-bench-score-gap-cost-per-task).
