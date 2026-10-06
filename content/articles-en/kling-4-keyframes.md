---
slug: kling-4-keyframes
title: AI video starts taking a storyboard. Kling 4.0's ten keyframes
desc: Kling 4.0 takes 30 seconds, 10 keyframes and 15 references in one generation. It moves from giving just a first and last frame to laying out the flow of a scene yourself. Here's what changes and what isn't out yet, in a diagram and a table.
tag: AI Design
---

Kling, the AI video model from China's Kuaishou, published its 4.0 specs. The full release is due sometime in October, and a lighter version, 4.0 Flash, opened to some subscribers on September 28.

The numbers stand out: up to 30 seconds per generation, up to 10 keyframes, up to 15 references. But as a designer, what I kept looking at was the keyframes. It means you can hand AI video a storyboard.

**First, a disclaimer.** The full release isn't out yet, and Flash is limited to top-tier yearly subscribers, so I haven't tried it. What follows is based on Kling's published specs and write-ups of them.

## From two frames to ten

Until now, there were two ways to direct AI video: describe it in words, or give a first and last frame. Kling 3.0 also took a first and last frame and let the AI fill in between.

![Kling 3.0 takes a first and last frame; Kling 4.0 takes up to 10 keyframes. A conceptual sketch based on Kling's published specs.](https://designrefs.com/articles/img/kling4-keyframes-en.svg)

Set only the start and end, and the middle is luck. Which way the person walks, when the camera turns, at what second the product enters the frame: the AI decides. Kling 4.0 lets you pin eight more frames in between. Anyone who has worked in video knows this thing. It's a storyboard.

## Twice the length

![Maximum video length per generation. Kling 4.0 doubles 3.0 to 30 seconds.](https://designrefs.com/articles/img/kling4-length-en.svg)

Thirty seconds fits a whole ad spot. Until now you had to make clips of around 15 seconds and stitch them together. At every seam, faces or lighting would shift slightly, a chronic problem with AI video. Generating longer in one go means fewer seams.

## Full release vs. Flash

| | Kling 3.0 | Kling 4.0 Flash | Kling 4.0 |
|---|---|---|---|
| Availability | On sale | Sep 28, Ultra yearly subscribers only | October (date not set) |
| Max length per generation | 15 s | 20 s | 30 s |
| Setting scenes | First and last frame | No multi-frame input | Up to 10 keyframes |
| References | – | – | Up to 15 (10 images, 5 videos) |
| Quality | Up to 4K | 720p | Up to 4K, 10-bit HDR |
※ Sources: [Atlas Cloud spec comparison](https://www.atlascloud.ai/blog/tips/kling-4-flash-vs-full), [Pandaily](https://pandaily.com/kling-ai-kling-4-0-30-second-native-video-multi-reference-control), [Morphic](https://morphic.com/resources/models/kling-4). Credit pricing for 4.0 hasn't been announced. 3.0 runs from 6 credits per second (720p) to 30 (4K).

The middle column is what matters. Flash, which opened first, has no multi-keyframe input. So the most notable feature in this announcement is something nobody can use yet. Until the full release, the spec sheet is all there is to judge by.

## What changes for designers

I've seen the same current all week. Image AI moved toward [placing boxes first and editing only the chosen spot](https://designrefs.com/en/articles/image-ai-edit-not-reroll/), and 3D AI toward [picking and fixing only the problem area](https://designrefs.com/en/articles/instructmesh-ai-3d-print/). Kling 4.0's keyframes are the same story: turning what was left to luck into something a person decides.

That shifts where the work sits. Knowing how to split a scene into frames, and what must be visible at which second, becomes more useful than writing long, elaborate prompts. It's a change that favors motion designers and ad producers who have drawn storyboards.

One more thing. Ten keyframes are, in the end, ten images. They might come from image AI or be drawn by a designer. For the video to look natural, the same person, product and lighting have to hold across all ten. That's where "edits that don't drift" on the image side meet keyframes on the video side.

## So, for now

There's some preparation worth doing before the full release.

1. **Start with a 15-second storyboard.** With the video AI you use now, give only a first and last frame and generate 15 seconds. Mark the moments in the middle that go off course. Those are where you'll pin keyframes in 4.0.
2. **Make keyframe images as one set.** Make ten separately and the person and lighting change from frame to frame. It's safer to keep one image as the original and derive the rest with [image edits that change only the chosen spot](https://designrefs.com/en/articles/image-ai-edit-not-reroll/).
3. **Judge price on the full release.** 4.0 pricing isn't out yet. Thirty seconds at 4K uses a lot of credits even on 3.0, so get in the habit of reviewing drafts short and low-res, and rendering only the final long and large.

AI tools for video and motion are collected under [AI design tools](https://designrefs.com/en/#ai).

※ Sources: [Atlas Cloud](https://www.atlascloud.ai/blog/tips/kling-4-flash-vs-full), [Pandaily](https://pandaily.com/kling-ai-kling-4-0-30-second-native-video-multi-reference-control), [Morphic](https://morphic.com/resources/models/kling-4), [sloptv](https://sloptv.co/news/kling-4-0-october-promise-flash-720p-only), [Atlas Cloud pricing](https://www.atlascloud.ai/blog/tips/kling-ai-pricing).
