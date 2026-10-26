---
slug: artcraft-free-adobe-alternatives
title: Seven free "Photoshops" rebuilt with AI. Can designers switch?
desc: A developer is building seven free, open-source apps with AI to replace Adobe's. The Photoshop replacement opens and saves PSDs but is still in early alpha. Here's where it stands and what designers should look at.
tag: AI Design
---

A story made the rounds in design circles this week. A developer released seven free apps meant to stand in for Photoshop, Illustrator, Premiere, Lightroom, After Effects, InDesign and Acrobat. The project is called ArtCraft, and he says he built it with AI.

Headlines everywhere said you can finally cancel Adobe. I took a calm look at whether that's true and how far along it is.

These apps were reportedly built with Anthropic's Claude Opus 5.5, and this site is built with Claude Code from the same company. So I've leaned on what the repositories say and on other outlets' checks rather than the developer's claims. I haven't installed the apps myself.

## Who, why, and how

The developer is software engineer Brandon Thomas. He says Adobe's cancellation fees were the trigger. On Adobe's "annual, paid monthly" plan, canceling before the year is up costs half of the remaining amount. The US Federal Trade Commission sued Adobe over this in 2024, and the case ended in a settlement.

Here's how it's made.

- **Written with AI.** He says the code was written using Claude Opus 5.5.
- **Rebuilt from scratch in Rust.** He describes it as a "clean-room" approach: not taking Adobe's code, but rebuilding from how the tools work and look.
- **Free and open source.** Released under MIT and Apache 2.0, so anyone can download and modify it.

## Seven apps: where they stand

![The current status of ArtCraft's seven apps. Solid outlines are early alpha; dashed are in development.](https://designrefs.com/articles/img/artcraft-suite-en.svg)

Only two have reached a usable stage. PhotoCraft (Photoshop) and the Acrobat replacement are in "early alpha"; the other five are still "in development". The developer first said feature parity would come within a month, then changed that to "months, not years".

## PhotoCraft opens PSDs

PhotoCraft, the furthest along, went after what matters most to designers first: the PSD. Its repository says it can open and save 8-, 16- and 32-bit PSDs, plus PSB for large files.

![PhotoCraft opened and re-saved 309 test files, and 307 rendered correctly. The developer's own test.](https://designrefs.com/articles/img/photocraft-psd-en.svg)

Of 309 public PSD test files opened and re-saved, 307 reportedly rendered correctly. The number looks high. But it's the developer's own test, and re-saved files aren't byte-identical to the originals, because the layer records and composite are rewritten.

What's missing is clear too.

| | In PhotoCraft today |
|---|---|
| Opening and saving PSD/PSB | Works (8, 16, 32-bit) |
| Generative AI features | None |
| Tools | About 20 missing vs. Photoshop |
| Type handling | Still weak |
| Plug-ins | Not supported |
| After Effects files (AEP) | EffectCraft can't open them |
※ Sources: [PhotoCraft repository](https://github.com/storytold/photocraft), [Windows Forum](https://windowsforum.com/news/artcrafts-open-source-adobe-alternatives-on-windows-what-works-in-alpha.447649/), [Cybernews](https://cybernews.com/ai-news/ai-adobe-alternatives-open-source/). Early testers say it's nowhere near replacing real work yet.

Legal questions remain too. Even without copying code, an interface that looks too similar could raise "trade dress" issues, and commentators note Adobe holds many patents on how features work.

## What designers should watch: the file, not the app

The takeaway for designers isn't whether you can cancel Adobe today. The answer right now is clearly no. You can't hand client work to an alpha.

There are two things worth watching instead.

**First, what holds us is the file format.** Designers stay with Adobe partly because the apps are good, but also because the files we trade are PSD, AI, INDD and AEP. That's why PhotoCraft put PSD compatibility first. A replacement becomes a real threat not when it has more features, but when it can open a client's file as is and send it back as is.

**Second, the cost of building software is falling.** One person, working with AI, put out the skeleton of seven apps. The polish is far off, but there will be more attempts like this. For Adobe, pressure on pricing and cancellation terms will likely come before pressure on features. That's not bad news for designers.

## So, for now

Don't switch. Watch, and try one thing.

1. **Test with a copy of a work file.** Copy a PSD you use often and open it in PhotoCraft. See which of layers, masks, adjustment layers and type layers break, and you'll get a feel for how close it is to your work. Never overwrite the original.
2. **Recheck your subscription terms.** If you're on Adobe's "annual, paid monthly" plan, check when you can cancel and what the fee is. After the first year, you can generally cancel without a fee.
3. **Compare with existing free options.** Long-standing free tools (GIMP, Inkscape, DaVinci Resolve and others) are still far more polished. They make a good baseline before getting excited about the new thing.

How design tools are changing in the AI era is covered in [Why thirty AI drafts don't make the work any shorter](https://designrefs.com/en/articles/ai-design-tools-in-practice/), and design tools are collected under [Design tools](https://designrefs.com/en/#tool).

※ Sources: [Cybernews](https://cybernews.com/ai-news/ai-adobe-alternatives-open-source/), [GIGAZINE](https://gigazine.net/gsc_news/en/20261005-artcraft-crafting-apps/), [PhotoCraft repository](https://github.com/storytold/photocraft), [Windows Forum](https://windowsforum.com/news/artcrafts-open-source-adobe-alternatives-on-windows-what-works-in-alpha.447649/), [Softonic](https://en.softonic.com/articles/artcraft-is-now-a-seven-app-open-source-creative-cloud-alternative), [Engadget (FTC settlement)](https://www.engadget.com/big-tech/adobe-agrees-to-pay-settlement-for-making-its-subscriptions-hard-to-cancel-210336635.html).
