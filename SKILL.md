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
| **Figurative verb** | "The pose finally lands." "The model finally clicked." "The pipeline breathes." "The build flies." "The cracks the org chart misses." | Nothing lands, clicks, breathes or flies. What was measured? |
| **Abstract noun with no referent** | "The habit behind the fleet." "Foundation for velocity." "Engine of growth." "Momentum." "North star." "In our DNA." | The noun points at nothing. Which habit? What foundation? |
| **Slogan** | "The machine is the manager." "Proof over claims." "Owning the stack." "Ship fast, learn faster." "Data beats opinions." | A poster line. It hides the actual rule or number. |
| **Meta-flourish** | "An agent writing about agents." "Written by the thing it describes." "A story told in commits." "The numbers tell the story." | Talks about the text instead of saying something. |
| **Idiom standing in for a number** | "Moved the needle." "Low-hanging fruit." "Hit the ground running." "A game of inches." | Hides how much, how long, or how many. |
| **Inverted sentence** | "With no hires, one item stays on plan and three wait." "Without a baseline, no target can be promised." | The condition comes first and no person acts. Who does what, and how much? See "Inverted sentences" below. |
| **Riddle title** | "Three things I defer, and what starts each one." "Two inputs, one output, three outcomes." | Every noun is a placeholder. The title describes the slide and never names the subject. What is the slide about? See "Riddle titles" below. |

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
| Figurative verb | Listen to operators. They see the cracks the org chart misses first. | Ask the people who run day-to-day operations, like support and sales. They notice problems before anyone else does. |
| Figurative verb | The model finally clicked at epoch 14, hitting 91% accuracy. | The model reached 91% accuracy at epoch 14. |
| Idiom | We moved the needle on churn: 5.1% down to 3.4%. | Churn fell from 5.1% to 3.4%. |
| Vague claim | Four months, each one a step up. | Commits rose from 777 in June to 1,855 in August. |
| Symbols | 23/23 e2e | All 23 end-to-end tests pass |
| Not X but Y | Our cache isn't just a speed boost, it's a rethinking of how Redis 7.2 serves 12,000 requests per second. | The new cache runs on Redis 7.2 and serves 12,000 requests per second. |
| Triad | Speed, reliability, and scalability through 3 regional data centers. | The platform runs in 3 regional data centers. |
| Sycophantic opener | Great question! You're absolutely right to ask. The default timeout is 30 seconds. | The default timeout is 30 seconds. |

More in `EXAMPLES.md` and `evals/cases.jsonl`.

## Messages to a customer or user

When the text is an email or reply to a real user, these rules come from an author rewriting a
drafted customer email by hand. They win over the plain-fact rules above where the two conflict.

- **First person singular** when one person runs the product. "I just added", never "we built" or "our team shipped".
- **Warm, short opener, then straight to the fixes.** "Thank you for taking the time to write this. It's really helpful. I totally hear you on all fronts." Do not restate the customer's problem back to them in detail; they know it.
- **Humble, casual tone is fine.** "hopefully will help!" and one exclamation mark are allowed. Stiff certainty ("So we built a fix this week.") is not.
- **Tie each feature to their complaint.** Say which problem a feature answers ("which should help with the inconsistency issue you mentioned. It's intended for exactly that.").
- **Add the practical hint they need to use it.** "Your editor should do this automatically if you tell it."
- **Structure:** thanks, what I added (one bullet per feature), how to use it, what to expect, "your current setup keeps working", thanks again.
- **No closing homework question** unless the reply truly needs an answer from them.
- **Drop internal detail:** no version numbers, no engine or model names, no setup jargon beyond one line.

| Draft | Author's edit |
|---|---|
| I totally hear you: digging through your project for the master image and re-uploading it... shouldn't be your job. So we built a fix this week. | I totally hear you on all fronts. I just added in a few fixes and improvements that hopefully will help! |
| What we built | What I just added |
| ...no upload. | ...no upload. Your editor should do this automatically if you tell it. |
| ...creatures get their own animations. | ...creatures get their own animations. You can pose each frame with a skeleton, which should help with the inconsistency issue you mentioned. It's intended for exactly that. |
| What were you animating when that happened? I'd like to fix that next. | (removed) |

## Slide titles

A slide title is a full sentence with a subject and a verb. It states who does what, with the number.
Use first person when the speaker does the action. These title failures come from a 90-day plan deck:

- **Figurative verb.** "feeds", "runs on", "becomes". Name the action a person takes.
- **Topic label or explainer.** "How X becomes Y", "What you told me, and what I will do about it", "Who I work with". Say the count and the action.
- **Imperative triad** written for rhythm. Say who does each step and by when.
- **Noun phrase with no verb.** "Thirteen weeks, with five dated milestones". Add the subject and the verb.
- **Passive "X gets Y" with no actor.** Name what acts on what.

