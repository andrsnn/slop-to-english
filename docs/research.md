# LLM-speak, AI slop, and AI-isms: research notes

Examples marked (synthetic) were written for this document. Examples marked (source) were quoted from the linked page. The pages were read through a summarizing fetch tool, so spot-check any quote before you reuse it publicly.

## A. What it is called and why it happens

**Names.** People use several overlapping terms.
- "Slop" means unwanted AI-generated content. Simon Willison popularized it in May 2024 by analogy to "spam", and defines it as content "mindlessly generated and thrust upon someone who didn't ask for it" [SW1]. Merriam-Webster and the American Dialect Society both picked "slop" as a 2025 word of the year (reported in search results, not verified on their sites).
- "AI-isms", "LLM-speak", "AI tells", and "AI tropes" mean the recurring word and sentence habits that make text read as machine-written. Wikipedia's editor guide "Signs of AI writing" (WP:AISIGNS) is the most detailed public catalog [W1]. tropes.fyi is a second catalog with over 50 entries [T1].
- "Emphatic epanorthosis" is the technical name for one habit: the "not X, but Y" self-correction [B1].

**Evidence that it is real and measurable.**
- Kobak et al. compared about 14 to 15 million PubMed abstracts from 2010 to 2024. After ChatGPT launched, style words jumped in frequency. "Delves" rose by a factor of 25.2. Other flagged words include "crucial", "intricate", "meticulously", "pivotal", "showcasing", and "underscores". The authors estimate at least 10% of 2024 abstracts were processed with an LLM, and up to 30% in some sub-corpora [K1].
- Liang et al. looked at 950,965 papers from 2020 to February 2024 on arXiv, bioRxiv, and Nature portfolio journals. They found steady growth in LLM-modified text, largest in computer science (up to 17.5%) [L1].
- Wikipedia editors list the word set by era. Examples from 2023 to mid-2024: "delve", "tapestry", "testament", "landscape", "intricate", "pivotal", "underscore", "vibrant". They note that the favored words shift as models change, so word lists go stale [W1].
- Boggia measured "not X, but Y" density with an Epanorthosis Index (model density divided by human density). Models overshoot human rates in oratory, and underuse the figure in informal Q&A [B1].

**Why it happens.** The sources support these causes, at different strengths.
1. Preference tuning. Juzek and Ward tested where words like "delve" come from. Their user studies suggest reinforcement learning from human feedback (RLHF) may contribute, but the findings are mixed and they say lack of transparency limits the research [J1]. Boggia argues that the "not X, but Y" habit comes from training corpora rich in promotional prose plus preference tuning that rewards confident, emphatic phrasing [B1].
2. Loss of variety after alignment. A separate line of work finds that post-training (RLHF, DPO) reduces output diversity ("mode collapse"). Its proposed data-level cause is typicality bias: human raters prefer familiar, predictable text [V1]. This explains why many different models produce similar prose, though the paper does not study the specific phrases listed here.
3. Training-data mix for punctuation. Goedecke argues em-dash overuse comes from newer models training on digitized late-1800s and early-1900s print books, which use about 30% more em-dashes than current prose [G1]. This is one author's hypothesis, not a settled result.
4. No taste or revision. Commentators say models write in one pass and apply a device (parallelism, tricolon, antithesis) every time because it reliably sounds "written", not because it fits [D1]. This is opinion, not measurement.
5. Prompt-level fixes work. Anthropic's prompting guide advises telling the model what to do instead of what not to do, for example asking for "smoothly flowing prose paragraphs" [A1]. Anthropic's published Claude system prompt bans one specific AI-ism: "Claude never starts its response by saying a question or idea or observation was good, great, fascinating, profound, excellent, or any other positive adjective" [SW2]. I did not find OpenAI documentation that names these phrases specifically, so nothing from OpenAI is cited here.

**What the sources do not show.** No source I found proves a single cause. Do not claim that RLHF, or any one data source, alone explains the phrasing. The tropes.fyi and gist lists are community catalogs, not studies. Their point that any one pattern is fine, but several clustered together signal machine text, is a fair reading of how the Wikipedia guide also warns against relying on one sign [W1][T1][G2].

## B. Taxonomy (19 categories)

Category slugs match the `category` field in `cases.jsonl`. A 20th slug, `control-plain`, marks inputs that are already plain and should come back unchanged.

