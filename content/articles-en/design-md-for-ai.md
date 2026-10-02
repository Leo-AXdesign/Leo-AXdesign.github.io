---
slug: design-md-for-ai
title: DESIGN.md, one file that hands your design rules to AI
desc: As AI makes more of our drafts and code, where you write down your rules starts to matter. I wrote this site's rules in Google's DESIGN.md format and ran the official checker on it. Here's what it caught.
tag: AI Design
---

Two design stories this week pointed in oddly similar directions.

[Canvas](https://designrefs.com/en/articles/shopify-canvas-sidekick/), which Shopify launched yesterday, lays a store's design system out right beside its AI assistant. The day before, Figma updated its Motion feature so that motion values such as easing and duration can be saved as "animation styles" and published to libraries. Both come down to keeping rules in one place, so that people and AI can pull from the same rules.

One way of keeping rules in one place keeps coming up lately: a single file called DESIGN.md.

**First, a disclaimer.** I'm building this site with Claude Code, and the experiment below was done there too. The checker is Google's official tool (version 0.4.0), used as is.

## What is DESIGN.md?

It's a format Google Labs used inside Stitch, its AI design tool. Google opened the format on April 21, so any AI tool can now read it. It's licensed under Apache 2.0 and still in alpha.

The structure is simple. One markdown file, two layers.

![The structure of a DESIGN.md file. Exact values on top, the reasons for them below.](https://designrefs.com/articles/img/design-md-anatomy-en.svg)

Between the `---` fences at the top go the tokens: colors, type, corner radius, spacing and components, as exact values. Below that, you explain in prose why you use those values. In Google's words, tokens give agents exact values, and prose tells them why those values exist and how to apply them.

That second layer is the point. Give an AI just the value `#6B6B6B` and it'll use that gray anywhere. Add one line, "only for descriptions", and it stops putting that color in headings.

## What goes in it

The prose sections have a set order. You can skip any of them, but the ones you use must follow this order.

| Order | Section | What to write |
|---|---|---|
| 1 | Overview | The brand's character and overall mood, in a sentence or two |
| 2 | Colors | Each color's name, value and where it's used |
| 3 | Typography | Type scale steps and their uses |
| 4 | Layout | Spacing and grid |
| 5 | Elevation & Depth | Shadows and layering |
| 6 | Shapes | Corner radius |
| 7 | Components | How parts like buttons and inputs are put together |
| 8 | Do's and Don'ts | What not to do |
※ Source: the spec in [google-labs-code/design.md](https://github.com/google-labs-code/design.md).

If you've ever made a brand guidelines PDF, the outline will look familiar. The difference is that an AI is reading it, so values and conditions work better than vague adjectives. "Emphasis by weight, not color" beats "a refined feel".

## I tried it on this site

Talking about it in the abstract didn't feel like enough, so I wrote this site's rules out as a DESIGN.md. This site uses only black and white: a few grays, one typeface and a few corner radius steps. Then I ran `lint`, the checker Google released alongside the format.

It came back with four warnings. Two were worth a look.

**First, one gray fell short.** The light gray `#A3A3A3`, used for site domains and tags, measured 2.52 : 1 contrast on white. The web accessibility standard for body text (WCAG AA) is 4.5 : 1. When I picked it I thought "less important text, so lighter". The checker drew the line with a number.

![Contrast on white for this site's four grays and one candidate. Only one falls below 4.5.](https://designrefs.com/articles/img/designmd-contrast-en.svg)

I put in `#767676` as a candidate and ran the `diff` command. It pointed out exactly one changed token and one fewer warning. At 4.54 : 1, it barely passes. Whether I actually switch is something I'll decide after looking at it on screen.

**Update.** The day this went up, I re-checked the whole site and switched to `#767676`. The matching gray in dark mode (`#5E5E5E`, 2.96 : 1) failed too, so it went up to `#868686`. The old gray stays only on decoration that isn't text, like the dot in the logo.

**Second, a warning about a missing primary color.** When there's no color named `primary`, the checker says the agent will auto-generate key colors. This site leaves out a primary color on purpose, being black and white, but an AI reads that gap as "not decided yet". So I need to write "There is no accent color. Don't create one" under Do's and Don'ts. Even what's absent has to be written down to be respected.

The other two warnings were about colors defined but never used by any component. It found some tidying up for me.

## How it fits with the tools you already use

DESIGN.md doesn't replace Figma variables or token files. With the checker's `export` command, the same tokens can be exported as a Tailwind config, CSS variables, or the W3C design token format (DTCG). Values stay in one place and flow out to many.

The difference is who reads it. Token files are read by code people write. DESIGN.md is read by AI. Put the file in a project folder and coding agents like Claude Code or Cursor read it before building any screens.

One caution. As the format caught on, sites offering "DESIGN.md collections" appeared, and people have pointed out that some of them don't match Google's official spec. If you're going to use someone else's file, run `lint` on it first.

## So, for now

You don't need to fill all eight sections from the start. This is enough to begin.

1. **Five colors or fewer.** A name, a value and one line on where each is used.
2. **Three type sizes.** Heading, body, small text.
3. **Three things not to do.** Write down the directions AI tends to drift in. No gradients, say, or no drop shadows.

Then run `npx @google/design.md lint DESIGN.md`. Like me, you might find that a color you've used for ages doesn't meet the standard. You end up checking your rules before handing them to AI.

How to put a style into words for AI is covered separately in [How to describe a design style](https://designrefs.com/en/articles/describing-design-style/). Tools for checking color contrast are under [Color](https://designrefs.com/en/#color).

※ Sources: [Google blog, Stitch's DESIGN.md format is now open-source](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/), [google-labs-code/design.md](https://github.com/google-labs-code/design.md), [the-decoder](https://the-decoder.com/googles-open-source-design-md-gives-ai-agents-a-prompt-ready-blueprint-for-brand-consistent-design/), [Figma release notes](https://www.figma.com/release-notes/), [note.com comparison with the official spec](https://note.com/ai_driven/n/n191c47fa4e24).
