# Where to use Jev, where to use Parallel, and how

The rule from the test: **Jev for text you already have. Jev plus your own data for questions about yourself. Parallel only for public facts that change, and only on the shortlist.**

Prices used below: Jev ≈ $0.06 per 1,000 requests (Eric's own: ~370,000 requests for ~$23), Parallel $1 per 1,000 requests, up to 100 questions per request. The costs below are estimates worked out from those prices, not measured runs.

## The pattern: cheap gate first, web check on survivors

```
big list ──► Jev (text you have) ──► shortlist ──► Parallel (live web, with sources) ──► action
                 ~$0.06 / 1,000                       $1 / 1,000
```

Eric's talent bot already works this way: "it uses Jev to look before… And then it'll use the expensive tokens" (tgKsHfID6Sg.md:711–719). Parallel goes in the "expensive" slot when the missing piece is a public fact.

---

## 1. M&A bot: agencies worth a conversation
**His words:** map "where they're based… whether their headcount is flat or if it's growing… the industry" (45AWhSkkaQ4.md:1827–1831).

| Step | Tool | Question | Input |
|---|---|---|---|
| 1 | Jev | Is this account an agency owner or operator? | Their bio / profile text |
| 2 | Parallel | HQ in the US? 40–80 employees? Marketing agency? Hiring now? | Company name + website, **4 questions in one request** |

**Cost:** 2,300 commenters on a post → Jev ≈ $0.14 → ~200 agencies → Parallel 200 requests ≈ $0.20. **About $0.35 total.**
**Test result:** on these kinds of questions, Jev 43–70%, Parallel 83–98%.

## 2. Outreach hook: "we noticed you're hiring"
**His words:** "hey um we noticed that you're hiring a bunch of people right now" (45AWhSkkaQ4.md:1815–1817).

| Step | Tool | Question |
|---|---|---|
| 1 | Jev | ICP fit, from what you already know (bio, CRM fields) |
| 2 | Parallel | "Does this company have open job postings right now?" Keep the **source link** |
| 3 | Code | Opener only if p ≥ 0.7, and it cites the link |

**Why Parallel:** hiring changes weekly. Jev scored 54% on "open job?" and Parallel 96%.

## 3. ICP list: 60,000 leads to 2,000
**His words:** "how we cut 60,000 leads to 2,000 ICP fits" (O2D8DvQ6zWA.md:255).

| Step | Tool | Cost |
|---|---|---|
| Fit from the data you have (title, industry, notes) | Jev on 60,000 | ≈ $3.60 |
| Fresh facts on the 2,000 (size, funding, hiring) | Parallel on 2,000 | ≈ $2.00 |
| **Total** | | **≈ $5.60** (all on Parallel: ≈ $60) |

## 4. AEO gate: "have we already published this?"
**His words:** the gate at 45AWhSkkaQ4.md:277–279; the false hold at :929–940.

**Don't pay for Parallel here first.** Give Jev your own pages:
1. Code: pull your sitemap and pick the 10 URLs that overlap the idea most (see `closest_posts()` in `bench.py`).
2. Jev: "Has this topic already been published?" with those 10 URLs in the state.
3. **Escalate only if Jev is unsure** (p between 0.35 and 0.65) → ask Parallel, which searches the live web.

**Test result:** Jev alone 67%, Jev + sitemap 97%, Parallel 100%. The Dev Day false hold was one of the unsure ones (0.55).
**Cost:** 20 ideas a day ≈ nothing for Jev; maybe 2 a day go to Parallel ≈ $0.06 a month.

## 5. Stats gate: is this number still current?
**His words:** "do you actually have real statistics to back this up or are you just making stuff up?" (45AWhSkkaQ4.md:282–284), and "maybe we only want stuff after 2020" (:636–639).

| Step | Tool | Question |
|---|---|---|
| 1 | Code | Pull every number and year out of the draft |
| 2 | Jev | Is this claim backed by a cited source in the text? |
| 3 | Parallel | Only for stats older than your cut-off: "Is there newer data on this?" Keep the link |

**Cost:** about 5 stats per post ≈ $0.005 per post.

## 6. Email sign-ups: ICP or M&A fit
**His words:** "all the people that are opting into our email list that are ICP fit or M&A fit" (O2D8DvQ6zWA.md:707–710).
Same as #1: Jev on what they typed into the form, Parallel on the company for the ones that pass.

---

## Where NOT to use Parallel

| Gate | Use | Why |
|---|---|---|
| AI-tell score on a draft | Jev | The answer is in the text |
| Repurposing ("which channel?") | Jev | It's judgement on your own video |
| Talent pre-screen (promotions, tenure) | Jev | It's in the CV. Don't search the web about candidates |
| Engagers "active 3× in 30 days" | Code + Jev | It's your own X or LinkedIn data |
| Ad creatives, homepages, video frames | Jev Images | Parallel takes no images |

---

## How to call them

**Jev** (one request, several questions about the same thing):
```bash
curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"jev-latest","state":"<the text you already have>",
       "questions":{"icp_fit":{"type":"noul","instructions":"This account runs or owns a marketing agency."}}}'
```

**Parallel** (it searches the web; batch the questions about one company into one request):
```bash
curl https://api.parallel.ai/v1/decisions \
  -H "x-api-key: $PARALLEL_API_KEY" -H "Content-Type: application/json" \
  -d '{"state":{"company":"Acme","website":"https://acme.com"},
       "questions":{
         "us_hq":{"type":"noul","instructions":"This company'"'"'s headquarters is in the United States."},
         "size":{"type":"noul","instructions":"This company has between 40 and 80 employees."},
         "hiring":{"type":"noul","instructions":"This company has open job postings right now."}}}'
```
Each answer comes back as a probability (`noul`). The `citations` cover the whole request, so ask one question per request when you need a source per answer.

**The routing rule in code:**
```python
def route(question, p_jev=None):
    if question.about_public_fact_that_changes:   # size, hiring, funding, location
        return "parallel"                         # on the shortlist only
    if question.about_own_site and p_jev is not None and 0.35 <= p_jev <= 0.65:
        return "parallel"                         # Jev was unsure even with your data
    return "jev"
```

## Test it on your own gate

1. Write your answer key first: `truth/*.json`, then fingerprint it (`build_truth.py` shows how).
2. Put your questions in `bench.py` (`COMPANY_QUESTIONS` / `TOPIC_QUESTION`).
3. `python bench.py` → `python score.py`. Check every miss by hand before you trust the numbers.
