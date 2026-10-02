---
slug: shopify-canvas-sidekick
title: Shopify Canvas lays out your whole store at once and lets you edit it with AI
desc: Shopify's Canvas, launched October 1, puts every page of a store on one surface. You click to edit, or tell Sidekick what you want. Here's what changed and what doesn't work yet, with diagrams and a table.
tag: AI Design
---

Shopify launched Canvas on October 1. It's a new workbench for designing online stores.

The name already sounds familiar to designers, and so does the thing itself. Every page of the store is laid out on one surface. You pan across it and zoom in on details, much like opening a Figma file. The difference is that what sits on this canvas isn't a mockup. It's the working store.

**First, a disclaimer.** Canvas is rolling out to stores over the coming days. I don't run a Shopify store, so I haven't used it myself. What follows is based on Shopify's announcement and changelog, and on articles covering the launch.

## From one page at a time to everything at once

Until now, Shopify stores were edited in the theme editor. You open one page and click through the settings listed on the left, one by one. To check the product page while working on the home page, you had to switch pages.

![The theme editor versus Canvas. A diagram based on the announcement, not the actual interface.](https://designrefs.com/articles/img/shopify-canvas-compare-en.svg)

Canvas flips that around. A store's pages, design elements and design system all sit on one screen. There are two ways to make changes.

- **Click directly.** Click any element on the canvas and edit it.
- **Say it.** Tell Sidekick, Shopify's AI assistant, what you want in the chat beside the canvas. From a single section to a store-wide redesign, the changes show up on the canvas as they happen.

The preview isn't a picture either. Shopify stresses that what's rendered is the real code behind the store, not a mockup. So you can check pages with animations and interactions intact, swapping in different products and collections and changing screen sizes.

## Two weeks and twenty minutes

Ben Sehl, Shopify's Director of Product, is also a co-founder of the clothing brand Kotn. The comparison he made at the launch stands out.

![Two numbers from Ben Sehl. Two weeks then, twenty minutes now. Not a like-for-like measurement.](https://designrefs.com/articles/img/canvas-store-time-en.svg)

> When I built Kotn 12 years ago, I knew how to code and it still took me two weeks to get a rough store working. Today, an entrepreneur on Shopify can build a fully custom store in twenty minutes that's head and shoulders above what I built then.

On a chart, the second bar is barely a dot. But this is a company insider's memory mixed with a sales pitch, not a measurement of the same store under the same conditions. Read twenty minutes as "enough to get started". Picking photos, polishing copy and filling in product details aren't in that number.

## What doesn't work yet

On day one, Canvas has a fair number of gaps. Shopify says they'll be filled over time.

| Item | In Canvas today |
|---|---|
| Third-party themes from the Theme Store | Not supported. Only Shopify-made and custom themes |
| App blocks and app embeds | Can't be added or configured |
| Adding new blocks | Not by hand. You have to ask Sidekick |
| Per-market customization, translation | Not supported. Translate in the Translate & Adapt app |
| Theme updates | A theme edited in Canvas stops receiving them |
| Downloading theme files | Not possible |
※ Sources: [Shopify changelog](https://changelog.shopify.com/posts/design-a-fully-bespoke-store-with-canvas), [TechCrunch](https://techcrunch.com/2026/10/01/shopify-debuts-canvas-a-way-to-build-online-stores-by-chatting-with-ai/). Sidekick is included on every plan at no extra cost.

The last two rows are the ones to watch. A theme edited in Canvas no longer gets updates from the original theme, and you can't download its files to work on elsewhere. Once a theme goes in, it lives inside Canvas.

The good news is you can start carefully. Under Online Store > Themes, create a new theme in Canvas, or duplicate your current theme and open the copy in Canvas. The original stays in the existing editor. For now, Canvas is desktop-only.

## What changes for designers

If you design Shopify stores for clients, the shape of the work shifts a little.

Until now it was two steps: make the design in Figma, then move it over through a developer or the theme editor. Canvas shortens the gap, because the surface you design on and the live store become the same surface. It also brings the moment when the store owner tells Sidekick "make the buttons black" themselves.

So the work that remains is this: deciding which buttons should be black, and why, and writing it down. Having the design system on the canvas also means the AI reads those rules and follows them. If the rules are blank, the AI fills them in on its own. I pick this up tomorrow in [DESIGN.md, the file that hands your design rules to AI](https://designrefs.com/en/articles/design-md-for-ai/).

One more thing. In last week's [DevDay roundup](https://designrefs.com/en/articles/openai-devday-2026-designers/), design tools were moving into ChatGPT. This time a design workbench moved into a commerce tool. Wherever you start, things are converging toward touching the real product directly.

## So, for now

If you have a Shopify store, duplicating your current theme and opening the copy in Canvas is about right. Leave the original alone, and if your store relies on app blocks or translations, hold off on moving over.

One thing worth trying on the copy: tell Sidekick three of your store's usual rules first (say, button shape, heading size and photo ratio), then ask it to build a new page. How many pages it keeps those rules for will tell you how far to trust this workbench.

For store references, see [UI/UX references](https://designrefs.com/en/#uiux). AI tools are collected under [AI design tools](https://designrefs.com/en/#ai).

※ Sources: [Shopify, Introducing Canvas](https://www.shopify.com/news/introducing-canvas), [Shopify changelog](https://changelog.shopify.com/posts/design-a-fully-bespoke-store-with-canvas), [TechCrunch](https://techcrunch.com/2026/10/01/shopify-debuts-canvas-a-way-to-build-online-stores-by-chatting-with-ai/), [Unite.AI](https://www.unite.ai/shopify-rolls-out-canvas-a-sidekick-powered-store-design-surface/), [ecommercenews](https://ecommercenews.com.au/story/shopify-launches-canvas-ai-workspace-for-store-design).
