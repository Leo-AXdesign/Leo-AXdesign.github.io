---
slug: krea-3-edit-keep-logo
title: Will Krea 3 keep your logo intact? About $0.06 per 2K edit
desc: Krea released its image editing model Krea 3 on October 15. It promises to keep a product's label and logo while changing the scene around it. Checked against Krea's blog and pricing page: speed, cost, how to prompt it, and what is still unverified.
tag: AI Design
---

Sometimes a product photo needs nothing more than a warm wooden shelf behind it. But when you hand it to an image AI, it is common to get a nice background with the bottle's label text gone soft and the logo shape shifted. Fixing that can take longer than reshooting.

On October 15, the image AI company Krea released Krea 3. It is an editing model: it changes an image you already have instead of generating one from scratch. The first promise in its launch post is that whatever you don't ask it to change stays as it was. This piece repeats only what I verified on Krea's blog and pricing page.

![Krea blog 'Introducing Krea 3'. Source: krea.ai/blog/introducing-krea-3 (captured 2026-10-21)](https://designrefs.com/articles/img/krea-blog-v2.webp)

Speed, price and quality are all Krea's own numbers. It compared against Nano Banana Pro and GPT Image 2, and I found no third-party reproduction under the same conditions. How it holds up on text-heavy packaging or complex logos has no examples yet. Plan limits are inconsistent on the pricing page, so I cover them separately later.

## What the launch post promises

The post describes the editing behavior like this:

- It preserves what you don't ask it to change. Products keep their labels and logos while the scene around them changes.
- In one example, the sofa, chairs and table were replaced while the rug, the view and the woman reading stayed the same.
- People and characters stay consistent across images.
- Each edit accepts up to 6 reference images.
- It works on paintings, vector art and ink drawings.
- It can turn sketches, moodboards and line drawings with color palettes into finished images.

The sofa before/after images belong to Krea, so they are not reproduced here. You can see them in the original launch post.

It is closer to fixing one spot than to rolling the dice again. We covered this direction in [Fix it, don't reroll: image AI moves toward editing](https://designrefs.com/articles/image-ai-edit-not-reroll/).

## Speed and price: the numbers Krea published

- Most edits finish end to end in under 8 seconds at native 2K.
- The fastest setup takes about 4 to 5 seconds. Krea says it is not real-time yet.
- Price: $0.06 per 2K image, $0.03 per 1K image.
- Comparison basis: median time for edit jobs on Krea from September 24 to October 1, 2026, queue time included. Nano Banana Pro took 33 seconds and GPT Image 2 took 90 seconds.
- At 100,000 edits a month (no reference images, list price): Krea 3 costs $6,000, Nano Banana Pro $13,500 and GPT Image 2 $22,000.

![Krea 3 edit cost and speed compared](https://designrefs.com/articles/img/krea-3-cost-speed-en.svg)

| Model | Cost for 100,000 edits (list) | Median time per edit |
|---|---|---|
| Krea 3 | $6,000 | Most under 8 s |
| Nano Banana Pro | $13,500 | 33 s |
| GPT Image 2 | $22,000 | 90 s |

※ Source: [Krea blog: Introducing Krea 3](https://www.krea.ai/blog/introducing-krea-3). Times were measured by Krea from September 24 to October 1. For Krea 3, "under 8 seconds" is an upper bound for most edits as stated in the post, not a median.

Dividing by 100,000 gives $0.135 per image for Nano Banana Pro and $0.22 for GPT Image 2, the same per-image figures the post lists. For one designer editing a single picture the gap hardly matters. For a few hundred product shots it does.

A caution: the timing comparison was measured on Krea's own service, while the other models run elsewhere. With a different queue the results would differ. Treat the numbers as a direction, not a verdict.

## Krea's prompting advice

The launch post lists four habits:

1. Start by stating what should stay the same.
2. Describe the change the way a photographer would: scene, light, camera.
3. With several images, say what each one is for.
4. Use "only" when you want a single change.

Applied to the product photo above, a prompt might read as follows. This is my paraphrase of Krea's advice, and I haven't run it.

> Keep the bottle's label and logo as they are. Change only the background to a wooden shelf in morning light. Keep the camera angle.

Putting what to protect before what to change stands out. Presumably the model reads from the sentence where it is allowed to touch. That is my guess.

## Where you can use it

According to the post, Krea 3 is live on krea.ai (Krea says it has 30 million users) and in the Krea API. It is also available through fal, Hedra, Together AI, Nous Research, OpenRouter and Replicate. Enterprise teams can contact Krea.

![Krea home page. Source: krea.ai (captured 2026-10-21)](https://designrefs.com/articles/img/krea-home.webp)

Plans on Krea's pricing page. The monthly prices look like annual-billing rates; the page also shows struck-through prices (Basic $9, Pro $35, Max $105, Business $200) that are probably the month-to-month prices, though the page doesn't label them.

![Plans on Krea's pricing page, yearly-billing prices; prices may change. Source: krea.ai/pricing (captured 2026-10-21)](https://designrefs.com/articles/img/krea-pricing.webp)

| Plan | Monthly price (appears to be annual billing) | Allowance |
|---|---|---|
| Free | $0 | 100 units per day |
| Basic | $5 | 5,000 units per month |
| Pro | $21 | 20,000 units per month |
| Max | $63 | 60,000 units per month |
| Business | $160 | 80,000 units per month (up to 50 seats) |

※ Source: [Krea pricing](https://www.krea.ai/pricing). The page's structured data lists Max as $70 and 40,000 units, which differs from the visible text. Check the current page before you pay.

How many Krea 3 images the free plan allows was unclear. The comparison table seems to show about 5 images a day (marked as approximate) in the Krea 3 row, while a separate editing-allowance table shows other numbers. I couldn't tell which applies. Try a few free runs before deciding.

## What is still missing

- **How well it preserves originals.** The post says "stays as it was," but nobody published numbers for tiny label text or intricate patterns.
- **Choosing the area.** The post's roadmap lists instructions by circling an area or writing on the image. Krea says it is building that. For now you describe the location in words.
- **Resolution.** Higher resolution at lower compute cost is also on the roadmap. The default today is 2K.
- **Copyright and commercial use.** This piece doesn't cover whether you may use the output for paid work. See [Can you use AI images in client work?](https://designrefs.com/articles/ai-image-commercial-use/) for the general principles, and read the service terms separately.
- **Independent verification.** Among the sources I opened, none compared Krea 3 with other models under the same conditions.

## What this means for designers

Editing models are useful when what must not change is clear: product photos, packaging mockups, ad drafts. They matter less for brainstorming many new images.

One worry is speed. Eight seconds makes it easy to run many times, and that raises the odds of missing a result that is plausible but wrong. Overlay the output on the original and check logos and lettering every time. That is my opinion.

For vibe coders it is an easy way to adjust product images and hero backgrounds for a landing page. But the problem of AI screens all looking alike isn't solved by images. Choosing fonts and colors comes first.

## So for now

**Write what to keep first, in one line.** Put "keep the label and logo as they are" at the front, then name a single change with "only." It is the order Krea recommends, and worth trying on any editing model.

**Test with one of your own photos inside the free limit.** Skip the launch examples. Use the photo with the smallest label text, run it once, and overlay it on the original. Zoom in on the letter edges and you'll know quickly.

**Read the terms before client work.** Good speed and price don't settle usage rights. Note what you confirmed next to the project file.

Tools for each use, including image generation and editing, are collected in [AI design tools](https://designrefs.com/ai/). Krea is in the image generation list.

## The maker's numbers, your files

Krea 3 is an editing model that promises to leave untouched what you don't ask it to change, and Krea says it finishes most edits in under 8 seconds at $0.06 per 2K image. These figures come from the maker, so how it performs on your own files is something you have to run to find out.

※ Sources: [Krea blog: Introducing Krea 3](https://www.krea.ai/blog/introducing-krea-3), [Krea blog index](https://www.krea.ai/blog), [Krea pricing](https://www.krea.ai/pricing).
