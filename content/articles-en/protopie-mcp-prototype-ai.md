---
slug: protopie-mcp-prototype-ai
title: ProtoPie opens up to MCP: AI can read, edit and hand off your prototypes
desc: ProtoPie has announced official MCP support. Studio MCP lets an AI read and edit the prototype you have open; Code MCP hands finished prototypes to coding agents. Checked against ProtoPie's own post and docs: what works and what isn't confirmed.
tag: AI Design
---

ProtoPie has announced official support for MCP. The byline on ProtoPie's blog post says October 7, while the page metadata says October 15. The two dates disagree, so I couldn't confirm the exact publication date.

Anyone who has built interaction prototypes knows the scene. To make a card expand when a button is tapped, you attach a trigger, pick a response and wire up a variable. It isn't hard, but it takes many small steps. Then you hand the finished prototype to a developer and the question comes back: how do we build this behavior? ProtoPie has put AI into both of those stretches.

This piece follows ProtoPie's blog posts and docs, and separates what works from what hasn't been confirmed.

This is based on what ProtoPie published; I haven't used the feature myself. Pricing, usage limits and per-plan scope were missing or inconsistent across the public pages.

## What MCP does here

MCP is a convention that lets AI tools call features in other programs. In ProtoPie's docs there are two servers, and they share the same ProtoPie account.

- **Studio MCP**: connects an AI to ProtoPie Studio so it can read and change the prototype you have open. It runs locally inside Studio, while the AI runs in the MCP client you connect.
- **Code MCP**: lets AI coding agents take a finished prototype and rebuild it in code. It runs on your machine through `npx` and is read-only.

In short, one is for making and the other is for handing off.

## Studio MCP: ask in words, fix by hand

The docs list five uses for Studio MCP.

- The AI reads and edits the open prototype. It can also capture the canvas.
- It authors layers, layouts and interactions by prompt. The example given is adding a Tap trigger to a button.
- It uses your own component libraries, building screens from the assets and components you already have in ProtoPie.
- It validates prototypes, checking whether behavior matches expectations and flagging interaction or flow issues.
- It targets specific elements by ID: layers, scenes, variables, components, triggers and responses. You copy an ID and paste it into your prompt, as in Change the interaction for [element ID].

Two things stand out. First, the AI pulls real instances from your component library instead of inventing parts. Second, you point at things by ID. It reads as a way to cut down the case where you say that button and the wrong layer changes. That reading is mine, and no public test shows how accurate it is.

ProtoPie says every generated interaction stays fully editable inside Studio. You continue by hand instead of rebuilding from scratch.

## Code MCP: handing a prototype to implementation

Code MCP sits on the developer side. ProtoPie says it helps AI coding agents understand finished prototypes and generate implementation output from them. The post names seven officially supported frameworks.

- React, React Native, Qt/QML, Flutter, SwiftUI, Compose and ArkTS

Dev View, introduced alongside it, lets you share a whole prototype, a single scene, a component or one layer. Instead of telling a developer to look at the entire screen, you can narrow the context to one component.

The [Figma Specs](https://designrefs.com/articles/figma-specs-markdown-context/) we covered passes context to coding agents through a single link too. The direction is the same, but what gets passed differs. Specs carries written context and mockups; ProtoPie carries a prototype with motion. Transitions and reactions that are hard to put into words can be shown as they are. That is my interpretation as well.

## Which AI connects

ProtoPie does not ship its own model. It follows a Bring Your Own Model approach. The post bylined July 20 names MCP-compatible clients such as Claude Code, Codex, Cursor, VS Code and Antigravity, and says support will keep expanding. The Studio MCP docs also name Claude Desktop.

There are a few conditions.

- ProtoPie Studio 10.3.0 or later, the version that ships the MCP server.
- The AI client and ProtoPie Studio must run on the same computer.
- A Pro or Enterprise plan.

The July post also says model quality matters. Models comparable to Claude Sonnet work well for simpler tasks, while Opus-class models generally produce stronger results for complex interactions and implementation. There are no numbers or test results behind this; it is ProtoPie's guidance.

A tool being connected may not be the same as getting the result you wanted. After connecting, you still decide what to ask and check what comes back. ProtoPie also assumes a flow where people fix what the AI makes.

## Plans: what is confirmed and what isn't

ProtoPie's public pages describe the plans slightly differently. A table helps.

| Page | What it says |
|---|---|
| Post bylined July 20 | In beta; Pro and Enterprise users get it at no additional cost |
| October official-support post | Studio MCP under MCP Core (Pro plan); Studio MCP, Code MCP and Dev View under MCP Enterprise (Enterprise plan) |
| Studio MCP docs | Pro or Enterprise plan, listed as MCP Core |

※ Sources: [ProtoPie blog: official MCP support](https://www.protopie.io/blog/protopie-mcp-official), [ProtoPie blog: from design to code](https://www.protopie.io/blog/blog-protopie-mcp-from-design-to-code-faster), [ProtoPie docs: Studio MCP](https://www.protopie.io/learn/docs/mcp-studio-mcp-introduction)

Whether Code MCP is available on the Pro plan reads differently depending on the page. The October post ties it to Enterprise, while the July post says Pro and Enterprise users pay nothing extra during the beta. It does not clearly say whether Code MCP falls inside that beta. Which one holds today is something to check on ProtoPie's pricing page. The official-support post lists no prices.

## What isn't confirmed yet

- Pricing and any AI usage limits. The official-support post has none.
- Whether the Pro plan can use Code MCP.
- Accuracy with Korean-language prompts. No public test exists.
- How much you have to fix in an AI-made interaction in real work.
- The quality of code for each of the seven frameworks.
- The exact publication date of the official post, since dates on the page disagree.

## So for now

**Test it on one small interaction.** A button that opens a modal is enough. If you have a Pro plan and Studio 10.3.0 or later, write down how long the same interaction takes by hand versus by prompt, and how many times you fixed it. That tells you whether it suits your team.

**Tidy your component names and library first.** Studio MCP pulls components from your library. Messy names confuse people and AI alike. Since you copy element IDs into prompts, keeping layer names readable helps.

**Decide what you hand to developers.** Whole screen or a single component? Practice narrowing it with Dev View. Rules can live in [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) or guidelines, and motion in the prototype, so each has its role.

AI design tools by use case are collected in [AI design tools](https://designrefs.com/ai/).

※ Sources: [ProtoPie blog: official MCP support](https://www.protopie.io/blog/protopie-mcp-official), [ProtoPie blog: from design to code](https://www.protopie.io/blog/blog-protopie-mcp-from-design-to-code-faster), [ProtoPie docs: getting started](https://www.protopie.io/learn/docs/mcp-getting-started), [ProtoPie docs: Studio MCP](https://www.protopie.io/learn/docs/mcp-studio-mcp-introduction).
