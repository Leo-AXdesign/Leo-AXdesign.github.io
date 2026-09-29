---
slug: claude-fable-5-1-vs-gpt-6-astra
title: Claude Fable 5.1 vs GPT-6 Astra, by the numbers
desc: Two frontier models released two days apart. Official specs, third-party evaluations and early reactions from designers, side by side with sources.
tag: AI Design
---

In the first week of September, two frontier AI models came out two days apart: Anthropic's Claude Fable 5.1 on September 1–2, and OpenAI's GPT-6 Astra on September 3. Both were announced as the smartest yet, and, as it happens, their price sheets are identical.

Asked which is better, it's hard to answer in one line. Lay out the official specs, the independent evaluations and the reactions of people who tried them first, one after another, and you'll see why.

**First, a disclaimer.** Many of the benchmarks were measured by the companies that made the models. Each table notes who measured what. Also, I'm building this site with Claude Code, so I only used numbers that have a source. All figures are as of mid-September 2026 and are changing fast.

## Specs: same price, different cache

| | Claude Fable 5.1 | GPT-6 Astra |
|---|---|---|
| Released | Sep 1–2, 2026 | Sep 3, 2026 |
| Input price (per 1M tokens) | $10 | $10 |
| Output price (per 1M tokens) | $50 | $50 |
| Cache reads (per 1M tokens) | **$0.25** | $1 |
| Context window | 1M tokens | **1.05M tokens** |
| Max output | 128K tokens | 128K tokens |
| Knowledge cutoff | **June 2026** | April 2026 |
※ Sources: [Anthropic model docs](https://platform.claude.com/docs/en/about-claude/models/overview), [OpenAI model docs](https://developers.openai.com/api/docs/models/gpt-6-astra). Bold marks the advantage.

On the table alone, they're practically twins. The differences are in two places.

For work where the model rereads the same long material, the picture changes. The cache price, what you pay to reload content it has already read, is a quarter as much for Fable 5.1 as for Astra. Attaching a brand guideline PDF and asking dozens of questions about it is exactly this kind of work. And Fable 5.1 knows about the world two months later.

There are no official numbers to compare speed. Anthropic classifies Fable 5.1 as "slower" among its own models.

## Same overall score, more than double the cost

On the overall index from independent evaluator Artificial Analysis (September 9, v4.3), the two models are tied for first at 53 points. Their coding agent index is also the same, at 62.

The difference is in what it cost to reach the same score. On average, Fable 5.1 spent $7.63 per index task and Astra spent $3.26. The token prices are the same; the cost differs because of how much they say. Per task, Fable 5.1 used about 78,000 output tokens and Astra about 27,000.

![Cost and output to reach the same score. A shorter bar means less was used.](https://designrefs.com/articles/img/fable-astra-cost-en.svg)

One caution. This index was revised twice in the week after Astra came out, and in that time Astra climbed from fifth to first. It's too early to call these settled numbers.

## Change the kind of work and the ranking changes

| Evaluation | What it measures | Fable 5.1 | Astra | Measured by |
|---|---|---|---|---|
| Code Arena: WebDev | Builds a web app; people pick the better of two | 1758 (2nd) | **1800 (1st)** | Arena user votes |
| Agent Arena | Long tasks using tools | **1st** | 2nd | Arena user votes |
| Design Arena 3D | Building 3D scenes | 1423 (3rd) | **1481 (1st)** | Design Arena user votes |
| Terminal-Bench 4.0 | Coding tasks in the terminal | 55.8% | **57.7%** | OpenAI announcement |
| DeepSWE v1.1 | Long, real-world development tasks | 67.4% | **74.1%** | OpenAI announcement |
| Humanity's Last Exam (with tools) | Expert-level questions | **65.0%** | 57.2% | OpenAI announcement |
※ Sources: [Runtime Wire](https://runtimewire.com/article/arena-gpt-6-astra-webdev-leaderboard-claude-agents) (Arena, Sep 9–13), [Better Stack](https://betterstack.com/community/guides/ai/kimi-claude-astra-design/) (Design Arena), [Vellum](https://www.vellum.ai/blog/gpt-6-astra-benchmarks-explained) (OpenAI's announcement table).

In head-to-heads building web screens, Astra leads; in agent head-to-heads involving long tool use, Fable 5.1 leads. Even in vote-based evaluations where people choose directly, the results split like this.

The row worth noticing is the last one. Even in OpenAI's own announcement table, Fable 5.1 scores higher on expert-level questions.

It's also worth knowing that the two companies choose different tests to announce. Anthropic published a SWE-bench Pro score of 81.2% for Fable 5.1, but OpenAI didn't publish Astra's score on the same test. Cases where the same test's scores sit side by side are rarer than you'd think.

## How designers reacted

When OpenAI introduced Astra, it put [visual judgment in front-end design](https://x.com/OpenAIDevs/status/2095596149654868092) up front: give it a sketch or reference and it turns it into a working screen, refining layout, typography and spacing.

The verdicts from designers who tried them first don't lean one way. One comparison ([Eidos Design](https://eidosdesign.substack.com/p/claude-fable-51-vs-gpt-6-astra-for), September 7) summed it up like this.

- **Astra**: The first draft is already close to finished. Handles layers and space well, strong at 3D and CAD. But it has a habit of adding when it should subtract, overfilling the screen, and when it's wrong, it's confidently wrong.
- **Fable 5.1**: The restrained one, better at refining a screen you'll actually ship. But it lacks boldness, so it needs another pass.
- **Both**: No real taste.

A comparison that split five design tasks between them ([Better Stack](https://betterstack.com/community/guides/ai/kimi-claude-astra-design/), September 14) reached a similar conclusion. For web design, Kimi K3 actually did best; Astra won 3D, and Fable 5.1 won 2D games. UI components were about even across the three, and none of them produced mobile app designs usable as is.

One more. Artificial Analysis noted that on a measure of the quality of documents like presentations, Astra scored lower than its predecessor, GPT-5.6 Sol. Worth knowing if you make a lot of slides.

## In short

The price sheets are the same, but the actual cost depends on how you use them. For work where you attach long material and ask many times, Fable 5.1 with its cheaper cache has the edge; for short, one-shot answers, Astra, which talks less, has the edge.

In evaluations, Astra leads at quickly producing web screens and 3D, while Fable 5.1 leads at long tasks involving tool use. The approach recommended by designers who tried them first lines up with these results: explore first with Astra, finish and refine with Fable 5.1.

And both models are less than a month old. The rankings could change again in a few weeks. In the end, you only know if it fits your work by running it on your work.

AI tools are collected by type under [AI tools](https://designrefs.com/en/#ai). Where to fit any tool into your workflow, I wrote about separately in [Why thirty AI drafts don't make the work any shorter](https://designrefs.com/en/articles/ai-design-tools-in-practice/).
