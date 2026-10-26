---
slug: lovable-design-system-same-look
title: Why Lovable dropped its 'three design directions' step for design systems
desc: Lovable removed the step that showed three design directions before the first build, and design systems are available on all paid plans. Checked against its changelog and docs: what is confirmed, what is missing, and how to set your own rules once.
tag: AI Design
---

If you build screens with Lovable or Cursor, they start to look alike. Rounded cards, a familiar purple, similar spacing. Rewording the prompt doesn't change the feel much. It's easy to blame a lack of design sense and move on.

Lovable's official changelog has had a few entries on this over the past weeks. One removed the 'three design directions' step shown before a first build. Another opened design systems to every paid plan. This piece repeats only what I verified in the changelog and the official docs, and lists separately what remains unconfirmed.

This is based on Lovable's official changelog and docs (August to October entries). There's no public comparison showing that design systems make screens look less alike, so that part is my interpretation. Plan descriptions differed between search summaries and the official docs, which I cover later.

## What changed

The relevant changelog entries:

| Date | Item | What it says |
|---|---|---|
| 2026-08-19 | Design systems | Available on all paid plans. Attach one and every build inherits its components, tokens and design rules |
| 2026-09-21 | Default design system per group | Admins on Business and Enterprise can set a default per group |
| 2026-10-08 | Design directions removed | The three directions shown before building a visually open-ended prompt are gone |
| 2026-10-12 | Image edits in Files tab | Mark a change directly on an image; the result is saved as a new file |

※ Source: [Lovable changelog](https://docs.lovable.dev/changelog)

### The three directions are gone

The changelog says: "The three design directions Lovable showed before building a visually open-ended prompt have been removed." If you typed something like "make it look good" without specifying the look, Lovable used to show three directions before the first build. Now it builds the look straight from your description.

The changelog adds that Lovable still asks about color, typography and layout when your prompt leaves them open. Older chats keep the direction chosen earlier, without previews.

The changelog gives no reason for the removal, so don't read it as 'the step was useless.' All that is confirmed is that the step is gone.

### Design systems on every paid plan

The August 19 entry reads: "Create a design system and attach it to your projects so every build inherits your components, tokens, and design rules." In plain terms, you define parts like buttons and cards plus color and type rules once, and later builds follow them.

Wrapping an existing npm package as a design system is Enterprise only, per the same entry. The docs make the same split: a React component library based system works on all paid plans, the npm wrapper path is Enterprise only.

## What a design system looks like

Lovable's docs describe it as a way to define your component library, styling guidelines and installation instructions once and reuse them across projects in a workspace. The design system itself is a dedicated Lovable project.

The docs list three parts:

1. Components: a React component library
2. Schema and guidelines: a machine-readable schema of tokens, a component catalog and constraints, plus rendered docs. Lovable consults it every time it generates code
3. Installation info: setup and required configuration

On release, the `.lovable` folder gets `design-system.json`, `rules/components.md`, `rules/design-tokens.md` and `rules/library-guidelines.md`. `system.md` is a file you write yourself and is not overwritten on release. The docs suggest putting your design philosophy and usage rules there.

That resembles the [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) approach we covered: a rules memo for the AI, kept as a file it reads each time. Lovable bundles it into the product.

### How to build one

Shortened from the docs:

1. In the prompt box's + menu, choose Design → Use a design system → Create design system. The name is used later when you attach it, so make it recognizable.
2. Configure it in chat. Either import an existing library by npm package name or public Git URL, or build from structured instructions: goal, tech stack, components you want, and reference docs (PDF, Markdown, screenshots).
3. Choose Release version. This generates the schema, renders docs, bumps the version and commits, so it can be attached to projects.
4. For a new project, pick it under + → Design → Use a design system. For an existing one, use Attach design system in Project settings → General.

Once attached, components are copied to `src/design-system/<slug>/` and rule files to `.lovable/rules/libraries/<slug>/`. When a new version appears, chat shows "Update available," and accepting it replaces the existing design system files. The docs say your project's own code is left untouched.

## Limits to know first

The ones that matter most to designers, from the docs:

- One design system per project. Remove the current one before switching.
- An unreleased draft can't be the basis of a new project.
- You can't convert an existing project into a design system. Create a new one.
- Avoid editing the `.lovable` folder or the copied components in a connected project. Updates overwrite local edits. Make lasting changes in the design system project.
- Detaching stops updates and rule enforcement. The copied files stay as ordinary code.
- Only React is officially supported. Vue, Angular and Svelte are not guaranteed.
- Reading uploaded material is best-effort, and the docs tell you to review the first output.

The plan descriptions also differ. A search summary of the docs said design systems are available on Enterprise plans. The changelog (August 19) and the docs' plan section say the React-based version is available on all paid plans. Check Lovable's pricing page before you pay.

## Other changes at the same time

The October 12 entry says you can mark a change directly on an image in the Files tab by drawing over an area, pinning a comment, erasing, or removing the background. The result is saved as a new file. It follows the same direction as [fixing instead of rerolling](https://designrefs.com/articles/image-ai-edit-not-reroll/).

There was also an 'Aesthetics' update in May. Lovable's [post on X](https://x.com/Lovable/status/2053874566460752191) says you can ask for typography, layout and color preferences, preview design concepts before building, and make bolder landing pages, apps and blogs. I got the May 11 date from the secondary outlet Create With and found no detailed Lovable doc. How it connects to the removed 'three directions' step is not confirmed in public material.

## What is still unconfirmed

- Why the three directions step was removed. The changelog gives no explanation.
- Any public side-by-side of builds with and without a design system.
- The credit cost of design systems. The docs say only that the setup verification step costs zero credits, and give no cost for other operations such as updates.
- Related entries in the part of the changelog I did not read.

## What it means for designers

For vibe coders the message is simple: stop persuading the tool with every prompt and attach a rule set you decided once. For designers it's a different job. Writing buttons, cards, colors and type rules in a form AI can read may become a new task. That is my guess.

If [Figma Specs](https://designrefs.com/articles/figma-specs-markdown-context/) passes the context of a design as one markdown page, Lovable's design system looks like the coding-tool version of the same idea. Different tools, same chore: write your rules down.

## So for now

**Write your rules in ten lines.** Pick a main color, an accent, two typefaces, a corner radius and a spacing unit. Even without Lovable, it works as a rules memo for Cursor or Claude Code. We wrote up how in the [DESIGN.md](https://designrefs.com/articles/design-md-for-ai/) piece.

**Don't leave the look open in the first prompt.** Per the changelog, Lovable asks when color, type and layout are unspecified. State them up front, such as "main color this, typeface this," and you skip the question.

**Put the edits you like back into the rules.** As the docs say, editing copied components in a connected project gets overwritten on update. Only changes made in the design system project last.

AI design tools by use are collected on the [AI design tools](https://designrefs.com/ai/) page.

## In short

Lovable removed the step that offered directions on open prompts and made design systems, which hand parts and rules to every build, a feature of all paid plans. Whether that makes screens look less alike is not confirmed. What is clear is that deciding the look is shifting from a line in a prompt to a rules file.

※ Sources: [Lovable changelog](https://docs.lovable.dev/changelog), [Lovable docs: Design systems](https://docs.lovable.dev/features/design-systems), [Lovable on X](https://x.com/Lovable/status/2053874566460752191), [Create With: Lovable Aesthetics](https://www.createwith.com/tool/lovable/updates/lovable-launches-aesthetics-to-give-users-more-control-over-design-output).
