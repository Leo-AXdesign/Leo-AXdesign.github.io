---
slug: image-ai-edit-not-reroll
title: 다시 뽑지 말고 고쳐 쓴다, 이미지 AI가 '편집' 쪽으로 간 한 주
desc: 9월 30일 Ideogram 4.5, 10월 2일 FLUX 3 Image. 이번 주 나온 두 이미지 모델은 더 예쁜 그림보다 '한 군데만 고치기'를 앞세웠다. 상자로 먼저 배치하는 방식과 크기별 가격까지 그림과 숫자로 정리했다.
date: 2026-10-03
order: 1
tag: AI 디자인
related: ai, tools
---

이미지 AI로 시안을 만들어 본 사람이라면 한 번쯤 겪었을 일이 있다. 제목 글자 하나만 바꿔 달라고 했는데, 돌아온 그림에서 모델 얼굴이 달라져 있고 병 색이 미묘하게 틀어져 있다. 두 번, 세 번 고칠수록 처음 그림에서 점점 멀어진다.

이번 주 나온 두 이미지 모델은 바로 이 지점을 겨냥했다. 9월 30일 Ideogram 4.5, 그리고 10월 2일 발표된 Black Forest Labs의 FLUX 3 Image. 둘 다 "더 멋진 그림"보다 "고른 곳만 고치고 나머지는 그대로"를 앞에 내세웠다.

**먼저 밝혀 둘 것.** 두 모델 모두 직접 돌려 보지 못했다. 아래 내용은 각 회사 발표와 이를 다룬 기사, 재판매처 가격표를 바탕으로 했다.

## 다시 뽑기와 고쳐 쓰기

지금까지 이미지 AI의 '수정'은 사실 다시 그리기에 가까웠다. 원래 그림을 참고는 하지만, 매번 전체를 새로 만든다. 그래서 고칠 때마다 손대지 않은 자리까지 조금씩 흔들린다. 업계에서는 이걸 '드리프트(drift)'라고 부른다.

