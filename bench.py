"""Ask Jev and Parallel the same questions. Refuses to run if the answer key changed.

Arms
  jev            Jev, given only what a bot would have up front (company name + website, or the topic).
  jev+sitemap    Gate B only: Jev, plus the 10 post URLs whose words overlap the topic most.
                 Plain-code retrieval, $0. Shows what Jev does once it's handed the evidence.
  parallel       Parallel Decisions API: same input, but it searches the live web itself.

Every response is saved in raw/ with its latency and reused on re-runs.
Keys come from .env here or in ../why-now/.env and are never printed.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRUTH, RAW = ROOT / "truth", ROOT / "raw"
JEV_URL = "https://api.typesafe.ai/v1/systemone"
PARALLEL_URL = "https://api.parallel.ai/v1/decisions"
TODAY = "2026-10-28"

COMPANY_QUESTIONS = {
    "us_based": "This company's headquarters is in the United States.",
    "size_20_100": "This company has between 20 and 100 employees.",
    "b2b": "This company sells mainly to other businesses rather than to consumers.",
    "yc_job_open": "This company currently has at least one open job listed on its Y Combinator company page.",
}
TOPIC_QUESTION = {"published": "singlegrain.com has already published a blog post that covers this topic."}


def api_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for env in (ROOT / ".env", ROOT.parent / "why-now" / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                k, _, v = line.partition("=")
                if k.strip() == name and v.strip():
                    return v.strip()
    return None


def check_truth():
    for line in (TRUTH / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split()
        if hashlib.sha256((TRUTH / name).read_bytes()).hexdigest() != digest:
            sys.exit(f"truth/{name} changed after it was fingerprinted. Not running.")


def post(url, headers, body):
    data = json.dumps(body).encode()
    for attempt in range(4):
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={**headers, "Content-Type": "application/json"})
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.load(r)
            return resp, round(time.perf_counter() - t0, 3)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(3 * (attempt + 1))
                continue
            sys.exit(f"HTTP {e.code} from {url}: {e.read().decode(errors='replace')[:300]}")
        except urllib.error.URLError:
            time.sleep(3 * (attempt + 1))
    sys.exit(f"no answer from {url}")


def questions(qs):
    return {k: {"type": "noul", "instructions": v} for k, v in qs.items()}


def ask(arm, item_id, state, qs, keys):
    path = RAW / f"{arm}--{item_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), False
    if arm.startswith("jev"):
        resp, secs = post(JEV_URL, {"Authorization": f"Bearer {keys['jev']}"},
                          {"state": json.dumps(state, ensure_ascii=False), "model": "jev-latest",
                           "questions": questions(qs)})
    else:
        resp, secs = post(PARALLEL_URL, {"x-api-key": keys["parallel"]},
                          {"state": state, "questions": questions(qs)})
    out = {"seconds": secs, "response": resp}
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out, True


def words(s):
    return set(re.findall(r"[a-z0-9]+", s.lower())) - {"the", "a", "and", "to", "of", "for", "in", "on", "with", "how", "your", "you", "is"}


def closest_posts(topic, posts, k=10):
    tw = words(topic)
    scored = sorted(posts, key=lambda u: (-len(tw & words(u.split("singlegrain.com/")[-1])), u))
    return scored[:k]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main():
    check_truth()
    keys = {"jev": api_key("TYPESAFE_API_KEY"), "parallel": api_key("PARALLEL_API_KEY")}
    if not all(keys.values()):
        sys.exit("Need TYPESAFE_API_KEY and PARALLEL_API_KEY in .env")
    RAW.mkdir(exist_ok=True)
    companies = json.loads((TRUTH / "companies.json").read_text(encoding="utf-8"))
    topics = json.loads((TRUTH / "topics.json").read_text(encoding="utf-8"))
    posts = (TRUTH / "posts.txt").read_text(encoding="utf-8").split()
    live = {"jev": 0, "parallel": 0}

    for c in companies:
        state = {"company": c["name"], "website": c["website"], "today": TODAY}
        for arm in ("jev", "parallel"):
            _, fresh = ask(arm, f"co-{slug(c['name'])}", state, COMPANY_QUESTIONS, keys)
            live["jev" if arm == "jev" else "parallel"] += fresh

    for t in topics:
        base = {"topic": t["topic"], "site": "singlegrain.com", "today": TODAY}
        arms = {
            "jev": base,
            "jev+sitemap": {**base, "closest_singlegrain_posts": closest_posts(t["topic"], posts)},
            "parallel": base,
        }
        for arm, state in arms.items():
            _, fresh = ask(arm, f"topic-{slug(t['topic'])}", state, TOPIC_QUESTION, keys)
            live["parallel" if arm == "parallel" else "jev"] += fresh
        print(".", end="", flush=True)

    print(f"\nlive requests: Jev {live['jev']}, Parallel {live['parallel']} (≈${live['parallel'] * 0.001:.3f})")


if __name__ == "__main__":
    main()
