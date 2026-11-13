---
slug: figma-editing-model-undo-60-percent
title: Figma says undo clicks on its agent dropped 60%. What the number does and doesn't tell you
desc: On October 29 Figma published how it trains its own editing model, plus post-launch numbers for its agent: 20% faster, 33% higher ratings, 60% fewer undos. We read what each figure is measured against, what the 62% match-or-beat rate leaves out, and what the post doesn't say.
tag: AI Design
---

Ask an agent to tidy the spacing, look at the result, and sometimes you hit Cmd+Z right away. Once is fine. By the third undo on the same screen, you start calculating that fixing it by hand would have been faster.

Figma's October 29 blog post includes exactly this undo number. It is written by the people who build the agent, about how they trained their own model, and it compares the agent's beta with its generally available version. The author is Josh Clemm, Figma's VP of software engineering.

![Figma blog post 'How we're training a Figma-fluent editing model' (source: https://www.figma.com/blog/training-a-figma-fluent-editing-model/, captured 2026-11-04)](https://designrefs.com/articles/img/figma-editing-model-undo-60-percent-shot1.webp)
This piece is built from Figma's post itself and one explainer (FourWeekMBA). Every figure below is Figma's own measurement, and none of it was checked by using the agent.

## One model just for editing

According to the post, Figma splits the work inside its agent across models. Precise, iterative edits to what is already on the canvas go to its own editing model: adjusting spacing, changing colors, reworking a layout. Image generation, vectors and new design explorations go to leading third-party models.

The post names two goals: be better at design, and be faster at those edits, because slow edits interrupt a designer's flow.

It also says where things stood at the start. When the work began, frontier models could not understand Figma's file syntax. Another reason was cost: asking an outside model to take long instructions every time burns many tokens. No cost figure accompanies that.

## The first model: 250,000 examples

Training has two stages. The first is imitation learning. Each example has three parts:

- a starting design
- an edit request (synthetic)
- a successful edit that fulfils the request

All of it is in Figma's native file format. Larger teacher models proposed the edits, and deterministic validators plus visual model judges filtered them. A step let the pipeline revise edits using evaluator feedback.

Figma says an earlier model, based on Llama 3.3 70B and trained on more than 250,000 examples, became competitive with top models of the time on editing tasks. That is the only training-size number in the post. Example counts for later models and for the reinforcement-learning stage are not given.

## Where imitation runs out, and why reinforcement learning follows

The post states the weakness of imitation learning plainly. The model learns to produce designs very close to what it saw, it generalizes less well, and it is less efficient with examples.

So the latest recipe adds reinforcement learning: the model gets a score for its result and is trained toward higher scores. Figma says it is working on design-specific training environments, more varied examples, shaping the reward model, and criteria written by experts. No reinforcement-learning results are reported. The post describes it as ongoing work.

The base models changed too. After Llama 3.3 70B, the post mentions Qwen models, Muse Spark Open, Inkling and others, and its evaluation chart refers to a model post-trained on Qwen 3.8 27B. Which of these runs in the agent today is not specified.

## Five numbers after general availability

The agent opened to all users earlier in the same month. The post compares the beta agent with the current one:

| Item | Change Figma reports | What to keep in mind |
|---|---|---|
| Task speed | Typical tasks about 20% faster | "About"; task mix not disclosed |
| Expert designer comparison | Beats or matches the previous agent 62% of the time | The other 38% is where it did worse |
| User ratings | 33% higher | Scale and number of responses not disclosed |
| Undo | Users undo the agent's work 60% less often | Baseline undo count not disclosed |
| Share of own model | Work powered by Figma's model more than doubled | Share of total not disclosed |

※ Source: [Figma Blog, How we're training a Figma-fluent editing model](https://www.figma.com/blog/training-a-figma-fluent-editing-model/) (published 2026-10-29, checked 2026-11-04). The comparison in every row is against the previous beta agent.

Cost is mentioned only as lower average cost per message, with no amount or percentage. The post also says the gains come from models, tools and the harness together, not from the editing model alone.

## Reading "60% fewer undos" against your own work

The post does not say whether the 60% compares the same users doing the same tasks. Beta users and post-launch users may be different people, and the kind of work they hand to the agent may have changed.

There is a second way to read it. Undo count is a proxy for "I didn't like that result," but not having undone something doesn't mean it was accepted as is. Someone who keeps a slightly-off result and finishes it by hand never presses undo, and that case doesn't show up in the number.

The 62% needs the same treatment. Expert designers judged the new agent equal or better 62% of the time, which leaves 38% where the new one did worse. That doesn't make the new version bad. But "better overall" and "in nearly four cases out of ten, the new one did worse" come from the same figure.

## Set beside Canva's Brush, announced the same day

Canva announced Brush, its own model for editing existing designs, the same day. We covered it in [our Canva Brush article](https://designrefs.com/articles/canva-brush-edit-existing-design/). One explainer (FourWeekMBA) calculated that the two announcements were posted 34 minutes apart and that neither mentions the other. That gap is the writer's arithmetic, not something I verified.

The two companies disclosed opposite things.

| | Figma | Canva Brush |
|---|---|---|
| Disclosed | Training method, earlier model's example count (250,000+) | Up to 69% faster, 46% cheaper per edit |
| Compared against | Its own beta agent | Its own previous design agent |
| Left out | Current base model, cost figure | Training data size, measurement conditions |

※ Sources: [Figma Blog](https://www.figma.com/blog/training-a-figma-fluent-editing-model/), [FourWeekMBA](https://fourweekmba.com/ai-figma-trained-llama-on-250000-examples-as-canva-ships-brush/); Canva figures follow the reports summarized in [our Brush article](https://designrefs.com/articles/canva-brush-edit-existing-design/).

Both compare against their own earlier version rather than an outside frontier model. So "Figma is faster" or "Canva is cheaper" cannot be concluded. That would take running both tools on the same file.

One chart in the post deserves a note. It shows an unreleased Figma model, "Figma design edits v3," at 77.8% next to a model called "Sol 6.1" at 76.9%. What the metric measures, how many tasks it covers, and the error margin are not stated. A 0.9-point gap means little without that. The post itself calls the evaluation one input among many for choosing models.

## What is still missing

Things I could not confirm from what I read:

- Which requests go to Figma's own editing model and which are handed to third-party models
- Whether credit use differs between the two. Credits are covered in [our Figma agent credits article](https://designrefs.com/articles/figma-agent-ai-credits-ga/), but model-by-model differences are not in that piece either
- The sample size and period behind the 60% undo reduction
- How well it follows Korean instructions
- Whether users' own files are used in training. The post mentions synthetic examples and expert-written criteria, not user files

## Three things to try next week

**Count your own undos.** For a week, note each edit you hand to the agent and each undo in a notes app with tally marks. That is the only way to learn whether Figma's 60% holds for your files. A week of data also shows which kinds of requests get undone.

**Keep edit requests narrow and say what to leave alone.** The editing model is described as built for "fixing," so limit the scope of the request. The line below is an example I have not tried.

`Only fix the vertical spacing in this card list to an 8px grid. Leave colors, type and images as they are.`

**Hand the agent your rules first.** Figma also posted a piece on October 23 about putting a design system to work with the agent. When color and type-size rules live in the file, a request like "just fix the spacing" is less likely to bring in stray colors. I did not read that post; if you need it, find it in the Figma blog index.

That the agent got better and that it got better on your file are different statements. Figma's numbers speak to the first. A week of undo tallies speaks to the second.

※ Sources

- [Figma Blog: How we're training a Figma-fluent editing model](https://www.figma.com/blog/training-a-figma-fluent-editing-model/) (2026-10-29)
- [FourWeekMBA: Figma Trained Llama on 250,000 Examples as Canva Ships Brush](https://fourweekmba.com/ai-figma-trained-llama-on-250000-examples-as-canva-ships-brush/)
- [Figma Blog index](https://www.figma.com/blog/) (post dates checked 2026-11-04)
