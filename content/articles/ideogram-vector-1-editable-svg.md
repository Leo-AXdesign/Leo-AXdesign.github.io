---
slug: ideogram-vector-1-editable-svg
title: AI로 뽑은 로고를 확대하니 뭉개질 때, 아이디오그램 벡터 1.0에서 확인할 것
desc: Ideogram이 10월 22일 첫 벡터 모델 Vector 1.0을 냈다. 글이나 이미지에서 편집 가능한 SVG를 만든다고 한다. 공식 API 문서와 보도로 확인한 내용, 가격, 레이어와 글자 처리처럼 아직 확인되지 않은 부분을 정리했다.
date: 2026-10-24
order: 1
tag: AI 디자인
related: ai, tools, graphic
---

클라이언트 메일은 두 줄이다. "AI로 뽑은 로고 마음에 들어요. 명함이랑 현수막에 다 쓸 거라 원본 파일 주세요."

받은 건 PNG 한 장이다. 현수막 크기로 키우면 가장자리가 뭉개진다. 인쇄소는 AI나 SVG 같은 벡터 파일을 달라고 한다. 이미지 AI 결과물을 일에 쓰려다 이 지점에서 막히는 경우가 많다.

Ideogram이 10월 22일 첫 벡터 모델 'Ideogram Vector 1.0'을 냈다. 글로 설명하면 SVG 파일이 나오고, 이미 있는 그림을 올리면 벡터로 바꿔 준다고 한다. 이 글은 공식 API 문서와 보도로 직접 확인한 것만 적는다.

