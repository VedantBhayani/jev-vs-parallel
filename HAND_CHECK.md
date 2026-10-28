# Hand-check before posting (~20 min)

**Done Oct 28.** Verdicts, sources and controls are in `hand_check.json`; `adjusted.py` re-scores with them. Lago, Algolia and Directed Edge were also checked by hand in a browser. Result: the key was wrong on 9 rows, right on 2, and 5 were unclear.

The answer key was frozen before any tool ran (`truth/SHA256SUMS`). These are the rows where Parallel disagreed with it.
Open each link and decide who's right. Don't edit the truth files: write your verdict here, and the post reports both numbers.

| # | Question | Company | Answer key | Parallel | Check | Your verdict |
|---|---|---|---|---|---|---|
| 1 | B2B? | Directed Edge | no (YC says Consumer) | yes 0.84 | directededge.com | |
| 2 | B2B? | nunu.ai | no (YC says Consumer) | yes 0.99 | nunu.ai | |
| 3 | B2B? | Clipboard | no (YC says Consumer) | yes 0.94 | clipboardhealth.com | |
| 4 | B2B? | Hogaru | no | yes 0.51 | hogaru.com | |
| 5 | B2B? | Pair AI | no | yes 0.72 | its website | |
| 6 | B2B? | Dydema | no | yes 0.87 | its website | |
| 7 | B2B? | Camp | no | yes 0.71 | its website | |
| 8 | US HQ? | treble.ai | no (São Paulo listed first) | yes 0.68 | treble.ai | |
| 9 | US HQ? | Cuckoo Labs | no (Seoul) | yes 0.89 | its website | |
| 10 | US HQ? | Twenty | no (Paris) | yes 0.90 | twenty.com | |
| 11 | US HQ? | Camp | no (Stockholm listed first) | yes 0.92 | its website | |
| 12 | US HQ? | Lago | yes (SF) | 0.44 | getlago.com | |
| 13 | US HQ? | SigmaOS | yes (SF listed first) | 0.01 | sigmaos.com | |
| 14 | 20–100 staff? | nunu.ai | no (YC says 5) | yes 0.97 | LinkedIn / site | |
| 15 | 20–100 staff? | Confident AI | no (YC says 7) | 0.51 | LinkedIn / site | |
| 16 | Open YC job? | Algolia | yes | no 0.01 | ycombinator.com/companies/algolia | |

Also check 3 random Parallel "right" answers the same way, so we're not only checking where it disagreed.
