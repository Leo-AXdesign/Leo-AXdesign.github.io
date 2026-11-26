---
slug: figma-agent-figjam-slides-ga-board-to-deck
title: From a pile of stickies to a spec, from a spec to a first deck: Figma's agent moves into FigJam and Slides
desc: On November 23 Figma made its agent generally available in FigJam and Figma Slides on all paid plans. We list the uses Figma's own posts describe, from organizing boards and summarizing specs to turning a script into slides, and mark what is still unstated, such as credits.
tag: AI Design
---

On November 23, Figma's agent started running inside FigJam and Figma Slides. The release notes call it "generally available" in both, on all paid plans. Until now the agent worked inside design files. This time it reaches the work around the mockup: the notes from meetings and the deck you present.

That matters because most of the time before a mockup exists is spent outside the canvas. You read research notes, group stickies on a board, reread last round's feedback before a crit, and build a deck at the end. This update puts the agent in that stretch.

※ We opened the release notes, Figma's blog post and the help center's section list. We did not run the agent in either product, so every "can" below is a use described in Figma's own posts.

![Figma blog: Figma's agent is now in FigJam and Slides (source: https://www.figma.com/blog/introducing-figma-agent-in-figjam-and-slides/, captured 2026-11-25)](https://designrefs.com/articles/img/figma-agent-figjam-slides-ga-board-to-deck-shot1.webp)
## What the release notes cover

| Item | Detail |
|---|---|
| Date | November 23, 2026 |
| Where | FigJam, Figma Slides |
| Plans | All paid plans (free plans not mentioned) |
| Works with | Connectors (pulling context from other apps) and attachments |
| Credits | Not mentioned in the release notes or the blog post |

※ Sources: [Figma Release Notes, 2026-11-23](https://www.figma.com/release-notes/), [Figma Blog, 2026-11-23](https://www.figma.com/blog/introducing-figma-agent-in-figjam-and-slides/) (checked 2026-11-25)

The release notes name Hex, Slack and Asana as connector examples. The blog's how-to uses Notion and Google Drive. Neither says which is the full list, so check the connector picker for your own team's apps.

## In FigJam: stickies become a table

The uses Figma lists for FigJam:

- Set up brainstorming boards and build journey maps from research and data
- Group sticky notes into themes
- Turn action items into a table with owners and due dates
- Pull context such as past feedback and competitor examples from connected tools onto the board and point out patterns
- Turn feedback stickies into a draft spec

The last one leads the release notes too: a messy board becomes a spec with a summary and next steps. The post shows two people's habits. One uses Summarize under Organize. The other writes a prompt in Ask agent, asking it to summarize the board discussion as a spec covering decisions, next steps, open questions and board comments.

That prompt works as a template. Asking an agent only to "summarize" tends to return the same text, shorter. Naming the slots first (decisions, next steps, open questions) keeps them from blurring together, and the same split helps when you write meeting notes by hand.

Another user in the post, Megan Bednarczyk, prepares for crits by asking for a summary of past crit feedback, the agreed direction and the questions for the coming crit. Her point, roughly, is that there is usually a lot of context to catch up on.

## In Slides: a spec becomes a first deck

The Slides uses are more concrete:

1. Build a first-pass deck from a spec, attached material or connected context. The release notes say you can start from a spec outline plus a brand template
2. Break a script into slides. You review an outline first, then click Generate deck
3. Fill a bar chart from a spreadsheet screenshot or data you provide
4. Adapt an existing deck for another audience, shorten copy, get feedback on the story and slides, and estimate runtime from speaker notes
5. Split crowded slides, sharpen takeaways and draft speaker notes (release notes)

Number 2 stands out because there is a step in the middle. The agent shows the skeleton before it builds the deck. If you wrote the script, seeing which paragraph lands on which slide is easier to fix than ten slides arriving at once.

One user (Jarrod Barretto) described the result as an architecture, a starting point to fill in. That is the right expectation to carry. Even with a brand template, read the first version as something that still needs work.

## How it differs from the agent in design files

The agent has already [drawn strokes as strokes in icons](https://designrefs.com/articles/figma-agent-vector-icons-strokes-not-fills/), [read briefs from Google Drive](https://designrefs.com/articles/figma-agent-google-drive-connector/), and Figma published a [figure about fewer undos](https://designrefs.com/articles/figma-editing-model-undo-60-percent/). This news changes the stage, not the agent. The shared part is pulling outside context through connectors and attachments. The output differs: screens and components in design files, tables, summaries and specs in FigJam, outlines and decks in Slides.

So the chain reads like this: feedback gathered in FigJam becomes a spec, and the spec becomes the starting point of a deck. Whether the agent carries that over automatically or you attach the spec yourself is not stated. The release notes say you start from a spec outline you attach, which leans toward doing it yourself.

## What is not written yet

- **Credits**: Neither post mentions them. A help article said the design-file agent uses more credits for more complex tasks, but we could not confirm the same applies in FigJam and Slides. A third-party piece we saw said these two were credit-free during the earlier beta. Whether that holds after general availability is unknown. The help center has a separate article on optimizing AI credits
- **Free plans**: The release notes say "all paid plans." A banner on the blog page says the agent is available to all users, and nothing explains how the two fit together
- **Older help copy**: One help answer we found said the agent works only in design files. It looks older and conflicts with the November 23 notice, so we went with the notice
- **Accuracy**: Chart filling, runtime estimates and spec summaries come with no numbers in Figma's posts

## Trying it on one real meeting

Skip the grand rollout and test it on last week's meeting. Duplicate a board you used, let the agent organize it, and set the result beside your own. Three things to compare:

- How many groups differ between its themes and yours
- Whether decisions and open questions stayed apart in the spec summary
- Whether the outline from your script breaks where you would breathe

Borrow Figma's prompt shape. For boards: "Summarize this discussion as a spec with decisions, next steps, open questions and board comments." For slides: "Break this script into slides, one message per slide, so the content flows logically." The second paraphrases the post's prompt, so run it once before relying on it.

If credits matter to your team, note your balance before and after the same task. With no figures in Figma's posts, that is the only sure way to learn what one board cleanup and one deck cost.

※ Sources

- [Figma Release Notes: Figma's agent is now in FigJam and Slides (2026-11-23)](https://www.figma.com/release-notes/)
- [Figma Blog: Introducing the Figma agent in FigJam and Slides (2026-11-23)](https://www.figma.com/blog/introducing-figma-agent-in-figjam-and-slides/)
- [Figma Help Center: Figma agent section](https://help.figma.com/hc/en-us/sections/41274694599575-Figma-agent)
- [Figma Help Center: Work with the Figma agent in design files](https://help.figma.com/hc/en-us/articles/37998629035799)
