"""Build the answer key BEFORE either tool is called, then fingerprint it.

Two of Eric's real Jev gates:

  A. M&A / ICP criteria (his M&A bot, 45AWhSkkaQ4.md:1827-1831; hiring hook at :1816):
     where they're based, headcount, industry, hiring now.
     50 YC companies. Answers come from the YC directory, updated the same day.

  B. "Have we actually published this piece of content before?" (his AEO gate, 45AWhSkkaQ4.md:277-279;
     the false hold at :929-940). 30 topics. Answers come from singlegrain.com's own post sitemaps.

Output: truth/companies.json, truth/topics.json, truth/SHA256SUMS
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRUTH = ROOT / "truth"


def first_location_is_us(c):
    first = (c.get("all_locations") or "").split(";")[0].strip()
    if not first or first.lower() == "remote":
        return None
    return first.endswith(", USA")


def size_band(n):
    """Clear yes/no for 'between 20 and 100 employees'; borderline sizes are left out."""
    if 25 <= n <= 85:
        return True
    if n <= 12 or n >= 150:
        return False
    return None


def companies(yc, n=50, seed=28):
    pool = []
    for c in yc:
        if c.get("status") != "Active" or c.get("industry") not in ("B2B", "Consumer") or not c.get("website"):
            continue
        us, band = first_location_is_us(c), size_band(c.get("team_size") or 0)
        if us is None or band is None:
            continue
        pool.append({
            "name": c["name"], "website": c["website"], "yc_page": c["url"],
            "truth": {"us_based": us, "size_20_100": band, "b2b": c["industry"] == "B2B",
                      "yc_job_open": bool(c.get("isHiring"))},
            "evidence": {"all_locations": c.get("all_locations"), "team_size": c.get("team_size"),
                         "industry": c.get("industry"), "isHiring": c.get("isHiring")},
        })
    rng = random.Random(seed)
    # Half B2B, half consumer, so "is it B2B?" has as many no's as yes's.
    b2b = [c for c in pool if c["truth"]["b2b"]]
    con = [c for c in pool if not c["truth"]["b2b"]]
    return rng.sample(b2b, n // 2) + rng.sample(con, n - n // 2)


# Topics he covered on video in October. Each was checked against all 2,746 post URLs
# by the keywords listed; none matched. Hand-check them before running.
NOT_PUBLISHED = [
    ("What OpenAI DevDay 2026 changed for marketers", ["devday", "dev-day"]),
    ("Using an AI tennis coach built on Jev Images to review match footage", ["tennis"]),
    ("NY Fed survey: small businesses using AI plan to hire more people", ["fed", "small-business-ai"]),
    ("Scanning your X followers with Grok Bot to find M&A targets", ["follower"]),
    ("Using state charts so a bot improver can find where AI agents break", ["state-chart", "statechart"]),
    ("An AI agent picked a connector and I paid $300 without comparing options", ["connector"]),
    ("Spying on competitors' Meta ads with Jev Images for under a penny", ["spy", "ad-library"]),
    ("Meta glasses footage as input for AI coaching", ["glasses"]),
    ("The 1-3-1 decision rule for running a bot fleet", ["1-3-1", "131"]),
    ("Trusted Continuation: handing work between AI agents", ["continuation"]),
    ("Grok Bot can read your DMs, bookmarks and followers", ["bookmark"]),
    ("Riverside as a podcast recording sponsor workflow", ["riverside"]),
    ("TV prices fell 97% while hospital prices rose 220%", ["hospital-price", "tv-price"]),
    ("Rent protests in Madrid and what drives housing costs", ["madrid", "rent-protest", "housing-cost"]),
    ("Analyzing Lily Ray's followers for about $15", ["lily"]),
]


def topics(post_urls, n_yes=15, seed=28):
    for title, keys in NOT_PUBLISHED:
        hits = [u for u in post_urls if any(k in u.lower() for k in keys)]
        if hits:
            sys.exit(f"'{title}' may be published already: {hits[:3]}")
    blog = sorted(u for u in post_urls if "/blog-posts/" in u)
    picked = random.Random(seed).sample(blog, n_yes)
    yes = [{"topic": re.sub(r"-v\d+$", "", u.rstrip("/").split("/")[-1]).replace("-", " "),
            "truth": {"published": True}, "evidence": u} for u in picked]
    no = [{"topic": t, "truth": {"published": False},
           "evidence": f"no post URL contains any of {k}"} for t, k in NOT_PUBLISHED]
    return yes + no


def main():
    yc_path, posts_path = sys.argv[1], sys.argv[2]
    yc = json.loads(Path(yc_path).read_text(encoding="utf-8"))
    posts = Path(posts_path).read_text(encoding="utf-8").split()
    TRUTH.mkdir(exist_ok=True)
    files = {"companies.json": companies(yc), "topics.json": topics(posts)}
    sums = []
    for name, data in files.items():
        blob = json.dumps(data, indent=1, ensure_ascii=False).encode("utf-8")
        (TRUTH / name).write_bytes(blob)
        sums.append(f"{hashlib.sha256(blob).hexdigest()}  {name}")
    (TRUTH / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print("\n".join(sums))
    print(f"{len(files['companies.json'])} companies, {len(files['topics.json'])} topics, {len(posts)} post URLs")


if __name__ == "__main__":
    main()
