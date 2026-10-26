---
slug: figma-agent-ai-credits-ga
title: The Figma agent now costs credits. How to make a month's worth last
desc: Figma's design agent has left beta and now consumes AI credits. Checked against Figma's FAQ and pricing page: what is confirmed, what is missing, and how to stretch a month's allowance.
tag: AI Design
---

If you tried Figma's agent during the beta, you probably never worried about the cost of a prompt. That period is over. According to Figma's official AI credits FAQ, the agent in Figma Design and the Weave tools became generally available on October 6, 2026, and have consumed AI credits since.

If you don't know what a prompt costs or how large the monthly allowance is, you hit a wall at the end of the month. This piece follows Figma's FAQ, its pricing page and a community forum reply, and separates what is confirmed from what is missing.

## What changed

From the 'Agent and Weave tools' section of Figma's FAQ:

- The agent in Figma Design and the Weave tools became generally available on October 6, 2026, and now consume AI credits.
- They share one budget with other generally available AI tools such as Figma Make.
- Weave tools have a fixed credit cost per tool. Agent usage varies with prompt complexity, the actions taken and the context you provide.
- Usage during the beta did not consume AI credits.
- Organization and Enterprise admins can download a CSV of beta usage. It contains only beta-period data.

The line to notice is the shared budget. In a month when you generate a lot with Make or image tools, there is less left for the agent. The FAQ says that if other AI tools have used up the budget, the agent may show 0 credits left.

## How big is a month's allowance

Here are the monthly credits listed on Figma's pricing page. Every seat gets a monthly allotment of AI credits.

![Monthly AI credits per Figma plan](https://designrefs.com/articles/img/figma-ai-credits-by-plan-en.svg)

| Plan | Monthly credits, Full seat | Monthly credits, Dev and Collab seats |
|---|---|---|
| Starter (free) | 500 (150 per day, up to 500 per month) | 500 |
| Professional | 3,000 | 500 |
| Organization | 3,500 | 500 |
| Enterprise | 4,250 | 500 |

※ Source: [Figma pricing page](https://www.figma.com/pricing/)

On the same page, seat prices on Professional are $16 a month for Full, $12 for Dev and $3 for Collab. The page doesn't say whether the Professional prices are for monthly or annual billing. Organization is $55 for a Full seat on annual billing and Enterprise is $90. Prices can change, so check the page before you buy.

The pricing page says "Number of credits used varies by request." There is no per-feature price list. According to the FAQ, credits reset monthly and the remaining amount shows in the AI Balance menu.

## What one run costs: a single clue

There is no official unit price, but there is one clue. On August 12, a post in Figma's community forum quoted a tooltip on the beta agent: "After beta, it will use 196 credits." A reply in the community described that number as a 'predictive receipt', a preview of what a similar prompt would cost after the beta. The same reply said prompts run during the beta won't be charged, now or later.

Some rough arithmetic follows. It is mine, and it rests on one prompt from one user.

- Professional Full seat: 3,000 ÷ 196 ≈ 15 runs
- Starter: 500 ÷ 196 ≈ 2 runs

Smaller prompts would allow more and larger ones fewer. Read it as a sense of scale, not an exact count. If you hand over whole screens every day, a month's allowance could shrink quickly. The forum answer is community guidance rather than an official policy page, and when it was written on August 12 no GA date had been set. The only reliable way to know today's cost is to run a prompt and check AI Balance.

## When you run short

Teams that use AI often can buy more credits through a subscription or pay-as-you-go billing. The pricing page says purchased credits are shared by the whole team. The FAQ says that from August 25 the add-ons give more credits at the same price: 2x on Professional and 1.6x on Organization and Enterprise. It applies automatically, invoices may show adjustment lines but the net cost stays the same, and the monthly spending limit is unchanged.

## What isn't confirmed

- The average credits for one agent prompt. There is no official price list.
- Which plans can use the agent. The pricing page doesn't say.
- Whether seat credits pool across a team or unused credits carry over. The pricing page doesn't state it.
- The credit ratio against other AI features such as Make and image tools.
- The situation for the agent in FigJam and Slides. The FAQ section I checked mentions only the Figma Design agent and Weave tools.

## Read it with the earlier pieces

[Figma Specs](https://designrefs.com/articles/figma-specs-markdown-context/) was about handing context to a team and AI in one markdown page. This change adds a price to handing that context to an AI. The FAQ says credit use varies with the context you provide. Keeping your rules short might improve results and also reduce usage. That is my guess, and no public test backs it up. The rules memo is covered in the [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) piece.

## So for now

**Open AI Balance first.** Note today's remaining credits, run one small prompt, and see how much dropped. That gives you a unit price for your own work. With no official price list, this is the most accurate method.

**Split prompts into small ones.** Asking for one card or one header at a time, instead of a whole screen, limits how much you spend on a result you don't like. This leans on the FAQ's note that usage varies with complexity and context.

**If you're on a team, ask your admin.** Purchased credits are shared, and Organization and Enterprise admins can download beta usage as a CSV. Seeing how much you used in the beta gives a rough idea of scale after GA.

AI design tools by use are collected in [AI design tools](https://designrefs.com/ai/).

## In short

The agent started drawing credits at general availability, and there is no official price list for one run. The most reliable way is to measure your own work with AI Balance. The arithmetic here rests on a single forum number. I haven't used the agent under credit billing.

※ Sources: [Figma Help: AI credits FAQ](https://help.figma.com/hc/en-us/articles/42614902212887), [Figma pricing page](https://www.figma.com/pricing/), [Figma Community Forum: figma agent beta pricing](https://forum.figma.com/ask-the-community-7/figma-agent-beta-pricing-56929).
