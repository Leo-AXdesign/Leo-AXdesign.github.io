---
slug: image-ai-edit-not-reroll
title: Edit, don't re-roll. The week image AI turned toward editing
desc: Ideogram 4.5 on September 30, FLUX 3 Image on October 2. This week's two image models led with "change one spot only" rather than prettier pictures. Here's box-first layout and price by size, in diagrams and numbers.
tag: AI Design
---

Anyone who has made drafts with image AI has probably been here. You ask it to change just the headline, and in the image that comes back the model's face is different and the bottle's color has shifted slightly. The more times you edit, the further you drift from the original.

This week's two image models aim right at that problem: Ideogram 4.5 on September 30, and Black Forest Labs' FLUX 3 Image, announced October 2. Both put "change only what you pick and leave the rest alone" ahead of "a more stunning picture".

**First, a disclaimer.** I haven't run either model myself. What follows is based on each company's announcement, articles covering them, and reseller price sheets.

## Re-rolling vs. editing

Until now, "editing" in image AI has been closer to redrawing. The model looks at the original, but rebuilds the whole thing every time. So each edit nudges areas you never touched. The industry calls this drift.

![Editing the same image three times. Older models shift everything each time; this week's models change only the chosen area. A conceptual sketch.](https://designrefs.com/articles/img/image-edit-drift-en.svg)

The promise from both models this week is the bottom row. Change the headline and only the headline changes. Recolor the bottle and only the bottle changes.

## Ideogram 4.5: ten edits without falling apart

Ideogram calls 4.5 "the most precise edit model". The core claim is that it reduces drift, so details hold up whether you edit an image twice, three times or ten times.

The number that stands out is size. The announcement showed a 4016 × 6016 source, about 24.2 megapixels, edited without downscaling. Paste the edited part back into the original, and it holds up in a large print or a close look. Good news for anyone who works in print.

Independent rankings put it mid-table. On Artificial Analysis it ranks 34th of 167 for generation and 23rd for editing. Reseller price sheets list it at 3 cents (low quality) to 22 cents (high quality) per image.

## FLUX 3 Image: place boxes first

FLUX 3 Image goes a step further. It says pixels you didn't edit stay numerically identical. Not "kept similar", but locked exactly.

More interesting is how you create. Instead of describing the scene in words, you can draw a box for each element to set its position and size first.

![Bounding-box layout in FLUX 3 Image. Headline, product, model and sale badge placed as boxes first. An illustrative example; the real format may differ.](https://designrefs.com/articles/img/flux3-bbox-layout-en.svg)

That order is familiar to designers. It's like blocking out a wireframe and then filling it in. Writing "model on the left, product bottom right, big headline on top" and hoping for the best turns into four boxes. Each box can take reference images, up to ten in total.

Output goes up to 4K (5456 × 3072). But the price jumps a lot with size.

![FLUX 3 Image price per image by size. 4K costs six times 2K. Half price until October 8.](https://designrefs.com/articles/img/flux3-price-en.svg)

2K is 10 cents an image; 4K is 61 cents, six times as much. Pick drafts at 1K–2K and re-render only the final one at 4K. Until October 8 it's half price as a launch discount, and an open-weight version you can run yourself is expected in the coming weeks.

## The two side by side

| | Ideogram 4.5 | FLUX 3 Image |
|---|---|---|
| Released | September 30 | Shipped Oct 1, announced Oct 2 |
| Headline claim | Less drift over many edits | Unedited pixels locked exactly |
| Layout | Described in words | Boxes set position and size |
| Reference images | – | Up to 10 |
| Size | Edits a 24.2 MP source without downscaling | Up to 4K (16.8 MP) |
| Price per image | ~3–22 cents | ~4–61 cents (half until Oct 8) |
※ Sources: [Ideogram 4.5 overview (orcarouter)](https://www.orcarouter.ai/blog/ideogram-4-5-launch-precise-edit-model), [the-decoder](https://the-decoder.com/black-forest-labs-launches-flux-3-image-with-multi-step-editing-that-leaves-the-rest-of-your-picture-alone/), [Tech Times](https://www.techtimes.com/articles/328502/20261002/black-forest-labs-launches-flux-3-image-json-bounding-boxes-lock-unchanged-pixels-numerically.htm), [kingy.ai pricing](https://kingy.ai/blog/flux-3-image-specs-benchmarks-comparison/). Prices are reseller rates and vary by provider.

Midjourney shipped a small update the same week too: style previews in the sidebar before you generate, and a fix so edits keep the original aspect ratio. Different scale, same direction. Predict before you generate, and drift less after.

## What changes for designers

Until now, image AI has been close to a slot machine. Pull until you like something, pick one, and start over if it's slightly off. So the output often stayed in mood boards and early exploration.

If only the edited spot changes, that's different. When a client says "just change the headline", you can do it without touching everything they already approved. For the first time, it's shaped to fit into real work, where revision requests go back and forth.

And box layout means composition becomes the person's job again. Where things go and how big is still the designer's call. Layout sense becomes more useful than tricks for writing long prompts.

## So, for now

Before you trust "it doesn't change", here's a way to check. All you need is Photoshop.

1. Stack the original and the result after 3–5 edits as layers in one file.
2. Set the top layer's blend mode to **Difference**.
3. If the screen is nearly black, it really stayed the same. Bright patches in areas you didn't edit show how much drifted.

Do this once before bringing a new model into your work, and you'll know how far you can trust it. Both models can be tried briefly, so test with a revision request you get often.

How to put a mood into words is in [Putting "make it feel right" into words](https://designrefs.com/en/articles/describing-design-style/), and whether you can use AI images for client work is in [Can you use AI-generated images in client work?](https://designrefs.com/en/articles/ai-image-commercial-use/). Image tools are collected under [AI design tools](https://designrefs.com/en/#ai).

※ Sources: [Ideogram 4.5 overview (orcarouter)](https://www.orcarouter.ai/blog/ideogram-4-5-launch-precise-edit-model), [completeaitraining](https://completeaitraining.com/news/ideogram-45-reduces-pixel-drift-in-multi-turn-edits/), [the-decoder](https://the-decoder.com/black-forest-labs-launches-flux-3-image-with-multi-step-editing-that-leaves-the-rest-of-your-picture-alone/), [Tech Times](https://www.techtimes.com/articles/328502/20261002/black-forest-labs-launches-flux-3-image-json-bounding-boxes-lock-unchanged-pixels-numerically.htm), [OpenRouter FLUX.3 Image](https://openrouter.ai/black-forest-labs/flux-3-image), [kingy.ai](https://kingy.ai/blog/flux-3-image-specs-benchmarks-comparison/).
