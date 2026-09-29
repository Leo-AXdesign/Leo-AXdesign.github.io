---
slug: open-image-model-license
title: A free image model that even does transparent backgrounds. Can you use it for work?
desc: While companies shift to cheap open models, Alibaba's new image model Qwen-Image-2.1 shut the door on commercial use. The difference between being able to download a model and being allowed to use it for work.
tag: AI Design
---

On the 28th, the Financial Times reported that corporate AI spending is shifting away from OpenAI and Anthropic toward cheap open models. The numbers make it clearer. In [Vercel's figures](https://vercel.com/blog/ai-gateway-production-index-september-2026) from its gateway that routes to many AI models, open models, the ones whose weights you can download, handled 7% of tokens last December. By August this year that was 56%, more than half for the first time.

The interesting part is the money. In the same month, open models took only 14% of the spending. Open models get the volume; closed models still make the money. It means people have started splitting the work: routine jobs go to cheap models, and only the important ones go to expensive models.

The same thing is happening with images. And right there, a problem popped up that designers can easily trip over.

**First, a disclaimer.** This isn't legal advice. License terms differ between model versions and they change. Check the original text on the model page before you actually use anything.

## Transparent backgrounds, straight out

On September 20, Alibaba released an image model called Qwen-Image-2.1. It has a few features designers will welcome.

The most striking is transparency. It produces PNGs with the background already gone. No separate cut-out step, and you can even pick out and edit just the text on a transparent layer. You can feed it up to ten reference images at once, which makes it handy for group shots, virtual try-ons and room styling drafts. The default output is 2048×2048.

It's small, too. The image generation part has 7 billion parameters and runs on a graphics card around the level of an RTX 3090. Quantized, it fits in roughly 16GB of video memory. In other words, you can run it on your own computer, for free, as much as you like.

The performance claims deserve some caution for now. The result that it beats most closed models comes from a benchmark Alibaba made itself, and there are no independent evaluations yet. Early testers said it's clearly sharper than the previous version, but noted a slight yellowish cast and missed instructions in complex compositions.

## But you can't use it for work

The problem is the license. Qwen-Image-2.1 comes with the "Qwen Research License", which limits use to research and evaluation, non-commercial only. To use it for paid work, you need separate permission from Alibaba.

There's a reason this became news. The previous versions, Qwen-Image and 2.0, were under Apache 2.0, which allows free commercial use. A model with the same name changed its terms completely with a 0.1 version bump. On Hacker News, some reactions went as far as saying it can hardly be called open anymore.

If you heard last year that "Qwen Image is fine for commercial use", that no longer holds for 2.1.

## What's mixed into the word "open"

"Open model" actually lumps together several different situations. Whether you can download it and whether you're allowed to use it for work need to be looked at separately.

| Status | Download | Commercial use | Example |
|---|---|---|---|
| Permissive license (Apache 2.0, MIT, etc.) | Yes | Yes. Mostly just keep the attribution | Ideogram 4.0 (released in June) |
| Research / non-commercial license | Yes | No. Needs separate permission | Qwen-Image-2.1 |
| Closed model | No | Depends on the terms of service | Midjourney, GPT Image |
※ Sources: [the-decoder](https://the-decoder.com/alibabas-open-weight-qwen-image-2-1-claims-to-beat-closed-models-in-image-generation-with-just-7-billion-parameters/) (Sep 20), [MIXED](https://mixed-news.com/en/qwen-image-2-1-transparent-rgba-7b-open-weights-research-licence/), [Wikipedia: Ideogram](https://en.wikipedia.org/wiki/Ideogram_(text-to-image_model)).

The first two rows look identical from the outside. Both are on Hugging Face, and both download for free. The only difference is one word in the License field on the model page.

## What if I just run it on my own computer?

It's an easy thought. If it runs on my own graphics card and never touches a server, who would know?

A license applies wherever you run the model. Whether anyone notices is a separate question. And with client work, trouble usually comes much later: months after a campaign ends, when someone asks, "How was this image made?"

One more thing. Clearing the license isn't the end of it. Whether AI output gets copyright protection, and whether it resembles someone else's character, are separate issues. I covered that in [Can you use AI-generated images in client work?](https://designrefs.com/en/articles/ai-image-commercial-use/)

## Thirty seconds before you download

When you download an open image model, there are about three places to look.

The License field, on the right side or at the bottom of the model page. If you see the words research or non-commercial there, assume you can't use it for work.

The version number. As we saw, the same model can have different terms in each version. If you got a ComfyUI workflow from someone else, check which files are actually inside it.

And a record. Write one line in the project folder: which model, which version, under which license. That line is the only thing that will let you answer the question that comes months later.

It's great that open models are getting cheaper and better. You can now run a model that does transparent backgrounds in one go on your own computer. But getting something for free and being free to use it are two different things. Image tools you can use commercially are listed under [AI tools](https://designrefs.com/en/#ai).