| Type | Before | After |
|---|---|---|
| Figurative verb | Interviews and scans feed one ranked risk list | I rank the risks I find in interviews and in scans |
| Topic label | What you told me, and what I will do about it | My response to four facts in your brief |
| Imperative triad | Rank the risks, fix the highest, then give each one an owner | I rank the risks by day 30 and fix the top five by day 60 |
| No verb | Thirteen weeks, with five dated milestones | The 90 days run for thirteen weeks and have five milestones |
| No actor | Code gets four checks between a commit and production | We run four checks on every code change before production |
| Explainer | How a scanner finding becomes a fix | We fix the findings an attacker can reach first |
| Figurative verb | A test attack times how fast we detect and contain | I run a test attack each quarter and time our response |
| Figurative verb | One control library feeds three outputs | One control library supplies the auditor, customers and my report |
| Topic label | Who I work with, and what each gets from me | I work with five groups and send the executives a weekly update |
| Topic label | Three things I defer, and what starts each one | Compliance sequencing: ISO certificates wait for a signed deal |
| Vague claim | Each hire owns named work, so a cut shows what slows | We can run all six projects on schedule with four hires |
| Figurative verb | An incident runs on three clocks | We act within 1 hour, 24 hours and 72 hours of an incident |

## Inverted sentences (condition first, actor missing)

An inverted sentence opens with a condition or circumstance: "With...", "Without...", "When...",
"In...", "Each quarter...". Its subject is a thing or a count ("one item", "three wait", "two slow
down"), and no person does anything. The listener hears the limit before they hear the result.

- **Start with the actor.** "We" or "I", then "can" or a plain active verb, then the result with its number. Put the condition last. Pattern: "We can <result, with number> with <condition>."
- **State what gets done.** Do not count what is left undone ("three wait", "two slow down"). Give the positive number out of the total ("three of the six").
- **Name the things.** "One item", "named work" and "three things" hide what they are. Say "projects", "checks", "logins".
- **Test:** can the listener answer "who does what, and how much" from the first five words?

These come from a 90-day plan deck.

| Before | After |
|---|---|
| With no hires, one item stays on plan and three wait | We can finish three of the six projects by day 90 with no hires |
| With one hire, three items stay on plan and one waits | We can finish five of the six projects by day 90 with one hire |
| With two hires, four items stay on plan and two slow down | We can finish all six projects by day 90 with two hires |
| I plan four hires, and each one owns named work | We can run all six projects on schedule with four hires |
| Each quarter I run a test attack and time our response | I run a test attack each quarter and time our response |
| In an incident we act within 1 hour, 24 hours and 72 hours | We act within 1 hour, 24 hours and 72 hours of an incident |
| Every login for a person, an agent or a service account has an owner | We give every person, agent and service account login an owner |
| Every code change passes four checks before it reaches production | We run four checks on every code change before production |
| A vendor purchase and a questionnaire answer each take four steps | We approve a vendor in four steps and answer a questionnaire in four |
| Five example risks, each with an owner and a date | I give each risk an owner and a date |
| Without a baseline, no target can be promised | I set each target after I measure a baseline |
| When the budget is cut, detection is the first thing to slip | We can keep detection on schedule only with the full budget |

## Riddle titles (describes the slide, never names the subject)

A riddle title counts things and points at them with placeholders: "three things", "each one",
"what starts each", "what I will do about it". It describes the layout of the slide. The listener
cannot tell what the slide is about without reading the body. It is neither a metaphor nor a slogan.
It is a riddle, because every noun is a placeholder.

- **Name the subject, then say the point.** Use the ordinary term a colleague would use for the subject.
- **A plain topic name beats a full sentence made of placeholders.** "Compliance sequencing" tells the listener more than "Three things I defer, and what starts each one".
- **Test:** cover the body of the slide. Can the listener say what the slide is about from the title alone?

These come from a 90-day plan deck.

| Before | After |
|---|---|
| Three things I defer, and what starts each one | Compliance sequencing: ISO certificates wait for a signed deal |
| What you told me, and what I will do about it | My response to four facts in your brief |
| Who I work with, and what each gets from me | I work with five groups and send the executives a weekly update |
| Each hire owns named work, so a cut shows what slows | We can run all six projects on schedule with four hires |
| Six areas, and the first move in each | We run four checks on every code change before production |
| Two inputs, one output, three outcomes | I rank the risks I find in interviews and in scans |
| What changes, what stays, and why it matters | We keep the weekly report and drop the monthly one |

## Thumbnails, titles, captions and labels (Aidan's edits, 2026-10-02)

Short on-screen text names the thing. It does not narrate what someone does, and it does not judge.

- **Name the feature in plain words.** The viewer should read the label and know what the video shows.
- **No first-person narration in a label.** "I move the skeleton" is a sentence about the author. The label is the feature: "Custom sprite skeleton posing".
- **No hype or put-downs.** "The AI attack was weak" is an opinion with no referent. Say what is on screen: "Custom attack animation" or "Default attack vs posed attack".
- **No two-line call-and-response.** "I move the skeleton / Spritely draws the frame" reads like a slogan. One plain label is enough.

| Draft | Aidan's version |
|---|---|
| I MOVE THE SKELETON / Spritely draws the frame | CUSTOM SPRITE SKELETON POSING |
| THE AI ATTACK WAS WEAK / so I posed a new one | CUSTOM ATTACK ANIMATION |
| ONE DRAWING / 8 DIRECTIONS + A GAME | 8-DIRECTION SPRITE ANIMATION |

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
