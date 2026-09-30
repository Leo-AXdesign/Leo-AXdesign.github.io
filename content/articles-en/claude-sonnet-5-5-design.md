---
slug: claude-sonnet-5-5-design
title: Claude Sonnet 5.5 leads with "an eye for design", and the mid-priced tier changes
desc: Anthropic's Sonnet 5.5, released September 28, put design sense front and center. Same price, faster work. Plus what happened when someone had it build a one-page site, in numbers.
tag: AI Design
---

Anthropic released Claude Sonnet 5.5 on September 28 (US time). In Korea, the news spread this morning.

Sonnet is the middle tier of Anthropic's lineup. Not the priciest, smartest model, and not the cheapest, fastest one. Its launches are usually quiet, but this one had a line that stood out: Anthropic wrote that the model has "a sharp eye for design".

It's unusual for a mid-priced model to lead with design. And this tier is closer to designers than you might think. For a tool company selling AI features, cost makes this price range the natural default rather than the most expensive model.

**First, a disclaimer.** I'm building this site with Claude Code. So I've only used company announcements and results from people outside who ran their own tests, and noted who measured what.

## Same price, crowded row

The price is the same as Sonnet 5: $2 input and $10 output per million tokens. What changed is speed and how much it says. Anthropic says it's more than 30% faster than the previous model and finishes the same work with fewer tokens, so most tasks cost up to 30% less.

![Price per million tokens. Models from two companies stand side by side in the $2 input, $10 output row.](https://designrefs.com/articles/img/price-tiers-0929-en.svg)

Put it on a chart and something interesting shows up. OpenAI's GPT-6 Sol sits in the same $2 / $10 row. After [the week AI got half price](https://designrefs.com/en/articles/ai-price-cut-week/), the two companies' mid-tier models now face each other at exactly the same price. The top row is still $10 input and $50 output.

## What it's supposed to be good at

Anthropic's list: well-scoped everyday tasks, fixing bugs, and making polished documents, slides and spreadsheets. Design was added to that. It's described as adding polish to interfaces and following templates well. In internal testing, Anthropic says it produced an investment presentation that needed almost no editing.

| Evaluation | Sonnet 5 | Sonnet 5.5 | Measured by |
|---|---|---|---|
| GDPval-AA (real-world document work) | 1449 | **1844** | Anthropic |
| FrontierCode (max effort) | 42.4% | **46.2%** | Anthropic |
| Speed | baseline | **30%+ faster** | Anthropic |
※ Source: [Anthropic, Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5). Anthropic also noted it scores two points below the higher-tier Opus 5.5 on GDPval-AA.

Launch tables tend to collect the good numbers. So I was more curious about results from someone outside.

## Asking it to build a one-page site

Right after launch, developer Thomas Wiegold [posted a test on his blog](https://thomas-wiegold.com/blog/claude-sonnet-5-5-review/). The task: a single page for "Low Tide", a made-up outdoor screening of three short films on a beach. The content was fixed (date, gate times, programme, tickets, FAQ), and Opus 5.5, Sonnet 5.5 and Sonnet 5 each got the same setup.

The ranking was Opus 5.5, Sonnet 5.5, then Sonnet 5. But the character of each result is what's interesting.

Opus 5.5 went for atmosphere. A big, soft "Low Tide" wordmark over a sunset, with the type and the sun reflected in the water line. Nine animations, and the most thorough accessibility work.

Sonnet 5.5 went toward print. Cream and navy, a flat orange sun, and type pairing roman with italic. Only four animations, but chosen with care, and it included a reduced-motion fallback. The reviewer pointed out that it came up with the same slider idea as Opus but executed it in a completely different way.

Sonnet 5 applied a film-reel theme mechanically: sprocket-hole borders, sections numbered as reels. There was an idea, but it felt like a template.

![Cost, time and output for the same task. Sonnet 5.5 was cheaper than Opus, and said more.](https://designrefs.com/articles/img/sonnet55-lowtide-en.svg)

The numbers are worth a look too. Sonnet 5.5 finished for $1.35, 30% less than Opus 5.5 ($1.94). But it actually produced more output tokens than Opus. The total came down because its tokens are cheaper, not because it said less. It's a personal test with one run per model, so it can't settle which is better on its own.

## What a better middle tier changes

Designers don't often pick a model by name. Usually we use whatever model our tools have chosen, and which tier a tool uses is decided by cost.

So if the middle tier gets better design sense, the first drafts from tools we use without knowing the model underneath can improve along with it. That's closer to daily work than the top model's score.

Checking for yourself isn't hard. Give it one template you use often and one page of brand guidelines, and ask it to build the same page. Watch how well it sticks to the template, and where it lets spacing and type sizes drift. That's the part Anthropic sounded most confident about this time.

If the model names are confusing, my earlier [comparison of Fable 5.1 and Astra](https://designrefs.com/en/articles/claude-fable-5-1-vs-gpt-6-astra/) helps sort out the tiers. Tools by use case are collected under [AI tools](https://designrefs.com/en/#ai).
