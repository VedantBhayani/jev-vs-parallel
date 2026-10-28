# Jev vs Parallel on two of Eric's Jev gates

## Results

| Gate | Question | Arm | Balanced acc. | Right on yes | Right on no | Brier | Refused |
|---|---|---|---|---|---|---|---|
| A | us_based | jev | 68% | 21/36 | 11/14 | 0.233 | 0 |
| A | size_20_100 | jev | 43% | 1/7 | 31/43 | 0.218 | 0 |
| A | b2b | jev | 70% | 23/25 | 12/25 | 0.206 | 0 |
| A | yc_job_open | jev | 54% | 1/14 | 36/36 | 0.176 | 0 |
| A | us_based | parallel | 83% | 34/36 | 10/14 | 0.088 | 0 |
| A | size_20_100 | parallel | 98% | 7/7 | 41/43 | 0.043 | 0 |
| A | b2b | parallel | 86% | 25/25 | 18/25 | 0.105 | 0 |
| A | yc_job_open | parallel | 96% | 13/14 | 36/36 | 0.02 | 0 |
| B | published | jev | 67% | 7/15 | 13/15 | 0.197 | 0 |
| B | published | jev+sitemap | 97% | 15/15 | 14/15 | 0.048 | 0 |
| B | published | parallel | 100% | 15/15 | 15/15 | 0.014 | 0 |

## Cost and speed (list prices)

| Arm | Requests | Input tokens | Cost | Per 1,000 requests | Median seconds |
|---|---|---|---|---|---|
| jev | 80 | 28,481 | $0.0012 | $0.015 | 0.359 |
| parallel | 80 | 314,527 | $0.08 | $1.0 | 0.8705 |
| jev+sitemap | 30 | 19,920 | $0.00084 | $0.028 | 0.3545 |

## Calibration: when it said p in this range, how often was the answer actually yes

| Arm | 0–0.2 | 0.2–0.4 | 0.4–0.6 | 0.6–0.8 | 0.8–1.0 |
|---|---|---|---|---|---|
| jev | 1/8 | 15/70 | 54/116 | 22/31 | 5/5 |
| parallel | 2/109 | 0/12 | 2/5 | 2/5 | 91/99 |
| jev+sitemap | 0/6 | 0/5 | 0/4 | – | 15/15 |