1. **negative-parallelism.** Defines the point by denying a strawman first: "not X, but Y". Examples: "It's not bold. It's backwards." (source T1). "not only a work of self-representation, but a visual document" (source W1). "Dropbox Paper is more than a doc - it's a co-editing tool that brings creation and coordination together in one place." (source GC1). Also "This is not a course. It is a journey of transformation" (source B1). Sources: W1, T1, GC1, B1.
2. **rule-of-three.** Lists items in threes (tricolon) for rhythm, often padded to fill the slot. Examples: "authority, clarity, and inoffensiveness" (source D1). "Plan smarter, ship faster, and grow stronger" (synthetic). "reliability, observability, and maintainability" (synthetic). Sources: W1, T1, D1, GPTZero (https://gptzero.me/news/the-rule-of-three/).
3. **punchline-em-dash.** Em-dashes used for dramatic asides and a punchline at the end of a sentence. Examples: "The problem -- and this is the part nobody talks about -- is systemic." (source T1). "a 14-inch laptop, 1.2 kg, 20-hour battery — built for one thing: you" (synthetic). "cut the build time — and that changes everything" (synthetic). Sources: W1, T1, G1.
4. **ai-vocabulary.** Words that appeared far more often in text after ChatGPT. Examples: "delve", "tapestry", "landscape", "testament", "intricate", "meticulous", "pivotal", "underscore", "realm", "crucial", "showcasing". "Somali merchants played a pivotal role in global coffee trade" (source W1). "Let's delve into the details..." (source T1). Sources: K1, L1, W1, T1, J1.
5. **buzzword-verbs.** Corporate verbs and adjectives with no concrete meaning. Examples: "leverage", "unlock", "elevate", "streamline", "harness", "seamless", "robust", "empower", "best-in-class synergies" (synthetic). "an all-in-one solution that unlocks unprecedented productivity" (source T1). Sources: T1, W1, G2.
6. **sycophantic-opener.** Praise for the question before answering. Examples: "Great question!" (synthetic). "What a fantastic and insightful observation!" (synthetic). Anthropic's system prompt bans openers that call a question "good, great, fascinating, profound, excellent" (source SW2). Sources: SW2, W1 (collaborative communication section).
7. **filler-signpost.** Announces what it will say instead of saying it. Examples: "It's worth noting that this approach has limitations." (source T1). "Let's break this down step by step." (source T1). "Let's dive in!" (synthetic). "Without further ado" (synthetic). Sources: T1, G2.
8. **cliche-scene-setter.** Opens with a vague world-state sentence. Examples: "In today's fast-paced digital world" (synthetic). "In an era of unprecedented change" (synthetic). "Ever since I was a child" (synthetic). No source found for exact frequency data. The pattern is described as "Imagine a world where..." and similar futurism openers in T1 and G2.
9. **grandiose-closer.** Ends by inflating the stakes to history or the future. Examples: "This will fundamentally reshape how we think about everything." (source T1). "In conclusion, the future of AI depends on..." (source T1, signposted conclusion). "we will reshape the future of payments, one API call at a time" (synthetic). Sources: T1, G2.
10. **false-profundity-slogan.** A quotable line that sounds deep and carries no information. Examples: "Story points are a planning tool with no fixed unit." (source T1, listed under quotable one-liners). "Data is the new oil" (synthetic). "Every pixel tells a story" (synthetic). Sources: T1.
11. **machine-personification.** Software and processes given human roles, or metaphors for automation. Examples: "quietly orchestrating workflows, decisions, and interactions" (source T1). "The pipeline checked it" (synthetic). "A fleet of agents" (synthetic). "The machine is the manager" (synthetic). Sources: T1 (forced figurative language, magic adverbs). Kriss describes AI prose as straining after depth and resonance [NYT].
12. **abstract-noun-subject.** Nominalized verbs and abstract nouns as the subject, hiding who did what. Examples: "the enablement of redundancy" (synthetic). "the realization of a 35% reduction" (synthetic). "characterized by the delivery of growth" (synthetic). Sources: W1 (superficial analyses, avoidance of basic copulatives) describes the related habit. No dedicated study found.
13. **significance-inflation.** Claims something is a pivotal, lasting symbol. Examples: "marking a pivotal moment in the evolution of regional statistics" (source W1). "An enduring testament to the influence..." (source W1). "stands as a testament to the team's dedication" (synthetic). Sources: W1.
14. **promotional-puffery.** Brochure language in neutral prose. Examples: "Nestled within the breathtaking region of Gonder" (source W1). "a vibrant town with a rich cultural heritage" (source W1). "boasts a diverse array" (W1 lists "boasts", "diverse array"). Sources: W1, T1.
15. **copula-avoidance.** Swaps "is" and "has" for pompous verbs. Examples: "serves as LAAA's exhibition space for contemporary art" (source W1, edited from "is LAAA's exhibition arm"). "The building serves as a reminder of the city's heritage" (source T1). "stands as", "marks", "represents", "boasts", "features" (source W1). Sources: W1, T1.
16. **vague-attribution.** Claims from unnamed groups. Examples: "Experts argue that this approach has significant drawbacks." (source T1). "Industry reports", "Observers have cited", "Some critics argue" (source W1). "Industry observers widely believe" (synthetic). Sources: W1, T1.
17. **staccato-rhetorical-question.** Self-asked question with a one-word answer, and stacked fragments. Examples: "The result? Devastating." (source T1). "He published this. Openly. In a book. As a priest." (source T1). "Skills? Python. Experience? 7 years." (synthetic). Sources: T1.
18. **false-suspense-analogy.** Teases a reveal, invites imagination, or explains with a metaphor. Examples: "Here's the thing about AI adoption." (source T1). "Imagine a world where every tool you use..." (source T1). "Think of it like a highway system for data." (source T1). Sources: T1, G2.
19. **despite-challenges-formula.** Names a problem only to dismiss it. Examples: "Despite its industrial prosperity, Korattur faces challenges typical of urban areas" (source W1). "Despite these challenges, Amu TV has managed to continue providing vital service" (source W1). "Despite these challenges, the initiative continues to thrive." (source T1). Sources: W1, T1.

Other patterns the sources list but that were not turned into test categories: title case headings, bold-first bullets, unicode arrows, emoji formatting, fractal summaries, synonym cycling, invented concept labels ("the supervision paradox"), false ranges ("from innovation to implementation to cultural transformation"), and compulsive counting ("Five things we wish to discuss") [W1][T1].

## C. Sources

- [W1] Wikipedia, "Signs of AI writing" (WP:AISIGNS): https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- [K1] Kobak, Gonzalez-Marquez, Horvat, "Delving into ChatGPT usage in academic writing through excess vocabulary": https://arxiv.org/abs/2406.07016 (HTML: https://arxiv.org/html/2406.07016v1)
- [L1] Liang et al., "Mapping the Increasing Use of LLMs in Scientific Papers": https://arxiv.org/abs/2404.01268
- [J1] Juzek and Ward, "Why Does ChatGPT 'Delve' So Much? Exploring the Sources of Lexical Overrepresentation in Large Language Models": https://arxiv.org/abs/2412.11385
- [B1] Boggia, "Artificial Epanorthosis: Why large language models overuse a classical rhetorical figure, and how to mitigate it": https://arxiv.org/abs/2607.21498
- [V1] "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity": https://arxiv.org/abs/2510.01171
- [SW1] Simon Willison, "Slop is the new name for unwanted AI-generated content": https://simonwillison.net/2024/May/8/slop/
- [SW2] Simon Willison, "Highlights from the Claude 4 system prompt": https://simonwillison.net/2025/May/25/claude-4-system-prompt/
- [A1] Anthropic, "Prompting best practices": https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- [T1] tropes.fyi, AI Writing Pattern Directory: https://tropes.fyi/directory
- [G2] "AI Writing Tropes to Avoid" gist: https://gist.github.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1
- [GC1] GC AI, "AI Writing Pattern to Know: Contrastive Negation": https://gc.ai/blog/ai-writing-pattern-to-know-contrastive-negation
- [G1] Sean Goedecke, "Why do AI models use so many em-dashes?": https://www.seangoedecke.com/em-dashes/
- [D1] Colin Gorrie, "Why ChatGPT writes like that": https://www.deadlanguagesociety.com/p/rhetorical-analysis-ai
- [NYT] Sam Kriss, New York Times Magazine essay on the voice of AI writing, published 2025-12-03 (URL seen in search results, not opened): https://www.nytimes.com/2025/12/03/magazine/chatbot-writing-style.html
- Also seen, not relied on for claims: Wikipedia "AI slop" https://en.wikipedia.org/wiki/AI_slop
