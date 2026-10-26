---
slug: figma-specs-markdown-context
title: Figma Specs: one markdown page that hands context to your team and to AI
desc: Figma has put markdown documents on the canvas with Specs, now in open beta on paid plans. Checked against Figma's own post and release notes: what works, what isn't confirmed, and how it differs from DESIGN.md.
tag: AI Design
---

Figma has added a feature called Specs: markdown documents that live on the canvas. It was announced at Figma's first Config event in India, and Figma's own post is dated October 15.

Open a design file and you can see the frames, but rarely why they look that way. Decisions sit in chat, requirements in a doc, mockups in Figma. Now AI agents have to read all of it too. Figma says it wants to gather that scattered context in one place on the canvas.

So this piece follows Figma's blog post and release notes rather than the launch buzz. I separate what works, who can use it, and what hasn't been confirmed.

This is based on what Figma published and on news coverage; I haven't used the feature myself. Per-plan limits and the exact range of supported markdown weren't in anything public.

## What Specs is

Figma describes Specs as a container for context that sits on the canvas. In its words, "a multiplayer container that allows context to fully express itself." Several people edit it together, and you write it in markdown.

The notable part is that designs can sit inside the document. You can embed FigJam files, frames and canvas nodes directly in a spec, so text and visuals sit side by side and you don't open a separate doc. A spec can be a standalone file or sit alongside your work on the canvas.

There are two ways to make one.

- Drag any existing `.md` file onto the canvas and it becomes a spec.
- In Figma or FigJam, press `D` or click the Specs icon in the toolbar to start a new one.

You can also duplicate a spec so teammates each work on their own version at the same time, then align on a direction later.

## Why markdown

Markdown is easy for people to read and easy for AI to read. [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/), which we covered on October 2, uses it for the same reason: exact values like colors and type sizes go at the top, and prose below explains why and how to use them.

Specs feels like the same idea moving inside Figma, but they aren't the same thing. DESIGN.md is a file format published by Google Labs; Specs is a document on the Figma canvas. One holds rules, the other holds the context of a piece of work. You don't have to pick one. That split is my own reading.

While building this site I checked the contrast of gray text with a checker and fixed it. When the standard is written as a number, a tool points out what the eye missed. Context documents are useful in a similar way.

## Agents read the spec, and comment on it

According to Figma's post, the Figma agent can read comments on a spec and reply to them, so you can work with an agent the way you would with a teammate. Separate conversations with agents run as separate threads, in parallel.

Two connectors were mentioned.

- GitHub connector: the agent can reference a codebase and draft a technical spec.
- Hex connector: the agent can analyze product usage data and leave the results as comments on the spec.

Coding agents connect through MCP. Paste a spec link into a coding agent's prompt, and the markdown, frame references, diagrams, code layers and Code Connect snippets come along with it. The goal is to replace "look at this Figma link and this doc" with a single link.

Figma's post includes examples too. Mark Harvey at Intuit documented an icon set's file names, categories, tags and descriptions in a spec. A Figma researcher collects brainstorm results and open questions in one. The second is closest to how designers might use it.

## What shipped alongside

Here is the status of each item, from the October 15 release notes and TechCrunch.

| Feature | Status | Availability |
|---|---|---|
| Specs | Open beta | Paid plans |
| Guidelines | Released (stage not stated) | Plan not stated |
| Centralized design systems (design library + code library + guidelines) | Preview | Not stated |
| Code layers | Public beta (moved from June's private beta) | Not stated |
| Figma agent | Generally available October 6 | Uses AI credits |
※ Source: [Figma release notes](https://www.figma.com/release-notes/) (checked October 16), [TechCrunch](https://techcrunch.com/2026/10/14/figma-announces-new-features-to-define-how-agents-work-on-its-platform/)

Guidelines deserve attention. Per the release notes, you can attach rules, best practices and anti-patterns to a published design library as markdown files, and the agent reads them every time someone prompts with the library enabled. Our earlier piece on [the week AI started drawing screens](https://designrefs.com/articles/chatgpt-intelligent-ui-figma-agent/) asked who holds the design rules. This is Figma's answer: people write the rules down, and the agent follows them.

Figma is also aware that AI output varies from run to run. TechCrunch reported that the announcements include tools meant to make results more predictable. No numbers on how much more predictable have been published.

The agent has used AI credits since October 6. The more context you attach and the more often you prompt, the more credits it may use, so check this if your team plans to use it. The release notes say custom skills are available even on the Starter plan.

## What isn't confirmed

- Specs pricing and when the beta ends. Figma only says open beta on paid plans.
- Limits such as file size or number of specs.
- Range of supported markdown syntax. You'll have to open it to see how far tables and checklists go.
- Behavior with Korean documents. No published test shows how well the agent follows a spec written in Korean.
- Which plans get guidelines and centralized design systems.

## So for now

**Drag one existing document onto the canvas as a spec.** A project brief or meeting notes in `.md` is enough. Before writing anything new, see how what you already have looks on the canvas. If you aren't on a paid plan, you'll have to wait for access.

**Write three lines on why you did it this way.** Next to a mockup, note the decision, the options you dropped, and what you still don't know. These three lines are useful whether a person or an agent reads them. Keeping open questions in their own place comes from the Figma researcher's example.

**Keep rules and context separate.** Put colors and type in [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) or guidelines, and the background of this piece of work in the spec. They won't blur together, and it's clear which text an agent should read.

AI design tools by use are collected on [AI Design Tools](https://designrefs.com/ai/).

※ Sources: [Introducing Specs: Markdown as a medium (Figma blog)](https://www.figma.com/blog/introducing-figma-specs/), [Figma release notes](https://www.figma.com/release-notes/) (checked October 16), [TechCrunch](https://techcrunch.com/2026/10/14/figma-announces-new-features-to-define-how-agents-work-on-its-platform/).
