---
name: slop-to-english
description: Rewrite text (slides, docs, READMEs, replies, copy) so a person can read it aloud and the listener knows what it claims. Removes opaque phrases first (figurative verbs, abstract nouns with no referent, slogans, meta-flourishes), then the classic LLM tells (not X but Y, triads, punchline dashes, AI vocabulary). Technical terms and numbers stay. Every line must be something a person would say out loud and must make sense out of context. Mandatory for player-facing or published copy (narration, in-game text, UI text, slides, READMEs). Use when asked to de-slop, de-LLM, humanize, or "make it sound like a person", or when text is convoluted or slogan-y.
---

# slop-to-english

Text written by a language model often sounds like a poster instead of a person. Rewrite it so
each line states a fact a listener can repeat back. Technical terms are fine (LoRA, cache hit,
p99, MAU). The target is phrasing that does not say anything you can point at.

## The test: would a person say this out loud?

Say the line out loud, once, to a friend across a table who has seen nothing else. Then ask:
**what happened, who did it, what number?** If the friend would stop you to ask "what does that mean?",
"who did that?", "of what?" or "which one?", the line fails. Every line has to pass on its own, out of
context: narration, in-game text, UI text, slides and READMEs alike. Less text is better. Cut a line
that adds nothing before you try to fix it.

This is the rule broken most often. These are the shapes that break it. The lines are made up; each
copies a real failure.

| Shape | Line that fails | What a person says |
|---|---|---|
| A thing acts like a person | Then I found the oven settings were trusting the old recipe too. | Then I found the oven settings came from the old recipe too. |
| No one does the action | The shelf was cut for a narrower wall. | I cut the shelf for a narrower wall. |
| A word points at something never named | Now a small script cleans up whenever those runs leave temp files. | Now a small script deletes the temp files the nightly build leaves behind. |
| A dropped noun or unit | Each field makes one more every day. | Each field grows one more crop every day. |
| A clause that lands on the wrong noun | So there's a checklist of the steps that every new hire is told to read. | So there's a checklist of the steps, and every new hire is told to read it. |
| Stacked hedges in a README | Budget roughly several hours on one big graphics card. | Expect it to take several hours on one big graphics card. |
| Poster shorthand | If sync fails, retry app first. | If syncing fails, restart the app and try again. |
| Figurative verb | Support for the old format quietly evaporated. | We removed support for the old format. |
| A joke you decode in two steps | Your parcel flew in one second! The pilot got half. | Your parcel is here! It's a little bent. |
| A joke that explains itself | You crashed! We added ads. Removing them costs more than the car. | You crashed! Please enjoy this ad. |

If `private/REAL-EXAMPLES.md` exists in this skill's folder, read it too: it holds the owner's real failures
and the fixes they accepted.

For a joke, the thing on screen does the joke: name it and add one short, plain reaction. Never explain
the joke. Under 10 words is best.

Swapping one word is not the fix. Say the line again from scratch, the way you would say it to the friend.

## Process

1. Read the whole text. Note the numbers and technical terms that must survive.
2. Flag each line that fails the test. Tier 1 first.
3. Rewrite only flagged lines. Leave the rest.
4. Read the result out loud in your head. Fix anything you would stumble on or feel silly saying.
5. Return the rewrite. If asked for a review only, return each flagged line with its replacement and do not edit files. If told to edit files, edit in place and list what changed.

## Do not

- Do not use the phrases this skill flags, in the rewrite or in your reply.
- Do not add praise, headings, or commentary the user did not ask for.
- Do not widen scope. Fix wording only. Do not restructure, reorder, or add content unless asked.
