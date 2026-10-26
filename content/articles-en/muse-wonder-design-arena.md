---
slug: muse-wonder-design-arena
title: Meta's first frontier model tops a design vote. How to read that ranking
desc: Muse Wonder, released by Meta on October 12, now ranks first for websites and UI on Design Arena, where people pick AI designs by eye. How the voting works, and what a No. 1 does and doesn't tell you, with diagrams and numbers.
tag: AI Design
---

On October 12, Meta released Muse Wonder and Muse Wonder Full, its first frontier-class models since it reorganized its AI teams. The announcement was all about memory: a model that keeps track of what matters to you over days and weeks, and sticks with hard tasks until they're done.

There wasn't a word about design. But the model showed up on Design Arena the same day, and two days later it ranks first in both the Website and UI Component arenas.

Design Arena is where people look at designs made by AI and pick the better one, building a ranking from those votes. When a new model is called "No. 1 at design", this is usually where that comes from. So this time I looked first at how that ranking is made, rather than at the model itself.

Two things before the numbers. Scores shift daily as votes come in, so everything below is as of October 14. And Anthropic's models sit on the same leaderboard, while this site is built with Claude Code.

## From one vote to a ranking

Design Arena's About page explains the method in some detail. Someone types a request, like "make a landing page for a cafe", and four randomly chosen models get the same prompt at the same time. The voter sees two results side by side, without knowing which model made which, and picks one.

![Design Arena compares the work of four models on the same prompt five times, with names hidden, to settle 1st through 4th. The winners shown are an example.](https://designrefs.com/articles/img/arena-bracket-en.svg)

There are five picks in all. The first two are within pairs. In the third, the two winners meet; in the fourth, the two losers. The fifth settles the middle two places. After five picks you have a full 1st-to-4th order, and only then are the model names revealed.

These one-of-two choices are combined statistically into a score, using math similar to chess ratings. The page says every vote counts the same, with no filtering or editorial adjustment.

## Unpacking "No. 1"

As of today, Muse Wonder has been in 2,086 tournaments. Here's where it finished.

![Across 2,086 Design Arena tournaments, Muse Wonder finished first 42% of the time, second 25%, third 19% and fourth 14%. Win rates by arena: 3D 69%, UI Component 66%, Game Dev 64%, Website 62%.](https://designrefs.com/articles/img/muse-wonder-arena-en.svg)

It came first a little over four times in ten. In the other six, voters preferred another model's work. A No. 1 model doesn't produce the best result every time. The top of the board is also tightly packed: on another tracker, the top ten models in the Website arena sit within about 50 points of each other.

The second chart has a twist. Its highest win rate is in 3D (69%), yet it ranks only 6th there. Its lowest is Website (62%), where it ranks first. Five models in the 3D arena win more often than it does; in the Website arena, none do yet. A rank depends as much on who else is in the arena as on how good the model is.

The numbers haven't settled, either. In the first two days, its Website score moved between 1355 and 1363, and at one point it was listed second.

## What the vote can't measure

Design Arena calls itself "a subjective framework" for evaluating AI design. Since it says so openly, it's worth reading the results with those limits in mind.

The prompts vary. They aren't set by the company; voters type their own. One person asks for a portfolio site, another for a game screen. There's no screening of who votes or on what device. One review pointed out that the format can reward whatever looks most striking in a few seconds.

Most of what designers weigh in real work sits outside the vote.

| What a vote shows | What a vote doesn't show |
|---|---|
| First impression | Whether it follows your brand rules |
| The result of a single prompt | Whether it holds up over two or three revisions |
| How finished one screen looks | Accessibility, like type size and contrast |
| Relative ranking between models | Whether it hands off to your files and tools |
※ The voting method is from [Design Arena's About page](https://www.designarena.ai/about); the critique is from a [ToolCenter review](https://www.toolcenter.ai/en/articles/design-arena-review-2026).

So the fair reading of this ranking is "the model whose first attempt caught people's eye most often". That's not nothing. First impressions matter, and these are thousands of human choices. It just doesn't mean it's the right model for your work.

## Can designers use it?

For now, the direct routes are on the developer side.

| | Where | Price |
|---|---|---|
| Muse Wonder | Meta Model API, Muse Code | $4 input, $20 output per million tokens |
| Muse Wonder Full | Higher Muse Code subscription plans | No public per-token rate |
| Muse app | Rolling out, subscribers first | Depends on plan |
※ Sources: [Meta](https://about.fb.com/news/2026/10/introducing-muse-wonder-models/), [TechCrunch](https://techcrunch.com/2026/10/12/meta-releases-its-first-frontier-model-muse-wonder/), [The Rundown](https://app.therundown.ai/guides/muse-wonder-guide). Availability varies by region and plan.

The Muse app is closer to designers. On September 29, Meta connected its Muse agent to Canva. It can pull the fonts, colors and brand assets from your Canva account to make flyers, invitations and social images, and the results stay editable in Canva. Meta says nothing publishes or sends without the user's approval. But Muse itself is only available in the US and Canada for now, and Meta hasn't said which model powers the Canva features.

The direction is clear, though. The model that just topped a design vote will soon run inside Muse, and Muse already has a hand in Canva. It's the same current as [Canva, Figma and Adobe moving into ChatGPT](https://designrefs.com/en/articles/openai-devday-2026-designers/): design tools move into chat windows, and the companies behind those chat windows have started selling their models' design sense.

## Turning the leaderboard into your own judgment

**Vote once yourself.** Put in a request like the work you actually get, whether "an order page for a neighborhood bakery" or "an app settings screen". After five picks, when the names appear, you'll see which model your eye leans toward. That tells you more than reading the leaderboard.

**Look at the arena that matches your work.** Besides Website and UI Component, the site ranks Logo, Graphic Design, Slides and SVG separately. First in Website doesn't guarantee anything for logos, as Muse Wonder's 3D rank shows.

**Make the final call with your own rules.** The parts the vote can't measure, you have to test. Give a model one template you use often and one page of brand rules, have it build the same screen, then ask for two or three revisions. It's the same method from the [Sonnet 5.5 article](https://designrefs.com/en/articles/claude-sonnet-5-5-design/). If your rules are already written down, attach your [DESIGN.md](https://designrefs.com/en/articles/design-md-for-ai/) as is.

AI design rankings will keep flipping. This week it's Meta; next month another name may be on top. AI tools by use case are under [AI tools](https://designrefs.com/en/#ai).

※ Sources: [Meta](https://about.fb.com/news/2026/10/introducing-muse-wonder-models/) (Oct 12), [TechCrunch](https://techcrunch.com/2026/10/12/meta-releases-its-first-frontier-model-muse-wonder/), [Design Arena: Muse Wonder](https://www.designarena.ai/models/muse-wonder-1.0) · [About](https://www.designarena.ai/about) (checked Oct 14), [BenchLM Design Arena Website](https://benchlm.ai/benchmarks/designarenawebsite) (Oct 13), [ToolCenter](https://www.toolcenter.ai/en/articles/design-arena-review-2026), [Canva Newsroom](https://www.canva.com/newsroom/news/canva-meta-muse/), [Unite.AI](https://www.unite.ai/meta-adds-small-business-skills-and-app-connectors-to-muse-ai-agent/).
