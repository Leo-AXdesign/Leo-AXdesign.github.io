---
slug: canva-craft-text-layout-image-model
title: Canva Craft plans the layout first, so poster text stops breaking
desc: On October 22 Canva released Craft, its first in-house image model, aimed at designs where layout and text matter. What press coverage says about its two-stage setup, the ranking claims, where you can use it, and what is still unknown, including price and commercial terms.
tag: AI Design
---

The client's email is one line. "Can you send three poster options today? Make the date and venue big."

You run the prompt through an image AI and the picture looks right. But the date reads "Oct 2th" instead of "Oct 27". You regenerate. This time the text is correct, but the title has slid into a corner. For three drafts, the number of generations keeps climbing. (This is an imagined scene.)

On October 22, Canva released Canva Craft, its first image generation model built in-house. It is aimed at posters, social posts and presentations, where text and layout matter more than photographic realism. This is not a hands-on review. It is a read of what press coverage reports, from a designer's point of view.

I haven't run the model myself; this is based on reporting from TechCrunch, Digital Trends and others. The rankings and performance figures are Canva's own, and I found nothing that verified them independently. API pricing and credit costs weren't in the coverage either.

## Plan first, then draw

TechCrunch and Digital Trends both describe two stages.

| Stage | What it does |
|---|---|
| 1: Plan | Reads the prompt and decides which elements go in, where they sit relative to each other, their relative sizes, the visual hierarchy, and the text to include |
| 2: Render | Takes that plan and produces the image, up to 2K resolution, in about 30 aspect ratios matched to platform use |

※ Sources: [TechCrunch (2026-10-22)](https://techcrunch.com/2026/10/22/canva-releases-its-first-image-generation-model/), [Digital Trends](https://www.digitaltrends.com/computing/canva-craft-ai-image-generation-model-launch/). The table condenses the two articles' descriptions.

It resembles how a designer builds a draft: decide where the title goes and how large the date is, then add color and imagery. The claim is that this order is built into the model. I could not confirm that it actually reduces text errors. A description is not a result.

## Trained on templates, not photos

According to the coverage, Craft was trained on human-made templates from Canva's library rather than on photographs: posters, social posts, presentations, infographics, menus and type-heavy layouts. The Letter Two says text generation supports 55 languages. No source I opened says whether Korean is among them or how accurate the glyphs are.

Two questions remain. One is quality for non-Latin scripts. The other is compensation for template creators. The Letter Two notes that neither creator compensation nor protection for customers' commercial use is stated. If you plan to use output in client work, treat both as open until terms appear. Our general guide to commercial use of AI images is [Can you use AI images in client work](https://designrefs.com/articles/ai-image-commercial-use/); it does not confirm that those rules apply to Craft.

## The ranking, as announced

The Letter Two relays Canva's announcement as follows.

| Category | Rank Canva reports |
|---|---|
| Overall | 4th at launch (behind GPT-Image-2.5 Sunburst, GPT-Image-2.5 Flare and GPT Image 2) |
| People and portraits | 1st (ahead of 86 models) |
| Abstract and patterns | 2nd |
| Products | 4th |

※ Source: [The Letter Two (2026-10-23)](https://thelettertwo.com/2026/10/23/canva-craft-ai-image-model). Figures cited by Canva from the DesignArena leaderboard; not independently verified in the article.

Digital Trends reports that Canva describes its research team as the world's second most advanced lab for image generation. That is a different claim from the model's 4th place, so merging them into "a #2 model" would be wrong. The leaderboard is also built on human votes, and how well those votes reflect poster-making convenience is a separate matter. We covered how to read such rankings in [Meta's first top model is #1 in design voting](https://designrefs.com/articles/muse-wonder-design-arena/).

## Where you can use it

What the reports agree on, and where they split.

- **Agree:** All Canva users can use it in the Dream Lab tab. It is also offered through the Canva API. Digital Trends mentions account and usage limits.
- **Agree:** Cheaper versions, Craftfast and Craft-ultrafast, are coming. No dates are given.
- **Split:** Using Craft from ChatGPT or Gemini through Canva's MCP (a connection that lets an AI assistant call Canva) is described as planned by TechCrunch and Digital Trends, and as "expected to launch soon" by The Letter Two. None of the sources I opened said it is usable today.
- **Single mention:** TechCrunch says generated images can be turned into layered designs through Canva Magic, and Digital Trends calls this Magic Layers technology. I did not find it in The Letter Two. How the layers are split, and whether text stays editable, is not confirmed.

That last item is the same question we raised for [Ideogram Vector 1.0](https://designrefs.com/articles/ideogram-vector-1-editable-svg/). Whether an image AI hands you one picture or a file you can edit is what matters most in real work.

## What to test first

**One text-heavy poster.** Run a poster with a date, venue, price and phone number through the same prompt ten times. Count how many come out with no text errors. Run the same prompt through the model you use now. Without that comparison, "handles text well" is just a feeling.

**Korean headlines.** It is unknown whether Korean is among the 55 languages, so test a Korean headline and small Korean body text separately. Characters with final consonants and small sizes break first.

**Change one thing.** Ask for a single-element edit, such as "keep the logo, change only the background color." Many models advertise editing, so it is worth checking whether the rest really stays put. It is the same test we used for [Krea 3's edit model](https://designrefs.com/articles/krea-3-edit-keep-logo/).

**Open the converted file.** If you can use the layer conversion, open the result and check whether the text is a text box. That one check decides how long delivery takes.

## What we don't know yet

- **Price.** API rates, app credit use and free limits have no confirmed source.
- **Independent tests.** Apart from the rankings Canva cites, I found no third-party comparison.
- **Commercial terms.** Compensation for the template creators whose work trained it, and protection for generated output, are not stated.
- **Korean quality.** Whether Korean is a supported language is unconfirmed.
- **Layer conversion in practice.** How well it separates layers, and whether text stays editable, is unknown until someone opens a file.
- **Specifications.** Model size and technical documentation were reported as not published.

## So for now

**Count ten generations.** Run one text-heavy poster ten times with the same prompt and record how many have no text errors. Put it next to your current tool under identical conditions, or there is no reason to switch.

**Read the terms before client work.** Until conditions on commercial use and template training appear, keep practice drafts and deliverables separate. Don't make promises that rest on something unconfirmed.

**Fix the layout in words first.** Whether or not a model plans first, writing position and size order into the prompt, such as "title in the top third, date largest under it, venue at the bottom," may help cut the number of regenerations. That is a method worth trying, not a result I compared.

If there is a type of site you'd like us to find next, leave a comment. Requests become the first topic for the next collection.

※ Sources: [TechCrunch: Canva releases its first image generation model](https://techcrunch.com/2026/10/22/canva-releases-its-first-image-generation-model/), [Digital Trends: Canva enters the AI image generation race with Craft](https://www.digitaltrends.com/computing/canva-craft-ai-image-generation-model-launch/), [The Letter Two: Canva Craft Is Canva Research's First Image Model](https://thelettertwo.com/2026/10/23/canva-craft-ai-image-model), [Future Tools news](https://futuretools.io/news).