![Ideogram 개발자 문서의 SVG 생성 API 페이지. 출처: developer.ideogram.ai/api-reference/vectors/generate-svg (캡처일 2026-10-24)](https://designrefs.com/articles/img/ideogram-vector-1-editable-svg-shot1.webp)
## 먼저 밝혀 둘 것

- 이 모델을 직접 돌려 보지는 않았다. 아래는 Ideogram 개발자 문서와 발표를 옮긴 보도에서 읽은 내용이다.
- Ideogram 발표 글(X)과 블로그, 제품 페이지는 열리지 않았다(접속 거부). 발표 문구는 검색에 잡힌 인용과 보도를 통해서만 봤다.
- 가격은 공식 API 문서 페이지에 적혀 있지 않았다. 아래 가격표는 문서를 인용한 외부 글 두 곳에서 가져왔고 서로 일치했다.
- 외부 기관이 결과물을 시험해 낸 자료는 찾지 못했다. "깔끔하다"는 말은 아직 Ideogram 쪽 설명이다.
- 앱 안에서 어느 요금제부터 쓸 수 있는지, 크레딧이 얼마나 드는지는 확인되지 않았다.

## 래스터와 벡터, 한 줄로

래스터는 점(픽셀)으로 그린 그림이라 키우면 뭉개진다. 벡터는 점과 선의 계산식으로 그린 그림이라 얼마든 키워도 선이 선명하다. 로고, 아이콘, 간판, 굿즈 인쇄는 벡터를 요구하는 일이 흔하다. 지금까지 많은 이미지 AI는 래스터만 내놓았고, 그걸 벡터로 바꾸는 일은 별도 작업이었다.

Ideogram의 발표 문구는 이렇게 전해진다. 텍스트 프롬프트로 "부드러운 그라데이션과 또렷한 글자체"를 가진 깨끗하고 편집 가능한 SVG를 만들거나, 어떤 이미지든 세밀하고 확대해도 되는 벡터로 바꾼다. Ideogram 앱과 API에서 쓸 수 있다.

## 공식 문서에서 읽은 것

API 문서에는 두 가지 작업이 따로 있다.

| 작업 | 주소(엔드포인트) | 넣는 것 |
|---|---|---|
| 글로 SVG 만들기 | POST /v2/svg/generate/ideogram-vector-1 | 프롬프트(필수), 참고 이미지(선택), 화면비, 품질, 장수, 시드 |
| 이미지를 SVG로 바꾸기 | POST /v2/svg/vectorize/ideogram-vector-1 | JPEG·PNG·WEBP 파일(50MB까지), 세밀도 모드 |

※ 출처: [Ideogram 개발자 문서: Generate SVG](https://developer.ideogram.ai/api-reference/vectors/generate-svg.md), [같은 문서: Vectorizer](https://developer.ideogram.ai/api-reference/vectors/image-to-svg.md). 표는 두 페이지의 매개변수를 줄여 옮긴 것이다.

이미지를 바꿀 때 고르는 세밀도 모드는 문서에 세 가지다. `simple`은 도형 수를 줄이고, `detailed`는 잔 디테일을 살리고, `auto`는 이미지에 맞춰 알아서 정한다. 외부 글 중에는 모드를 Simple과 Default로 적은 곳이 있었는데, 공식 문서 표기는 위와 같다.

그 밖에 문서에서 확인한 것은 이렇다.

- 결과물은 기본으로 비공개다. 기업용은 항상 비공개다.
- 요청을 보내면 바로 파일이 오지 않고 작업 번호(`generation_id`)를 받아 결과를 따로 가져온다.
- `dry_run`을 켜면 생성도 청구도 하지 않고 이 요청의 값만 알려 준다. 돈이 걸린 일괄 작업 전에 써 볼 만하다.
- 동시에 돌릴 수 있는 작업 수에 한도가 있고, 넘으면 429 오류가 난다. 일일 한도, 구독 필요 같은 거절 사유도 문서에 나열돼 있다.

문서의 두 페이지 어디에도 레이어, 글자 처리, 그라데이션 품질 설명은 없었다. 그 부분은 결과 파일을 직접 열어 봐야 안다.

## 값은 이렇게 보도됐다

| 작업 | API 한 장당 |
|---|---|
| 글로 만들기, 품질 낮음 | 0.13달러 |
| 글로 만들기, 품질 중간 | 0.16달러 |
| 글로 만들기, 품질 높음 | 0.20달러 |
| 글로 만들기, 품질 높음 + 참고 이미지 | 0.32달러 |
| 이미지를 벡터로 | 0.10달러 |

※ 출처: [Creators Toolbox: Ideogram Vector](https://creatorstoolbox.com/blog/ideogram-vector-model), [OrcaRouter: Ideogram Vector 1.0, What the SVG File Actually Holds](https://www.orcarouter.ai/blog/ideogram-vector-1-0-svg-file-output). 두 글이 Ideogram의 공개 요금이라며 같은 값을 적었다. 공식 개발자 문서 페이지에서는 값을 확인하지 못했다.

계산해 보면 높음 품질로 열 장을 뽑아도 2달러다. 시안을 여러 안 보여 주는 일이라면 부담이 큰 금액은 아니다. 다만 이건 API 값이고, 앱에서 쓰는 크레딧 값은 알려지지 않았다.

## 디자이너가 먼저 열어 볼 세 가지

**첫째, 레이어가 나뉘어 있나.** 외부 글에 따르면 Ideogram은 글로 만든 SVG의 도형이 따로 움직일 수 있는 단위로 나온다고 설명한다. 반면 이미지를 변환하는 쪽은 도형을 묶어 레이어로 만드는 기능이 "아직 제공되지 않는다"고 한다. 내가 연 변환 문서에는 그 옵션이 보이지 않았다. 사진이나 PNG 로고를 변환하면 한 덩어리로 겹친 선과 면이 나올 수 있다고 보고, 일러스트레이터나 피그마에서 정리할 시간을 따로 잡는 편이 안전하다.

**둘째, 글자가 글자로 남나.** 발표는 "또렷한 글자체"를 내세운다. 그런데 그 글자가 수정할 수 있는 텍스트인지, 윤곽선으로 바뀐 도형인지는 자료에 없다. 로고 안의 이름을 오타 하나 고치려는 상황이라면 이 차이가 크다. 윤곽선이면 글자를 지우고 다시 쳐야 하고, 글꼴도 알 수 없다.

**셋째, 점이 몇 개나 되나.** 그라데이션과 디테일이 많은 SVG는 경로(선분 단위)가 수천 개일 수 있다. 외부 글은 파일이 커질 수 있다고만 짚고 수치는 내지 않았다. 웹에 올리는 아이콘이면 파일 크기와 렌더링 속도를, 인쇄용이면 선 두께와 면 겹침을 확인하는 게 순서다.

일러스트레이터나 피그마에서 편집된다는 말은 보도에 반복해서 나온다. 다만 이것도 Ideogram의 설명이다. 열렸을 때 파일 구성이 쓸 만한지는 별개 문제다.

## 이미 있는 선택지와 나란히 놓으면

벡터를 바로 뽑는 AI는 이번이 처음이 아니다. 검색 결과에는 Recraft가 SVG를 직접 내놓는다는 설명이 있었다. 이번 소식의 새로움은 "벡터를 낸다"보다 "이미지 생성에서 이름난 회사가 벡터 전용 모델을 따로 냈다"에 가깝다. 어느 쪽이 더 낫다고 비교한 자료는 찾지 못했다.

Ideogram 같은 이미지 생성 도구와 AI 로고·브랜드 키트 도구는 [AI 디자인 툴](https://designrefs.com/ai/)의 이미지 생성 항목에 Recraft, Looka 등과 함께 모아 두었다. 이미지 AI의 결과물을 다시 뽑지 않고 고치는 흐름은 [배경만 바꿨는데 로고까지 바뀌었을 때, 크레아 3 편집 모델에서 확인할 것](https://designrefs.com/articles/krea-3-edit-keep-logo/)에서 다뤘다. 그쪽은 래스터 편집, 이쪽은 벡터 출력이라 쓰는 자리가 다르다.

## 지금 알 수 없는 것

- **결과 품질.** 로고, 아이콘, 포스터 중 어느 쪽에 강한지 독립 시험이 없다.
- **앱 요금.** 무료 계정에서 쓸 수 있는지, 크레딧이 몇 개 드는지 확인되지 않았다.
- **상업 이용 조건.** 이 모델 결과물의 저작권과 사용 범위는 이번에 열어 본 자료에 없다. 일반 이미지 모델의 기준은 [AI로 만든 이미지, 클라이언트 작업에 써도 될까](https://designrefs.com/articles/ai-image-commercial-use/)에 정리해 두었다. 이 모델에 그대로 적용된다는 확인은 아니다.
- **편집 기능.** 문서에 만든 SVG를 말로 고치는 엔드포인트는 보이지 않았다. 외부 글도 수정은 디자인 툴에서 하라는 쪽이다.
- **품질 값의 의미.** 낮음·중간·높음이 어떻게 다른지 문서에 설명이 없다.

## 그래서 지금은

**래스터와 벡터를 먼저 구분하자.** 클라이언트가 원본 파일을 달라고 할 때 받는 형식이 무엇인지부터 확인한다. 인쇄, 간판, 굿즈는 벡터가 필요하고 웹 화면용 일러스트는 PNG로 충분한 경우도 많다. 형식이 맞지 않는데 모델부터 바꿔 보는 일을 줄일 수 있다.

**열 장 정도로 파일 속을 열어 보자.** 로고 한 개, 아이콘 한 세트, 글자가 들어간 포스터를 각각 뽑아 일러스트레이터나 피그마에서 열어 본다. 레이어가 나뉘었는지, 글자가 살아 있는지, 점이 얼마나 많은지를 적어 두면 다음에 맡길 일과 맡기지 않을 일이 갈린다. API를 쓴다면 `dry_run`으로 값부터 확인한다.

**납품 전에 사람 손을 한 번 넣는 시간을 잡자.** 변환한 SVG는 도형이 한 덩어리로 겹쳐 있을 수 있다. 색 값과 획 두께를 정리하고 이름을 붙이는 작업을 견적에 넣어 두면 "AI라서 금방 끝나겠죠"라는 말에 답하기 쉽다.

다음에 찾아 줬으면 하는 사이트 종류가 있으면 댓글로 남겨 달라. 들어온 요청은 다음 모음의 첫 소재로 삼는다.

※ 출처: [Ideogram 개발자 문서: Generate SVG](https://developer.ideogram.ai/api-reference/vectors/generate-svg.md), [Ideogram 개발자 문서: Vectorizer](https://developer.ideogram.ai/api-reference/vectors/image-to-svg.md), [Ideogram 발표(X)](https://x.com/ideogram_ai/status/2113300317584720259), [Runtime Wire: Ideogram launches its first vector model](https://runtimewire.com/article/ideogram-vector-1-svg-model-launch), [Creators Toolbox: Ideogram Vector](https://creatorstoolbox.com/blog/ideogram-vector-model), [OrcaRouter: What the SVG File Actually Holds](https://www.orcarouter.ai/blog/ideogram-vector-1-0-svg-file-output), [Future Tools 뉴스](https://futuretools.io/news).
