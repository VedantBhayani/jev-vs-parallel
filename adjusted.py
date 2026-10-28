"""Re-score gate A with the hand-check verdicts. truth/ stays frozen; this is a second view, not a replacement.

- verdict "parallel" or "key": use the real answer found by hand
- verdict "unclear": drop that company-question from both tools' scores
"""
import json
from pathlib import Path

from bench import COMPANY_QUESTIONS, check_truth, slug
from score import load, metrics, p_of

ROOT = Path(__file__).resolve().parent


def main():
    check_truth()
    companies = json.loads((ROOT / "truth" / "companies.json").read_text(encoding="utf-8"))
    checks = json.loads((ROOT / "hand_check.json").read_text(encoding="utf-8"))["verdicts"]
    fix = {(v["company"], v["question"]): v for v in checks}

    lines = ["| Question | Arm | Frozen key | After hand check | n after |", "|---|---|---|---|---|"]
    out = {}
    for q in COMPANY_QUESTIONS:
        for arm in ("jev", "parallel"):
            frozen, adjusted = [], []
            for c in companies:
                p = p_of(load(arm, f"co-{slug(c['name'])}"), q)
                t = c["truth"][q]
                frozen.append((p, t))
                v = fix.get((c["name"], q))
                if v and v["verdict"] == "unclear":
                    continue
                adjusted.append((p, v["real_answer"] if v else t))
            f, a = metrics(frozen), metrics(adjusted)
            out[f"{q}/{arm}"] = {"frozen": f, "adjusted": a}
            lines.append(f"| {q} | {arm} | {f['balanced_accuracy']:.0%} | {a['balanced_accuracy']:.0%} | {a['n']} |")
    (ROOT / "results_adjusted.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
