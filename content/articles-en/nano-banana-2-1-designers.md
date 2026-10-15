---
slug: nano-banana-2-1-designers
title: Nano Banana 2.1 is "half price". What designers should check
desc: Google's image model Nano Banana 2.1 is out. 1K and 2K images cost half as much, but 4K doesn't, and text got better while the model card lists weak spots. Checked against Google's pricing page and model card, with charts and numbers.
tag: AI Design
---

Google's image model Nano Banana has become a familiar name in Korea too. On October 6 it moved up to version 2.1.

Most launch headlines said the same thing: "4K at half price." But when I opened Google's pricing page today, only 1K and 2K were half price. 4K came down by a quarter. And the "old model shuts down October 29" line in several articles doesn't appear anywhere in Google's own docs.

So this piece follows the documents rather than the buzz. I went through Google's pricing page, model card and deprecation table one by one and kept only what designers need.

**First, a disclaimer.** I'm building this site with Claude Code. Every performance number below was measured by Google itself, and no one has published tests of Korean text yet.

## What changed

Nano Banana 2.1 is an image generation and editing model built on Gemini 3.6 Flash. It's rolling out to the Gemini app, AI Mode in Search, AI Studio, the video tool Flow, the UI design tool Stitch and Google Ads.

Google highlighted three things: visual design, editing a region you describe in words, and consistency, so the same people and objects hold across several images. You can give it up to 14 reference images, and it tracks up to four characters and ten objects among them. Aspect ratios now stretch to long strips like 8:1, which is handy for web banners and wide signage drafts.

The smallest size, 0.5K, is gone. You now choose 1K, 2K or 4K.

## Price: half at 1K and 2K, less off at 4K

![Price per image. 1K went from $0.067 to $0.034 and 2K from $0.101 to $0.050, both half. 4K went from $0.151 to $0.113, a 25% cut.](https://designrefs.com/articles/img/nano-banana-21-price-en.svg)

The 4K price that spread at launch was $0.0756. The pricing page now says $0.113, because a 4K image uses more tokens than it did with the previous model. If you plan to generate a lot at 4K, redo the budget.

The number to notice is 2K. A 2K image on the new model ($0.050) costs less than a 1K image on the old one ($0.067). The model card explains why that matters.

## Google's numbers, and the weak spots it admits

The model card reports scores from people comparing results and picking the better one. Higher means it was picked more often.

| Evaluation | Nano Banana 2.1 | Nano Banana 2 | Nano Banana Pro |
|---|---|---|---|
| Overall preference | **1050** | 990 | 935 |
| Infographic design | **1048** | 961 | 912 |
| Infographic factuality | **0.521** | 0.179 | 0.265 |
| General editing | **1026** | 938 | 939 |
| Multi-character consistency | **1106** | 978 | 1011 |
※ Source: [Nano Banana 2.1 model card](https://deepmind.google/models/model-cards/nano-banana-2-1/) (October 2026). All evaluations are Google's own.

The biggest jump is infographic factuality, from 0.179 to 0.521. It gets numbers and names in charts wrong much less often. It's still far from perfect, though, so always double-check any image with figures in it.

The same model card lists weak spots. At 1K, small text often comes out blurry, and long paragraphs or page-length text are still hard. It sometimes confuses positions like left and right. It says text works "across several languages" but doesn't mention Korean.

Which brings us back to 2K. For posters or product detail images with text, generate at 2K instead of 1K. It costs less than the old model's 1K and avoids blurry small text.

## Editing in words: how to ask

Choosing what to change by describing it, instead of painting a mask, is the area that improved most. Put it next to the left/right weakness, though, and how you ask starts to matter.

![When asking Nano Banana 2.1 for a partial edit, name the object (the word SALE, the person in the hat) rather than a position (top left, on the right). Prompts are examples.](https://designrefs.com/articles/img/mask-by-words-en.svg)

"The word 'SALE'" rather than "the text at top left"; "the person in the hat" rather than "the person on the right". If only one thing on screen fits the description, the model is less likely to touch the wrong spot. I covered this shift from rerolling to fixing one spot in [last week's image AI piece](https://designrefs.com/en/articles/image-ai-edit-not-reroll/).

## Every image carries a mark

Images made with Nano Banana carry SynthID, an invisible watermark. According to reports, 2.1 also attaches Content Credentials (C2PA), which record what tool made the image. Google has a short video on how to check.

![How to tell whether an image was made with AI, from Google's official YouTube channel.](https://www.youtube.com/watch?v=Sm7OTow3mcY)

This matters for client work. If you deliver images made with Nano Banana, the client can later confirm they were AI-generated. Assume it can't be hidden and say up front where you used AI. Whether you can use the images commercially is covered in [my piece on AI image commercial use](https://designrefs.com/en/articles/ai-image-commercial-use/).

## What to try this week

**Generate one Korean-language poster at 2K.** Use real copy, with a title, subtitle and small print. No one has shown with numbers how well it handles Korean yet, so your own copy is the fastest test.

**If you use it through the API or automations, check the model name.** Google recommends 2.1 as the replacement for the previous model (Nano Banana 2), but hasn't set a shutdown date. If you've seen "shuts down October 29", check Google's [deprecation table](https://ai.google.dev/gemini-api/docs/deprecations) yourself. Neither model has a free API tier.

**Use 4K only when you need it.** Unless it's a large print image, pick drafts at 2K and render only the final one at 4K.

AI image tools by use case are under [AI tools](https://designrefs.com/en/#ai).

※ Sources: [Nano Banana 2.1 model card](https://deepmind.google/models/model-cards/nano-banana-2-1/), [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) · [deprecations](https://ai.google.dev/gemini-api/docs/deprecations) (checked Oct 15), [Neowin](https://www.neowin.net/news/google-launches-nano-banana-21-with-better-editing-and-subject-consistency/), [Android Headlines](https://www.androidheadlines.com/2026/10/google-launches-nano-banana-2-1-ai-images-price.html), [Apidog](https://apidog.com/blog/nano-banana-2-1/), [Google on YouTube](https://www.youtube.com/watch?v=Sm7OTow3mcY).
