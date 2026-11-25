---
slug: canva-brush-edit-existing-design
title: A client asks for twelve slide titles cut to one line: Canva's Brush edits what you already made
desc: Canva's Brush, announced October 29–30, is a model for editing existing designs by instruction. It is open to Pro subscribers first. What the reports confirm, what stays unknown because Canva's own page would not open, and what to do before trying it.
tag: AI Design
---

On a twelve-slide deck, cutting every title to one line means making the same fix twelve times. One slide takes no time. By about the seventh, you are flipping back to see how you shortened the earlier ones, and if the colors have to stay as they were last time, you check each slide once more.

Canva's Brush, released at the end of October, targets exactly this kind of work: editing a design that already exists. If Craft, the image model that arrived a week earlier, is the one that draws, Brush is the one that adjusts what has been drawn.

I have not opened Brush myself. Canva's newsroom post (canva.com/newsroom/news/canva-brush/) was blocked (403) when I tried to open it, so I could not read that either. What follows is based on sentences from that post quoted in search results, plus four news and explainer pages that I did open. I do not describe button positions or output quality, because I have seen neither.

## Craft draws, Brush adjusts

Craft, released on October 22, is Canva's first in-house image generation model. It aims at posters, presentations and menus, where text and layout matter. We covered it separately in [our Canva Craft article](https://designrefs.com/articles/canva-craft-text-layout-image-model/).

Brush comes next in the chain. In the wording quoted from Canva, Craft produces the image and Brush refines the design around it. Brush is a vision-language model from Canva Research. In plain terms, it is an AI that looks at the page and understands instructions in words. You use it inside Canva AI.

## What the announcement confirms

Several reports agree on the same points.

- It edits existing designs, from a single line of text to a whole presentation.
- It works in a loop: it writes and runs code to change elements, checks the page visually, then decides the next adjustment.
- The output stays fully editable like any other Canva design, so a person can adjust text, images and layout afterward.
- For now it powers "supported design edits" in Canva AI for Canva Pro subscribers. Wider availability is described only as "coming soon."
- Canva used the line "Great design happens in the edit."

One explainer gave the steps like this.

1. Open an existing design in the Canva editor, or attach or link a design in Canva AI.
2. Choose Brush from the model dropdown.
3. Describe the change you want.

The same piece lists uses such as restyling colors or overall look, updating headings across a multi-page presentation, and adapting slides for Instagram. The starting point is said to be canva.com/ai.

## The two numbers are Canva's own

| Item | What was reported | Compared with |
|---|---|---|
| Speed | Up to 69% faster on general design editing tasks | Canva's previous design agent |
| Cost | 46% cheaper per edit task | Canva's previous design agent |
| Announced | October 29 (two outlets), October 30 (two outlets) | Probably a time-zone difference; not confirmed |
| Availability | Canva Pro subscribers | Wider rollout undated |

※ Sources: [FourWeekMBA](https://fourweekmba.com/ai-canva-builds-its-own-ai-model-says-it-cuts-edit-costs-46/), [Capital Brief](https://www.capitalbrief.com/briefing/canva-launches-ai-design-editing-model-brush-48352e11-c62c-4319-973a-490efa945f92/), [Small Business Trends](https://smallbiztrends.com/canva-unveils-brush-ai-tool-revolutionizes-design-editing-speed-and-quality/), [Unbox Daily](https://unboxdailyhq.com/new-agentic-ai-design-editor-canva-brush-arrives-for-pro-users/) (checked 2026-11-01)

Both figures are maximums, and the baseline is Canva's own earlier agent, not an outside model. FourWeekMBA pointed out that some write-ups recast this as a comparison with frontier models, which Canva's announcement does not say. None of the pages I read described the test conditions, such as how many tasks or what mix. For a designer, 69% does not mean your own work gets 69% faster. It means Canva measured an internal improvement over its earlier setup.

## Where it started

According to the reports, Brush began from an unnamed open-weights model (one whose weights are public). Canva post-trained it on real design and editing tasks and added large-scale reinforcement learning. The inputs reportedly include Canva's design data, its reward setup and professional designers' judgment, and user data is described as anonymized and from people who opted in. Canva has not said which base model it used.

This matters to designers for one reason: it raises the question of whether your own work was used. I confirmed only the "opted-in, anonymized" description. Where that opt-in is switched on or off was not in anything I read.

## Brand Kit support is still in the works

One explainer lists these limits, which I repeat as written.

- **No Brand Kit integration yet.** Brand fonts and colors may not be applied consistently. It is said to be in development.
- **No attachment referencing yet.** You cannot hand it an image and say "like this." Also in development.
- **Image-heavy layouts may come out weaker.** Improvement is planned.
- **Review the output by eye** before using it in important client work.

Things I could not confirm:

- Whether Pro plans have a usage cap or credits for Brush. One explainer says Canva has not clearly stated whether usage is unlimited.
- When Free and team plans get it.
- Whether edits are logged and can be undone step by step.
- How well it follows instructions written in Korean.
- Whether there is an API for calling it outside Canva. Craft has a public API, but none of the pages I read mention one for Brush.

## One instruction, twelve times or once

Back to the twelve slides. Until now this job went one of two ways: open all twelve slides and fix each by hand, or build a good master page (a shared template applied to every slide) and change it once. If the file has no master, the first way is the only way.

Brush seems to fit in the gap: applying the same edit across a whole file that was built without a master. That is my guess from the announcement's description. How far you can trust it on a complicated file needs more results from people who have used it.

Canva's choice is also worth noting. It split the model that produces a new draft from the model that edits one. Our recent piece on [Figma agent credits](https://designrefs.com/articles/figma-agent-ai-credits-ga/) noted that an agent's credit use varies by request. Canva putting a per-edit cost figure up front reads in the same vein. Whether editing is actually cheaper than starting over was not established in the announcement.

## Keep a copy, and spell out what stays

**Duplicate the design before editing.** I could not confirm an undo feature. Use "Make a copy" in Canva and run Brush on the copy. It covers the day a client says "last time was better."

**Write the brand font and color into the instruction.** With no Brand Kit support, say what must stay. The line below is an example I have not tried.

`Keep the title font and color as they are, shorten only the titles on slides 3 to 12 to one line. Do not touch the images.`

Name both what to change and what to leave. Asking for one change at a time also makes the results easier to compare.

**Scan the result slide by slide.** Image-heavy layouts were flagged as weaker, so start with slides that have large photos. Check that text is readable over the picture and that no line overflows. If the file goes to a client, do not skip this step.

※ Sources: [Canva newsroom: Introducing Canva Brush](https://www.canva.com/newsroom/news/canva-brush/) (could not be opened; only sentences quoted in search results used), [FourWeekMBA](https://fourweekmba.com/ai-canva-builds-its-own-ai-model-says-it-cuts-edit-costs-46/), [Capital Brief](https://www.capitalbrief.com/briefing/canva-launches-ai-design-editing-model-brush-48352e11-c62c-4319-973a-490efa945f92/), [Small Business Trends](https://smallbiztrends.com/canva-unveils-brush-ai-tool-revolutionizes-design-editing-speed-and-quality/), [Unbox Daily](https://unboxdailyhq.com/new-agentic-ai-design-editor-canva-brush-arrives-for-pro-users/)
