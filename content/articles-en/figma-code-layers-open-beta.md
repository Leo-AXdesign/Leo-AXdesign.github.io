---
slug: figma-code-layers-open-beta
title: Figma code layers in open beta: clickable mockups right on the canvas (free until Nov 4)
desc: Figma opened code layers in open beta on October 15. You can turn design frames, a GitHub repo, a website capture or a prompt into a clickable, code-backed prototype on the canvas. Checked against the release notes, help article and blog: what is confirmed and what is missing.
tag: AI Design
---

A client replies to your mockup: "What happens when I press this button?" A static frame has no answer. Wiring up prototype links can eat a whole day. This is the moment you want a screen that actually responds.

On October 15, at Config India 2026, Figma opened code layers in open beta. They put prototypes backed by running code right on the canvas. This piece repeats only what I verified in Figma's release notes, help article and blog, and lists separately what remains unconfirmed.

Code layers are rolling out gradually, so they may not show up in your account yet. This follows the official docs; I haven't run it myself. Supported frameworks, usage limits and credit costs weren't in the docs, and plan wording differs slightly between pages, which I cover later.

## What a code layer is

The help article describes code layers as interactive prototypes backed by running code that sit on the canvas. Design and code live in one file, so you can compare variations side by side and push changes back to the layer.

In short, a real button sits on the canvas instead of a drawn one. Select a layer and press Play. Several layers can run at once, and you can preview on mobile through the Figma app.

## Five ways to create one

| Method | How |
|---|---|
| From scratch | Pick the Code tool (shortcut B), drag on the canvas, then prompt the Figma agent |
| From your design | Select design frames and click Build selection in the right sidebar. Multiple frames work |
| From a GitHub repo | Clone a connected repository to build on an existing frontend |
| From a local folder | Upload a folder of code files |
| From a website | Use Capture code in the Figma Chrome extension, then paste into a Design file |

※ Source: [Figma Help: Code layers in Figma Design](https://help.figma.com/hc/en-us/articles/44193259600535-Code-layers-in-Figma-Design)

There is one more route. You can ask a coding agent such as Claude Code to import a project into a Figma file. The docs give the example prompt "Import this project as a code layer in <Figma file URL>." Creating layers this way requires a Full seat.

### Imports can be slow

The article says importing a project through MCP can take 10 minutes or more and some projects may need changes to run in a code layer. The blog says support for more complex codebases is planned. Try a small screen first.

## Editing: by words, by clicking

1. Ask the Figma agent in plain language.
2. Open the code editor to view code, add comments and edit designs.
3. Use the point-and-edit tool to select an element in the preview and adjust its properties. Changes apply after you click Apply in the chat.
4. Click Reload code layer to see the result.

Step 3 stands out for designers: you can fix elements by pointing at them without reading code. How accurate it is has no public comparison.

## Back to the canvas, out to GitHub

The flow isn't one-way, according to the docs.

- Extract designs from the current state, a selected element, or a recorded flow that produces multiple frames.
- Push updates from extracted designs back to the code layer.
- With GitHub, Figma stores a clone you can branch, then open pull requests to merge into the original repository.

So the loop can run mockup → clickable screen → mockup → dev repo. When you hand off, you can show behavior as a running screen rather than as notes and pictures.

## Who can use it, and what it costs

- Help article: available on Education (K-12), Starter, Professional, Organization and Enterprise plans, with edit access to Figma Design files.
- Release notes and blog: open beta, available on all plans.
- Free period: the release notes say creating and editing within a code layer is free on paid plans through November 4. The help article says that after that date, all code layer tasks use credits.
- Other agent work tied to the same request still uses credits.
- Credit use varies with task complexity. No numbers are given.
- Imports through GitHub or MCP don't use credits, but later prompts to the Make agent do.

We covered agent credits in [Figma's agent started using credits](https://designrefs.com/articles/figma-agent-ai-credits-ga/). It's the same wallet, so what you'll pay after the free period can't be known from today's numbers.

Plan wording differs: the blog says all plans, while the release notes' free condition says paid plans. What a free-plan account gets can't be settled from the docs alone. Check Figma's pricing page before paying.

Admin controls are limited too. Only Enterprise plans can opt out, and admins can disable code layers only by turning off AI features altogether. Worth knowing if your team is deciding.

## How it fits with the rest of that day's news

The October 15 release notes held more than code layers.

| Item | Status | What it says |
|---|---|---|
| Guidelines | Open beta | Add guidelines to published libraries so the agent follows your patterns |
| Code sources | Closed beta | Import GitHub repos or npm packages so the agent reflects your real design system code |
| Centralized design systems | Preview | Bundle design libraries, code libraries and guidelines in one place |
| Payload | All plans | Make scaffolds a backend with CMS, database, auth and admin panel |
| Figma MCP | Available | Faster, more Figma products supported, 20 new partners |

※ Source: [Figma release notes](https://www.figma.com/release-notes/), [Figma blog: Config India 2026](https://www.figma.com/blog/build-by-design/)

The blog says guidelines and code sources will be available on all paid plans. Those two matter here: if code layers make a screen you can click, guidelines keep it from drifting off your rules. That ties to [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) and [Figma Specs](https://designrefs.com/articles/figma-specs-markdown-context/), covered earlier.

## Still unconfirmed

- Which frameworks and languages code layers support. The help article names none.
- Per-task credit costs after the free period.
- The quality of the code produced. I found no public evaluation.
- Exactly what a free-plan account can do. The documents word it differently.
- Which projects fail to import. The docs say only that some need changes.

## What this means for designers

Making a prototype has meant wiring links. Code layers put "instructing a running screen in words" in that place. If people can click a design before handoff, questions like "is it supposed to move like this?" in development might shrink. That is my guess, with no verified evidence yet.

For vibe coders it runs the other way. You can bring a built screen into Figma, extract it as a design, adjust spacing and color there, and send it back. If you lack design sense, there is now a path to polish in a design tool.

## What to do now

**Test one small screen before November 4.** Pick a login screen or a pricing table and click Build selection. When importing an outside project, avoid large ones because imports can take 10 minutes or more. A feel for how it behaves during the free window helps you judge credits later. The free window applies to paid plans.

**Hand off a clickable screen with your next mockup.** Instead of long notes on a static frame, show how it behaves. Start by checking whether it answers the client's one-line question: "what happens when I press this?"

**Write your rules down first.** Guidelines attach to published libraries. If you don't have one yet, start with a ten-line note: main color, fonts, corner radius, spacing unit. It works in any tool.

AI design tools by use are collected on [AI design tools](https://designrefs.com/ai/).

## Summary

Figma now lets a running, code-backed prototype sit beside a static mockup, and creating and editing is free on paid plans through November 4. How far you can trust it has no public comparison yet. What is certain is that the work is moving a step from drawing a design to letting people click it.

※ Sources: [Figma release notes](https://www.figma.com/release-notes/), [Figma Help: Code layers in Figma Design](https://help.figma.com/hc/en-us/articles/44193259600535-Code-layers-in-Figma-Design), [Figma blog: Config India 2026](https://www.figma.com/blog/build-by-design/).
