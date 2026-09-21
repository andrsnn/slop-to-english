# Before and after

Real examples. Most "before" lines come from a slide deck drafted by a local Qwen 3.8-27B model.
The "after" lines are what the skill produces: the literal fact, with every number and technical term kept.

## Opaque phrases (most common, weighted 3x in the eval)

More lines of the kind the skill treats as top priority. Each "before" hides a number or a name.

| Type | Before | After |
|---|---|---|
| Abstract noun | Our engine of growth is a referral loop that brought 1,800 signups in May. | A referral program brought 1,800 signups in May. |
| Abstract noun | Security is in our DNA. We rotate 60 API keys every 30 days. | We rotate 60 API keys every 30 days. |
| Abstract noun | The momentum is real: 5 releases in 5 weeks. | We shipped 5 releases in 5 weeks. |
| Abstract noun | This quarter was about laying the groundwork. We migrated 12 services to Postgres 16. | This quarter we migrated 12 services to Postgres 16. |
| Meta-flourish | It's software building software: an agent that reviews the 25 pull requests other agents open each day. | One agent reviews the 25 pull requests other agents open each day. |
| Meta-flourish | This isn't a report, it's a mirror of how 6 people worked over 90 days. | This report covers how 6 people worked over 90 days. |
| Meta-flourish | Behind every commit is a lesson. This month we learned that 2 retries beat 5. | This month we found that 2 retries beat 5. |
| Slogan | Ship fast, learn faster. We deployed 31 times last week. | We deployed 31 times last week. |
| Slogan | Code is a liability. We deleted 6 of our 18 microservices in March. | We deleted 6 of our 18 microservices in March. |
| Slogan | Small team, big impact: 4 engineers built the whole billing system in 10 weeks. | 4 engineers built the billing system in 10 weeks. |
| Figurative verb | Listen to operators. They see the cracks the org chart misses first. | Ask the people who run day-to-day operations, like support and sales. They notice problems before anyone else does. |
| Figurative verb | Our onboarding flow now sings. Signup takes 90 seconds and 2 screens. | Signup now takes 90 seconds and 2 screens. |
| Figurative verb | The database finally exhaled after we added 3 read replicas, and p99 latency settled at 120 ms. | After we added 3 read replicas, p99 latency is 120 ms. |
| Figurative verb | Kubernetes tamed the beast: 48 services now roll out with zero downtime. | With Kubernetes, 48 services now roll out with zero downtime. |
| Idiom | The team hit the ground running and closed 9 bugs on day 1. | The team closed 9 bugs on day 1. |

## Lines

| Pattern | Before | After |
|---|---|---|
| Slogan | The machine is the manager. | A failing test blocks the commit. |
| Slogan | Proof over claims. | Reviewers only see the code and the test results. |
| Metaphor | The pose finally lands. | The model draws the reference image according to the skeleton pose provided. |
| Slogan | Owning the stack. | I started running my own models. |
| Slogan | Nobody trains on bad data. A human signs off first. | I review every training record before it's used. |
| Meta-flourish | An agent writing about agents. | A local Qwen model wrote this deck. |
| Vague claim | Four months, each one a step up. | Commits rose from 777 in June to 1,855 in August. |
| Slogan | The API bill is now zero. | I run the models on my own hardware, so there are no API fees. |
| Symbols | 23/23 e2e | All 23 end-to-end tests pass |
| Balanced count | Three ways to get answers, one way to score them. | The script can send each test to a server, run a command, or read a saved file. Scoring is the same for all three. |

## Whole slides

| Before | After |
|---|---|
| The agents did the work. The pipeline checked it. | Agents write the code. Tests and reviews check it. |
| The fix: a model that actually reads the pose. | Qwen-Image-Edit-2509 reads the pose. |
| llmhub: the API bill is now zero. | llmhub runs the models on my own hardware. |
| 854 agent sessions, run like a team. | 854 agent sessions. |
| This deck was written by the thing it describes. | A local model wrote the first draft. |
| The hard part was staying up: a 135 GB model that won't fit in RAM, and a watchdog that keeps clients alive through 25-minute reloads, zero errors. | No errors during 25-minute model reloads. |
| A full-time job on one side of the clock; a product people pay for, a finished game, and my own AI stack on the other. The agents did the hands-on work. I set the direction, and made every claim prove itself. | Alongside my full-time job I built a paid product, a game, and my own AI setup. Agents did the hands-on work. |

The last two show the length trade-off. Slides had a 150-character limit, so the rewrite drops detail.
Without a limit the skill keeps every fact (see `evals/cases_own.jsonl`, where the references keep them all).

Test cases built from these lines are in `evals/cases_own.jsonl`.
