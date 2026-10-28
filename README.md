# Jev vs Parallel on two of Eric Siu's Jev gates

Eric Siu runs Jev as the cheap gate in front of his bots. Parallel launched a Decisions API this week that answers the same kind of question but searches the live web first. This tests both on the questions Eric's own gates ask, against answers fixed before either tool ran.

## The two gates

**A. M&A / ICP criteria**: his M&A bot maps "where they're based… whether their headcount is flat or if it's growing… the industry" (AEO webinar, Oct 2026), and his outreach hook is "we noticed that you're hiring". 50 YC companies, 4 questions each. Answer key: the YC directory, updated the same day.

**B. "Have we actually published this piece of content before?"**: his AEO gate. In the same webinar it held an idea because "Jev thought a page had already covered it… There's no DevDay post on the blog." 30 topics: 15 that are on singlegrain.com, 15 he covered on video that aren't. Answer key: the site's own post sitemaps (2,746 URLs).

Headcount growth isn't tested: there's no public answer key for it.

## Results (Oct 28, 2026)

Balanced accuracy, so always saying "no" scores 50%.

| Question | Jev (name + website only) | Jev + 10 closest sitemap URLs | Parallel |
|---|---|---|---|
| HQ in the US? | 68% | | 83% |
| 20–100 employees? | 43% | | 98% |
| Sells to businesses? | 70% | | 86% |
| Open job on its YC page? | 54% | | 96% |
| Already published on singlegrain.com? | 67% | 97% | 100% |

| | Jev | Parallel |
|---|---|---|
| Cost per 1,000 requests (list price) | $0.015 here; Eric's real usage ≈ $0.06 | $1.00 |
| Median latency | 0.36 s | 0.87 s |
| Answers between 0.4 and 0.6 | 116 of 230 | 5 of 230 |

## What it means

- **Facts about other companies: Parallel is worth it.** Jev doesn't know a 30-person startup's size or whether it's hiring, and it says so: half its answers sat near 0.5. Parallel looked them up.
- **Questions about your own site: give Jev your sitemap first.** Jev went from 67% to 97% once it was handed the 10 closest URLs, at about 3% of Parallel's price. The data matters more than the model.
- **The Dev Day case came back.** Given nearby OpenAI posts, Jev leaned "already published" (0.55) on a Dev Day post that doesn't exist, the same false hold Eric hit live. Parallel said 0.27. One case, not a rate.
- **Route by question:** Jev for judging text you already have, Jev plus your own data for questions about yourself, Parallel only for public facts that change.

**Where and how to use each, with cost per use case and API examples: [USE_CASES.md](USE_CASES.md).**

## Limits

- Small sample: 230 company answers and 30 topic answers.
- Scores above use the frozen key, unchanged. A hand check of Parallel's 16 misses (`hand_check.json`) found the key itself wrong on 9 (YC's own labels: e.g. Lago is in Paris, Algolia has no jobs on its YC page), right on 2, and 5 unclear. `adjusted.py` re-scores with those verdicts: Parallel 97–100%. That view favours Parallel, because only its misses were checked, so the frozen numbers are the ones to quote.
- The 15 published topics come from post URLs, which makes them easy to match.
- Jev's prompts here are short, so its cost per request is lower than in a real pipeline.
- One run, one day.

## Run it

```
python build_truth.py yc.json posts.txt   # answer key + fingerprint
python bench.py                           # needs TYPESAFE_API_KEY and PARALLEL_API_KEY in .env
python score.py                           # results.md, results.json
```

Raw responses for every call are in `raw/`. Built with Claude Code.
