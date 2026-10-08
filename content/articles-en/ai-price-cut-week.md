---
slug: ai-price-cut-week
title: AI got half price in a week. Will design tools follow?
desc: On September 22, Opus 5.5, GPT-6 Sol and Luna all launched on the same day and the price sheets changed dramatically. What that means, in numbers, for the credits and subscriptions designers pay for.
tag: AI Design
---

Last Tuesday, September 22, three price sheets changed in a single day. Anthropic released Claude Opus 5.5, and the same day OpenAI unveiled GPT-6 Sol and GPT-6 Luna. All three are cheaper than the previous generation. Quite a bit cheaper.

API prices sound far removed from designers. Not many designers call an API directly. But the credit prices charged by Figma Make, Canva and every image and prototyping tool out there sit on top of these numbers. When the underlying cost goes down, what we pay moves too, eventually. The only question is when, and by how much.

**First, a disclaimer.** All prices are as of September 27. OpenAI's developer event (DevDay) is scheduled for the 29th, so they may change again within days. Also, I'm building this site with Claude Code, which is why I've only used numbers from company announcements and independent outlets.

## The price sheet, one week later

| Model | Input (per 1M tokens) | Output (per 1M tokens) | vs. previous generation |
|---|---|---|---|
| Claude Opus 5.5 | $4 | $20 | 20% cheaper than Opus 5.0; cache reads 60% cheaper |
| GPT-6 Sol | $2 | $10 | Half of GPT-5.6 Sol |
| GPT-6 Luna | $0.10 | $0.50 | Half of GPT-5.6 Luna |
| (For reference) Claude Fable 5.1, GPT-6 Astra | $10 | $50 | Unchanged |
※ Sources: [Simon Willison](https://simonwillison.net/2026/Sep/22/opus-and-sol-and-luna/) (Sep 22), [Digital Applied's September model release tracker](https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker).

What stands out more than the numbers is Anthropic's claim. It said Opus 5.5 performs at the level of Fable 5.1 on most work. If that's true, you can now get what the top model did three weeks ago for 40% of the price. It's the company's own claim, though, so it's worth waiting for independent evaluations to pile up.

This didn't happen out of nowhere this week, either. According to [Vercel's figures](https://vercel.com/blog/ai-gateway-production-index-september-2026) from its gateway that routes to many AI models, the average token price fell 23.2% in August alone, the third monthly drop in a row. September 22 is closer to the day that trend showed up on the price sheets all at once.

## The top row hasn't moved

Not everything got cheaper. The bottom row of the table, Fable 5.1 and Astra, is still $10 input and $50 output.

If anything, a new tier seems to be forming above them. According to a September 27 report by Korea's AI Times, traces of a $500-a-month "Pro Max" plan were found in ChatGPT's settings screen. That's two and a half times the current top Pro plan ($200 a month). There's no official announcement yet.

So prices aren't moving in one direction; they're spreading apart. Common work is getting cheap fast, while the best models and the fastest processing hold on to high prices.

And cheap tokens don't mean cheap work. In my earlier [comparison of Fable 5.1 and Astra](https://designrefs.com/en/articles/claude-fable-5-1-vs-gpt-6-astra/), the price sheets were identical, yet the cost per task differed by more than double, because of how much each model talked. A similar story came up this time. Simon Willison wrote that when he set Opus 5.5 to maximum thinking, it used up the entire 128,000-token output limit without reaching a conclusion, costing $2.56 per attempt. Even so, he said he'd switched his default models for development work to GPT-6 Sol and Opus 5.5.

## It's already reaching design tools

Figma moved first. At the Goldman Sachs technology conference on September 8, CEO Dylan Field said Figma had cut the price of Figma Make credits quite a bit, in some cases by half. He explained that the company chose to grow usage over short-term margins.

On the 16th of the same month, Figma let people publish Figma Weave, its workflow tool for generating images and vectors, to the Community. It's free for now while in open beta. But Figma has already announced that it will consume AI credits once it's generally available. Free is for the beta only.

## What's getting cheaper is the price, not the result

At the same event, Field also said this: "Hallucination is a huge issue." Pulling a design system into the wrong context is still a problem too, he said. His assessment was that frontier models are improving at design work only incrementally.

Designers' experience isn't much different. The [AI in Design Report 2026](https://stateofaidesign.com/), published May 20 by Designer Fund and Foundation Capital, surveyed more than 900 designers in over 60 countries. The survey was run in the first quarter of this year.

- 91% of designers use AI every week, up sharply from 54% last year.
- The average designer uses 7 AI tools, more than double last year's 3.
- 62% named inconsistent output as their biggest challenge.
- The top reason people keep using a tool is reliable quality (80%).

If price were the problem, it would be solved by now. These numbers say it isn't. What people want isn't a cheaper result but one that's reliably good every time.

## So what you can do now

If you use seven tools, it's probably time for a cleanup. There's a good chance two subscriptions are doing the same job.

It's also worth checking which model each of your tools uses. It's usually listed in the settings or the help pages. If the underlying cost has halved and the credit price hasn't moved in three months, that's one reason to switch tools.

You can hold off on annual plans for a bit. Unit prices have dropped three months in a row, and there's another announcement on the 29th. Paying month to month hurts less right now.

Lower costs don't immediately bring subscription prices down. Sometimes the price stays the same and you get a few more credits instead. Next month, count once more what one credit on your plan actually buys you, and how many times. AI tools by use case are collected under [AI tools](https://designrefs.com/en/#ai).

※ Corrected Oct 8: the AI in Design Report 2026 was published on May 20, not September 16 as originally stated.
