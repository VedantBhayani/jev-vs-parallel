"""Score every arm against the frozen answer key.

"yes" means p >= 0.5. Balanced accuracy = mean of (right on true-yes items, right on true-no items),
so always answering "no" scores 50%, not 86%. Brier = mean squared gap between p and the truth (lower is better).
Refusals count as wrong and are reported separately.

Output: results.json, results.md
"""
import json
import statistics
from pathlib import Path

from bench import COMPANY_QUESTIONS, TOPIC_QUESTION, check_truth, slug

ROOT = Path(__file__).resolve().parent
JEV_PRICE_PER_M = 0.042      # input tokens, output free (TypeSafe list price)
PARALLEL_PER_REQ = 0.001     # Parallel list price


def load(arm, item_id):
    return json.loads((ROOT / "raw" / f"{arm}--{item_id}.json").read_text(encoding="utf-8"))


def p_of(resp, q):
    a = resp["response"].get("answers", {}).get(q, {})
    return a.get("noul") if a.get("type") == "noul" else None


def metrics(pairs):
    """pairs: [(p or None, truth bool)]"""
    yes = [(p, t) for p, t in pairs if t]
    no = [(p, t) for p, t in pairs if not t]

    def right(p, t):
        return p is not None and (p >= 0.5) == t

    def rate(rows):
        return sum(right(p, t) for p, t in rows) / len(rows) if rows else None

    answered = [(p, t) for p, t in pairs if p is not None]
    return {
        "n": len(pairs),
        "accuracy": rate(pairs),
        "balanced_accuracy": (rate(yes) + rate(no)) / 2 if yes and no else rate(pairs),
        "right_on_yes": f"{sum(right(p, t) for p, t in yes)}/{len(yes)}",
        "right_on_no": f"{sum(right(p, t) for p, t in no)}/{len(no)}",
        "brier": statistics.mean((p - t) ** 2 for p, t in answered) if answered else None,
        "refused": len(pairs) - len(answered),
    }


def main():
    check_truth()
    truth = ROOT / "truth"
    companies = json.loads((truth / "companies.json").read_text(encoding="utf-8"))
    topics = json.loads((truth / "topics.json").read_text(encoding="utf-8"))

    results, calib, usage, misses = {}, {}, {}, []
    gates = [
        ("A", ["jev", "parallel"], [(f"co-{slug(c['name'])}", c) for c in companies], COMPANY_QUESTIONS),
        ("B", ["jev", "jev+sitemap", "parallel"], [(f"topic-{slug(t['topic'])}", t) for t in topics], TOPIC_QUESTION),
    ]
    for gate, arms, items, qs in gates:
        for arm in arms:
            u = usage.setdefault(arm, {"requests": 0, "input_tokens": 0, "seconds": []})
            for item_id, _ in items:
                r = load(arm, item_id)
                u["requests"] += 1
                u["input_tokens"] += r["response"].get("usage", {}).get("input_tokens", 0)
                u["seconds"].append(r["seconds"])
            for q in qs:
                pairs = []
                for item_id, item in items:
                    p, t = p_of(load(arm, item_id), q), item["truth"][q]
                    pairs.append((p, t))
                    if p is not None:
                        b = min(int(p * 5), 4)
                        c = calib.setdefault(arm, [[0, 0] for _ in range(5)])
                        c[b][0] += 1
                        c[b][1] += t
                    if p is None or (p >= 0.5) != t:
                        misses.append({"gate": gate, "arm": arm, "question": q,
                                       "item": item.get("name") or item.get("topic"), "p": p, "truth": t})
                results[f"{gate}/{q}/{arm}"] = metrics(pairs)

    cost = {}
    for arm, u in usage.items():
        dollars = (u["input_tokens"] / 1e6 * JEV_PRICE_PER_M) if arm.startswith("jev") else u["requests"] * PARALLEL_PER_REQ
        cost[arm] = {"requests": u["requests"], "input_tokens": u["input_tokens"], "dollars": round(dollars, 5),
                     "per_1000_requests": round(dollars / u["requests"] * 1000, 3),
                     "median_seconds": statistics.median(u["seconds"])}

    (ROOT / "results.json").write_text(json.dumps(
        {"results": results, "calibration": calib, "cost": cost, "misses": misses}, indent=1), encoding="utf-8")

    pct = lambda x: "–" if x is None else f"{x:.0%}"
    lines = ["# Jev vs Parallel on two of Eric's Jev gates", "", "## Results", "",
             "| Gate | Question | Arm | Balanced acc. | Right on yes | Right on no | Brier | Refused |",
             "|---|---|---|---|---|---|---|---|"]
    for key, m in results.items():
        g, q, arm = key.split("/")
        lines.append(f"| {g} | {q} | {arm} | {pct(m['balanced_accuracy'])} | {m['right_on_yes']} | {m['right_on_no']} | "
                     f"{'–' if m['brier'] is None else round(m['brier'], 3)} | {m['refused']} |")
    lines += ["", "## Cost and speed (list prices)", "", "| Arm | Requests | Input tokens | Cost | Per 1,000 requests | Median seconds |",
              "|---|---|---|---|---|---|"]
    for arm, c in cost.items():
        lines.append(f"| {arm} | {c['requests']} | {c['input_tokens']:,} | ${c['dollars']} | ${c['per_1000_requests']} | {c['median_seconds']} |")
    lines += ["", "## Calibration: when it said p in this range, how often was the answer actually yes", "",
              "| Arm | 0–0.2 | 0.2–0.4 | 0.4–0.6 | 0.6–0.8 | 0.8–1.0 |", "|---|---|---|---|---|---|"]
    for arm, buckets in calib.items():
        lines.append(f"| {arm} | " + " | ".join(f"{t}/{n}" if n else "–" for n, t in buckets) + " |")
    (ROOT / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n{len(misses)} wrong or refused answers listed in results.json")


if __name__ == "__main__":
    main()