![같은 그림을 세 번 고칠 때. 예전 방식은 매번 전체가 흔들리고, 이번 주 모델들은 고른 자리만 바뀐다. 개념을 그린 그림이다.](https://designrefs.com/articles/img/image-edit-drift.svg)

이번 주 두 모델이 내건 약속은 아래 줄이다. 제목을 고치면 제목만, 병 색을 바꾸면 병만 바뀐다.

## Ideogram 4.5: 열 번 고쳐도 무너지지 않게

Ideogram은 4.5를 "가장 정밀한 편집 모델"이라고 소개했다. 핵심 주장은 하나다. 같은 그림을 두 번, 세 번, 열 번 고쳐도 디테일이 유지되도록 드리프트를 줄였다는 것.

눈에 띄는 숫자는 크기다. 발표에서 4016 × 6016 픽셀, 약 2420만 화소짜리 원본을 줄이지 않고 그대로 고치는 장면을 보여 줬다. 고친 부분을 원본에 다시 붙여도 크게 뽑거나 가까이 들여다볼 때 티가 나지 않는다는 얘기다. 인쇄물을 다루는 사람에게는 반가운 대목이다.

외부 평가에서는 중간 정도다. Artificial Analysis 순위로 그림 만들기는 167개 중 34위, 편집은 23위였다. 값은 재판매처 가격표 기준으로 한 장에 3센트(낮은 품질)부터 22센트(높은 품질)까지다.

## FLUX 3 Image: 상자로 먼저 자리를 잡는다

FLUX 3 Image는 한 걸음 더 갔다. 고칠 때 바꾸지 않은 픽셀은 숫자 하나까지 그대로 둔다고 했다. '비슷하게 유지'가 아니라 '똑같이 고정'이다.

더 흥미로운 건 만드는 방식이다. 글로 장면을 설명하는 대신, 요소마다 상자를 그려 자리와 크기를 먼저 정할 수 있다.

![FLUX 3 Image의 상자 배치. 제목, 제품, 모델, 할인 딱지를 상자로 먼저 놓는다. 발표를 바탕으로 그린 예이고 실제 형식과는 다를 수 있다.](https://designrefs.com/articles/img/flux3-bbox-layout.svg)

디자이너에게는 익숙한 순서다. 와이어프레임을 먼저 잡고 그 안을 채우는 것과 같다. "왼쪽에 모델, 오른쪽 아래에 제품, 위에 큰 제목"을 글로 길게 설명하고 운에 맡기던 일이, 상자 네 개로 바뀐다. 상자마다 참고 이미지를 붙일 수 있고, 한 번에 최대 10장까지 쓴다.

출력은 최대 4K(5456 × 3072)다. 다만 크기에 따라 값이 크게 뛴다.

![FLUX 3 Image의 크기별 한 장 값. 4K는 2K의 6배다. 10월 8일까지는 절반 값.](https://designrefs.com/articles/img/flux3-price.svg)

2K는 장당 10센트인데 4K는 61센트, 6배다. 시안은 1K~2K로 뽑아서 고르고, 최종 하나만 4K로 다시 뽑는 편이 맞다. 10월 8일까지는 발표 할인으로 절반 값이고, 내려받아 직접 돌릴 수 있는 오픈 가중치 판도 몇 주 안에 낸다고 했다.

## 두 모델을 나란히

| | Ideogram 4.5 | FLUX 3 Image |
|---|---|---|
| 나온 날 | 9월 30일 | 10월 1일 출시, 2일 발표 |
| 내세운 것 | 여러 번 고쳐도 덜 흔들림 | 안 고친 픽셀은 그대로 고정 |
| 배치 | 글로 설명 | 상자로 자리·크기 지정 |
| 참고 이미지 | – | 최대 10장 |
| 크기 | 2420만 화소 원본을 줄이지 않고 편집 | 최대 4K (1680만 화소) |
| 한 장 값 | 약 3~22센트 | 약 4~61센트 (8일까지 절반) |
※ 출처: [Ideogram 4.5 정리(orcarouter)](https://www.orcarouter.ai/blog/ideogram-4-5-launch-precise-edit-model), [the-decoder](https://the-decoder.com/black-forest-labs-launches-flux-3-image-with-multi-step-editing-that-leaves-the-rest-of-your-picture-alone/), [Tech Times](https://www.techtimes.com/articles/328502/20261002/black-forest-labs-launches-flux-3-image-json-bounding-boxes-lock-unchanged-pixels-numerically.htm), [kingy.ai 가격 정리](https://kingy.ai/blog/flux-3-image-specs-benchmarks-comparison/). 가격은 재판매처 기준이라 쓰는 곳마다 다를 수 있다.

같은 주에 Midjourney도 작은 갱신을 냈다. 만들기 전에 옆 막대에서 스타일을 미리 보는 기능, 그리고 고친 그림이 원래 비율을 지키도록 한 수정이 들어갔다. 크기는 달라도 방향은 같다. 뽑기 전에 예상하고, 뽑은 뒤엔 덜 흔들리게.

## 디자이너에게 달라지는 것

지금까지 이미지 AI는 '뽑기'에 가까웠다. 마음에 드는 게 나올 때까지 여러 장을 뽑고, 고르고, 조금 다르면 처음부터 다시. 그래서 결과물이 무드보드나 초기 탐색 단계에 머무는 경우가 많았다.

고친 자리만 바뀐다면 이야기가 달라진다. 클라이언트가 "제목만 바꿔 주세요"라고 할 때, 승인받은 나머지를 건드리지 않고 고칠 수 있다. 수정 요청이 오가는 실제 작업 흐름에 처음으로 들어올 수 있는 모양이 된 셈이다.

그리고 상자 배치는 구도를 잡는 일이 다시 사람 쪽 일이 된다는 뜻이기도 하다. 어디에 무엇을 얼마나 크게 둘지는 여전히 디자이너가 정한다. 프롬프트를 길게 쓰는 요령보다 레이아웃 감각이 더 쓸모 있어지는 쪽이다.

## 그래서 지금은

'안 바뀐다'는 말을 믿기 전에 확인하는 방법이 있다. 포토샵만 있으면 된다.

1. 원본과 3~5번 고친 결과를 한 파일에 레이어로 겹친다.
2. 위 레이어의 혼합 모드를 **차이(Difference)**로 바꾼다.
3. 화면이 거의 까맣다면 정말 그대로인 것이다. 고치지 않은 자리에 밝은 얼룩이 보이면 그만큼 흔들린 것이다.

새 모델을 작업에 들이기 전에 한 번만 해 보면, 어디까지 믿고 맡겨도 될지 감이 온다. 두 모델 모두 짧게라도 써 볼 수 있으니, 평소 자주 받는 수정 요청 하나로 시험해 보자.

원하는 분위기를 말로 전하는 법은 ['느낌 있게'를 말로 옮기는 일](https://designrefs.com/articles/describing-design-style/)에, 만든 이미지를 일에 써도 되는지는 [AI로 만든 이미지, 클라이언트 작업에 써도 될까](https://designrefs.com/articles/ai-image-commercial-use/)에 정리해 두었다. 이미지 도구들은 [AI 디자인 툴](https://designrefs.com/ai/)에 모여 있다.

※ 출처: [Ideogram 4.5 정리(orcarouter)](https://www.orcarouter.ai/blog/ideogram-4-5-launch-precise-edit-model), [completeaitraining](https://completeaitraining.com/news/ideogram-45-reduces-pixel-drift-in-multi-turn-edits/), [the-decoder](https://the-decoder.com/black-forest-labs-launches-flux-3-image-with-multi-step-editing-that-leaves-the-rest-of-your-picture-alone/), [Tech Times](https://www.techtimes.com/articles/328502/20261002/black-forest-labs-launches-flux-3-image-json-bounding-boxes-lock-unchanged-pixels-numerically.htm), [OpenRouter FLUX.3 Image](https://openrouter.ai/black-forest-labs/flux-3-image), [kingy.ai](https://kingy.ai/blog/flux-3-image-specs-benchmarks-comparison/).
