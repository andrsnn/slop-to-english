---
name: slop-to-english
description: Rewrite text (slides, docs, READMEs, replies, copy) so a person can read it aloud and the listener knows what it claims. Removes opaque phrases first (figurative verbs, abstract nouns with no referent, slogans, meta-flourishes), then the classic LLM tells (not X but Y, triads, punchline dashes, AI vocabulary). Technical terms and numbers stay. Use when asked to de-slop, de-LLM, humanize, or "make it sound like a person", or when text is convoluted or slogan-y.
---

# slop-to-english

Text written by a language model often sounds like a poster instead of a person. Rewrite it so
each line states a fact a listener can repeat back. Technical terms are fine (LoRA, cache hit,
p99, MAU). The target is phrasing that does not say anything you can point at.

## The test

Say the line out loud to someone across a table. Then ask: **what happened, who did it, what number?**
If the listener would ask "what does that mean?", the line is opaque. Rewrite it as the literal fact.

## Tier 1: opaque phrases (fix these first, they are the most common)

An opaque phrase sounds meaningful but has no literal meaning. The reader cannot say what it claims.

| Type | Examples | Why it fails |
|---|---|---|
| **Figurative verb** | "The pose finally lands." "The model finally clicked." "The pipeline breathes." "The build flies." | Nothing lands, clicks, breathes or flies. What was measured? |
| **Abstract noun with no referent** | "The habit behind the fleet." "Foundation for velocity." "Engine of growth." "Momentum." "North star." "In our DNA." | The noun points at nothing. Which habit? What foundation? |
| **Slogan** | "The machine is the manager." "Proof over claims." "Owning the stack." "Ship fast, learn faster." "Data beats opinions." | A poster line. It hides the actual rule or number. |
| **Meta-flourish** | "An agent writing about agents." "Written by the thing it describes." "A story told in commits." "The numbers tell the story." | Talks about the text instead of saying something. |
| **Idiom standing in for a number** | "Moved the needle." "Low-hanging fruit." "Hit the ground running." "A game of inches." | Hides how much, how long, or how many. |

How to fix a Tier 1 phrase:

1. Find the literal fact behind it: who did what, with which number, tool, or name.
2. Use the numbers and names around the phrase. The fact is usually in the next sentence.
3. If the text never says what the phrase refers to, do not guess. Keep only the facts that are there. If nothing concrete is left, cut the line.
4. If you can ask the author, ask one question: "What does 'X' mean here?"
5. Do not swap one figure of speech for another. "The joints end up where I put them" is still a metaphor. Say what the model does: "The model draws the reference image according to the skeleton pose provided."
6. Name what goes in and what comes out. "The pose finally lands" says neither. "The model draws the reference image according to the skeleton pose provided" names the input and the action.

## Tier 2: the classic tells

Fix these too, after Tier 1.

- **"Not X, but Y"** and "It isn't about A, it's about B." Say the Y and stop.
- **Triads and balanced counts** written for rhythm. "Speed, reliability, and scalability." "Three ways to X, one way to Y."
- **Punchline em-dashes** and dash chains. One dash per paragraph at most.
- **AI vocabulary.** delve, tapestry, testament, landscape, realm, intricate, pivotal, crucial, underscore, showcase.
- **Buzzword verbs.** leverage, unlock, elevate, streamline, harness, empower, seamless, robust.
- **Sycophantic openers.** "Great question!" "What a fascinating point!"
- **Filler signposts.** "It's worth noting that", "Let's dive in", "Here's the thing", "In conclusion".
- **Scene-setters.** "In today's fast-paced world", "In an era of unprecedented change".
- **Grandiose closers.** "This will reshape the future of ..."
- **Significance inflation and puffery.** "A pivotal moment", "nestled in the heart of", "vibrant", "rich tapestry".
- **Copula avoidance.** "Serves as", "stands as", "boasts" where "is" or "has" works.
- **Vague attribution.** "Experts agree", "studies show", with no name.
- **Staccato questions.** "The result? Devastating."
- **Symbols a speaker cannot say.** ~, →, ✓, ✗, "e2e 23/23", "v28a→v33". Write the words.

## How to rewrite

- **Say the literal fact with the number.** Subject, verb, object. Short sentences. Someone does something.
- **Keep every real number, name and technical term.** Change how they are said, not what is said.
- **Do not invent.** Never add a number, name, or claim that is not in the source. If a phrase has no fact behind it, cut it.
- **Do not write "X, not Y" in your rewrite.** Say the X.
- **Keep the author's voice.** First person stays first person. No added warmth, jokes, or praise.
- **Match the length limit** if one is given (slides: usually under 150 characters).
- **Leave plain lines alone.** If a line already passes the test, return it unchanged.

## Before and after

Tier 1 first. These are real drafts from a slide deck written by a local model.

| Type | Before | After |
|---|---|---|
| Abstract noun | Owning the stack. | I started running my own models. |
| Abstract noun | Foundation for velocity: 3 quarters of test-suite investment. | We spent 3 quarters on the test suite. |
| Meta-flourish | An agent writing about agents. | A local Qwen model wrote this deck. |
| Meta-flourish | This deck was written by the thing it describes. | A local model wrote the first draft. |
| Meta-flourish | A story told in commits: 1,204 of them across 5 repos. | 1,204 commits across 5 repos. |
| Slogan | The machine is the manager. | A failing test blocks the commit. |
| Slogan | Proof over claims. | Reviewers only see the code and the test results. |
| Slogan | Nobody trains on bad data. A human signs off first. | I review every training record before it's used. |
| Slogan | The API bill is now zero. | I run the models on my own hardware, so there are no API fees. |
| Figurative verb | The pose finally lands. | The model draws the reference image according to the skeleton pose provided. |
| Figurative verb | The model finally clicked at epoch 14, hitting 91% accuracy. | The model reached 91% accuracy at epoch 14. |
| Idiom | We moved the needle on churn: 5.1% down to 3.4%. | Churn fell from 5.1% to 3.4%. |
| Vague claim | Four months, each one a step up. | Commits rose from 777 in June to 1,855 in August. |
| Symbols | 23/23 e2e | All 23 end-to-end tests pass |
| Not X but Y | Our cache isn't just a speed boost, it's a rethinking of how Redis 7.2 serves 12,000 requests per second. | The new cache runs on Redis 7.2 and serves 12,000 requests per second. |
| Triad | Speed, reliability, and scalability through 3 regional data centers. | The platform runs in 3 regional data centers. |
| Sycophantic opener | Great question! You're absolutely right to ask. The default timeout is 30 seconds. | The default timeout is 30 seconds. |

More in `EXAMPLES.md` and `evals/cases.jsonl`.

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
