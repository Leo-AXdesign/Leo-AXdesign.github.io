---
slug: macos-27-ai-off-switch
title: The switch to turn off Mac AI all at once is gone. An off button is design too
desc: macOS 27 removed the switch that turned off Apple Intelligence entirely. Users are building outside tools to strip AI out. What changed, what to check on a designer's Mac, and the question left for anyone designing AI features.
tag: AI Design
---

A tool spread quietly among Mac users this week. It's called RemoveMacAI. It turns off Apple's AI features on a Mac and deletes the model files they use. Several people reported getting back more than 12GB of storage.

There's a reason a tool like this appeared. In macOS 27, released this fall, the switch that turned off all AI features at once is gone.

**First, a disclaimer.** I haven't run this tool on macOS 27 myself. What follows is based on reporting from Mac-focused outlets. Apple hasn't explained why it removed the switch.

## What changed

![In macOS 26, one switch turned off every AI feature; in macOS 27, each feature has to be turned off separately. A sketch based on reports.](https://designrefs.com/articles/img/macos27-ai-switch-en.svg)

Through macOS 26, there was a switch for all of Apple Intelligence. Flip it, and Writing Tools, Genmoji, Image Playground and the rest turned off, and the model files were removed.

In macOS 27, that switch is gone. You have to find and turn off each feature, and reports say the toggles are spread across several settings screens, about a dozen in all. The bigger difference is that turning them off leaves the model files in place. By Apple's own figure, that's up to 14GB on Macs with M3 or later.

RemoveMacAI fills the gap. Using a configuration-profile mechanism Apple provides for organizations, it turns features off, deletes the models and blocks them from downloading again. The developer says it doesn't touch system files directly and can be reversed. It's not a method Apple officially recommends, though.

## What to check on a designer's Mac

There are two reasons designers shouldn't just skip past this.

**Storage.** A designer's Mac is always short on space. A few PSDs and some video sources fill it fast. Unused AI models taking 14GB is a size worth noticing.

**Client material.** Writing Tools rewrites selected text, and the ChatGPT extension can send content to an outside service. If you handle contracts or pre-launch material, you should at least know which features are on.

| What to check | Where | Why |
|---|---|---|
| Writing Tools | System Settings > Apple Intelligence & Siri | So you don't use it on client documents by accident |
| ChatGPT extension | Same place | A path for content to reach an outside service |
| Image Playground, Genmoji | Same place (also check Screen Time) | Turn off if unused |
| Space used by models | System Settings > General > Storage | See how big the leftover model files are |
※ Sources: [MacRumors](https://www.macrumors.com/2026/10/06/strip-apple-intelligence-from-macos-27/), [Digital Trends](https://www.digitaltrends.com/computing/macos-27-removed-the-apple-intelligence-off-switch-heres-how-to-get-rid-of-it-anyway/), [Futurism](https://futurism.com/artificial-intelligence/mac-users-nuking-every-trace-of-apple-ai). Menu names and locations may vary by macOS version.

Using an outside tool to delete the models is your call. On a work Mac, talk to IT first; configuration profiles can clash with company management settings.

## An off button is design too

This doesn't end with Mac settings. Many designers are now putting AI features into their own products. So the same question sits in front of us: when a user wants to turn this off, can they do it easily?

Apple's choice is a useful cautionary example.

- **One step to turn on, ten to turn off.** It's on by default, and turning it off means visiting several screens. Users read that as "please don't turn this off."
- **What stays after you turn it off.** If files remain after a feature is off, users don't trust that it's really off. So they go looking for outside tools.
- **Changes without explanation.** When a switch disappears with no reason given, people assume the worst.

Do the opposite. If you design AI features, put the off controls in one place, and tell users in one line what turns off and what remains. If you change a feature, say why. If users start looking for outside tools, that's a sign the settings screen's design has failed.

## So, for now

1. **Start with your own Mac.** Use the table above to see which AI features are on and how much space the models use. Turn off what you don't use.
2. **Ask the same of what you build.** For the AI feature you're working on, find where "off" is and count how many taps it takes. More than three is worth another look.
3. **Change with a reason.** If you need to change or remove a setting, write the reason down, even as one line in the release notes.

Who sets the rules when AI draws the interface is covered in [the week AI started drawing screens](https://designrefs.com/en/articles/chatgpt-intelligent-ui-figma-agent/), and UI references are under [UI/UX references](https://designrefs.com/en/#uiux).

※ Sources: [Futurism](https://futurism.com/artificial-intelligence/mac-users-nuking-every-trace-of-apple-ai), [MacRumors](https://www.macrumors.com/2026/10/06/strip-apple-intelligence-from-macos-27/), [MacRumors (storage)](https://www.macrumors.com/2026/10/05/apple-intelligence-removal-tool-frees-mac-storage/), [Digital Trends](https://www.digitaltrends.com/computing/macos-27-removed-the-apple-intelligence-off-switch-heres-how-to-get-rid-of-it-anyway/), [Daring Fireball](https://daringfireball.net/linked/2026/10/06/cli-tool-removes-apple-intelligence-from-macos-27).
