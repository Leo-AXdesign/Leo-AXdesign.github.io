---
slug: figma-make-payload-save-button
title: When the Save button saves nothing: what to check in Payload, now inside Figma Make
desc: On October 15, Figma put the open-source CMS Payload inside Figma Make. Prompting an app now also sets up a database, file storage, user login and an admin panel. Checked against Figma's blog and release notes: what it does, hosting in free beta with pricing TBA, and what is still unknown.
tag: AI Design
---

The mockup looks right. There is a list of posts, product cards, and a Save button. But press it, refresh, and everything is gone. The screen has nowhere to keep data.

Filling that gap used to mean connecting a separate backend: the part behind the screen that stores data and handles login. On October 15, Figma announced on its official blog that Payload is now inside Figma Make. This piece repeats only what I verified on that post and Figma's release notes.

![Figma blog 'Create, ship, and manage data-backed websites with Payload in Figma'. Source: figma.com/blog/websites-with-payload-in-figma (captured 2026-10-22)](https://designrefs.com/articles/img/figma-make-payload-save-button-shot1.webp)
## Before you read

- I did not run Payload in Figma Make for this piece. Everything below is what Figma's blog and release notes say.
- The help article Figma points to ("Add a backend to a functional prototype or web app") would not open for me, so I could not check it.
- The post gives no usage limits, storage caps or rate limits.
- It also does not say whether Figma-hosted projects can be exported or self-hosted.
- Access rolls out to all accounts over several weeks, so it may not be visible in yours yet.

## What the post promises

Payload is an open-source headless CMS: a content-management tool kept separate from the screen. It joined Figma and now lives inside Figma Make. The post is by Figma's James Mikrut, dated October 15, 2026.

As described:

- When you prompt an app with content-management features in Figma Make, it sets up a database, file storage, user login and an admin panel.
- Figma hosts it. The pitch is that design, content and data live in one place.
- You can upload a CSV and ask the agent to create a collection from it. The post's example is adding catalog entries in bulk.
- API keys can be stored in Make's settings. Figma keeps them securely and they are not exposed to visitors once the site is published. Before this, the post says, you had to set up and connect a Supabase project.
- On a published site, add /admin to the address to reach the admin panel.

## Each role gets a different door

| Role | What the post says they do |
|---|---|
| Designers | Prompt experiences using real content |
| Marketers | Create articles, edit copy, tag, swap media, reorder categories, review versions and publish in the admin panel |
| Developers | Customize the app with Payload's open-source framework |

※ Source: [Figma blog: Payload in Figma](https://www.figma.com/blog/websites-with-payload-in-figma/). Summary of Figma's own description.

Each role gets a workspace, and there are granular permissions to control who can change what. The post does not say which permission levels exist.

What stands out for designers is the first line: start from real content, not lorem ipsum. That reading is mine.

## Price and timing: free now, pricing later

From Figma's release notes and blog:

- Payload is available on all plans. Access rolls out to all accounts over the coming weeks.
- Hosting for Payload-backed Figma Make projects is currently in beta and free to use.
- Figma says it will announce pricing and packaging before it takes effect. No amount or date is given.

"Free" comes with "for now." If the site is for a client, settle in advance who pays when a fee appears. That is my opinion.

To avoid mixing up news from the same week: the free window for code layers is separate from Payload. We covered the agent starting to use AI credits in [Figma's agent started charging credits](https://designrefs.com/articles/figma-agent-ai-credits-ga/).

## What we can't know yet

- **Getting data out.** The post does not say whether Figma-hosted projects can be exported or self-hosted. It points to Payload.org for self-hosting or extending, which reads as being about the open-source project, not Figma-hosted apps.
- **Limits.** No storage, request or user caps are listed.
- **Login method.** The post says user login is set up, but I found no detail on the method (email, social sign-in and so on).
- **Real-world quality.** That one prompt yields a usable admin panel is Figma's description. Your project is the test.
- **Independent checks.** None of the sources I opened was a third-party test of Payload in Figma.

## What this means for designers

For screens whose content changes, such as a portfolio or a small shop site, the distance between mockup and live site shrinks. Client jobs that need an admin panel for editing copy fall in this range too.

For vibe coders, it removes the step of shopping for a database and login separately. It does not fix the problem of AI-made screens all looking alike. Choosing fonts and colors still comes first.

One worry is responsibility. When you only draw screens, a mistake means redrawing. Once login and data are attached, privacy and backups follow. Think first about whose data the site collects. That is also my opinion.

We covered the related Figma flow in [Figma Specs: handing context to your team and AI in one Markdown page](https://designrefs.com/articles/figma-specs-markdown-context/). Payload adds data on top of that.

## So for now

**Start with ten real rows.** Put ten real product names or post titles in a CSV, upload it and have a collection created. It is the method the post shows, and you see at once how real text changes the screen.

**For client work, write down the hosting terms.** It is free beta now but pricing is unset. Note who pays when a fee appears and how the data would move.

**Pause before collecting personal data.** If you accept user logins, list what you store, and check limits and export options in the help center before going live.

AI design tools such as Figma Make are grouped by use in [AI design tools](https://designrefs.com/ai/).

※ Sources: [Figma blog: Payload in Figma](https://www.figma.com/blog/websites-with-payload-in-figma/), [Figma release notes (Releasebot)](https://releasebot.io/updates/figma).
