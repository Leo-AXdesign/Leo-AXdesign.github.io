---
slug: chatgpt-intelligent-ui-figma-agent
title: The week AI started drawing screens. Who holds the design rules?
desc: ChatGPT now answers with buttons and charts, and the Figma agent is out of beta. Two features from the same week, side by side, with diagrams on who sets the rules for the screen.
tag: AI Design
---

This week brought two announcements in a row about AI drawing screens.

On October 6, Figma took its design agent out of beta. The next day, OpenAI brought GPT-6 to ChatGPT and introduced "Intelligent UI": instead of answering only in text, ChatGPT can answer with a screen that includes buttons, forms and charts. It opened to paid users first, and reaches free users starting today.

One lives in a chat window, the other inside a design tool. Different places, but in both, AI draws the screen itself. Which raises the same question: who sets the rules for that screen?

**First, a disclaimer.** Both features are only days old, so there are almost no hands-on reviews yet. This is based on the companies' announcements and coverage. I'll also note that I'm building this site with Claude Code.

## Answers arrive as screens

OpenAI's description: GPT-6 composes answers from text, visuals and interactive elements, and decides how to lay them out for each question. Comparisons sit side by side, explanations become diagrams you can play with, and simple questions still get plain text.

OpenAI's examples: a cooking timeline next to a recipe, road-trip stops on a map, and small tools built on the spot. A savings calculator, a bill splitter, even a game you can play inside the chat.

![The same question answered in text and as an interface. An illustration; actual answers may differ.](https://designrefs.com/articles/img/intelligent-ui-answer-en.svg)

Turn it into a designer's question and it clicks. Ask "how much should I charge per hour for freelance work?" and you used to get a few paragraphs. Now you might get sliders for hours and rate, with the estimate calculated next to them. The illustration above was drawn to show that difference.

OpenAI also shared how it works. There's a library of components OpenAI built in advance, and the model renders them onto the screen while it's still writing the answer. It doesn't wait to finish thinking; it fills in the screen as it goes. OpenAI says the model checks the interfaces it makes for clarity, usefulness and completeness, while admitting that improving its design judgment is still a work in progress.

Here's who can use it:

| | Details |
|---|---|
| Paid (Plus · Pro · Business · Enterprise) | From Oct 7, in the Chat tab |
| Free · Go | From Oct 8 |
| Not supported | Pro's thinking mode, outdated desktop apps |
| How to turn it off | "Layout and visuals" in web settings; some visuals may still appear |
※ Sources: [OpenAI, GPT-6 and Intelligent UI for everyone](https://openai.com/index/gpt-6-for-everyone/), [9to5Mac](https://9to5mac.com/2026/10/07/openai-brings-gpt-6-to-chatgpt-and-debuts-intelligent-ui/), [Relevant Audience](https://relevantaudience.com/ai/gpt-6-intelligent-ui-chatgpt-answers). Press reports say paid plans run on GPT-6 Sol and free plans on GPT-6 Luna.

## The same week, the Figma agent left beta

Figma's announcement came a day earlier. According to its October 6 release notes, the design agent is now generally available. It's faster, and you can search for Figma files and attach them during a chat. You can also watch an agent working on a teammate's request live on the canvas.

The part designers should notice is "library guidelines". You upload markdown files to a design library with rules, best practices and antipatterns, and the agent reads them every time someone prompts with that library enabled.

The free ride is over, though. From October 6, the agent uses AI credits, drawn from the same pool as Figma Make. There's no fixed price per request. Figma only says usage depends on how complex the prompt is, how many actions the agent takes and how much context you attach, like libraries or files. The agent in FigJam and Slides is still in closed beta and doesn't use credits.

## Who holds the rules?

Put the two side by side and the difference is clear.

![ChatGPT Intelligent UI builds screens from OpenAI's components; the Figma agent reads your team's library and guidelines.](https://designrefs.com/articles/img/ui-rules-owner-en.svg)

The screens ChatGPT draws are made of OpenAI's components. Whoever asks, the buttons and charts look the same. The announcement said nothing about other companies bringing their own components or design rules. OpenAI owns the rules.

The Figma agent is the opposite. It uses components your team made and reads guidelines your team wrote. Your team owns the rules. And those rules fit in a single markdown file, the same idea as [DESIGN.md](https://designrefs.com/en/articles/design-md-for-ai/), which I covered last week. If you want AI to do the work, you have to write the rules down in a form AI can read.

## What's left for designers

**Judging when a screen beats text.** OpenAI says the model decides the format for each question. That judgment is what UI designers do every day: a calculator, a table, or one sentence? OpenAI says this is still being improved, so for now a person's eye is better.

**Writing the rules down.** If you'll use the Figma agent, start with library guidelines. They don't need to be long. Five lines of don'ts is enough: one accent color per screen, body text never below 16px, shadows only on cards. If you already have a DESIGN.md, carry the same content over.

**Watching credits for a month.** More complex requests and more attached files cost more credits. For the first month, attach only what you need instead of a whole library, and count how fast the credits go.

There will only be more screens drawn by AI. Which rules they follow will come down to who writes those rules down first. AI tools by use case are under [AI tools](https://designrefs.com/en/#ai), and design system references under [Design & Code](https://designrefs.com/en/#dev).

※ Sources: [OpenAI](https://openai.com/index/gpt-6-for-everyone/) (Oct 7), [Figma release notes](https://www.figma.com/release-notes/) (Oct 6), [FourWeekMBA](https://fourweekmba.com/ai-figma-design-agent-leaves-beta-now-draws-ai-credits/), [9to5Mac](https://9to5mac.com/2026/10/07/openai-brings-gpt-6-to-chatgpt-and-debuts-intelligent-ui/), [Relevant Audience](https://relevantaudience.com/ai/gpt-6-intelligent-ui-chatgpt-answers).
