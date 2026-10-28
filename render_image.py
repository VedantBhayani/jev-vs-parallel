"""Render the results image for the post (1600x900 PNG). Numbers are the frozen-key results from results.md."""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent

HTML = """
<style>
  * { box-sizing: border-box; margin: 0; }
  body { width: 1600px; height: 900px; background: #0b0b0c; color: #f4f4f2; font-family: "Segoe UI", Arial, sans-serif; padding: 64px 90px; }
  .kicker { color: #f27038; font-size: 22px; font-weight: 600; letter-spacing: .04em; }
  h1 { font-size: 50px; font-weight: 750; margin: 14px 0 34px; letter-spacing: -.01em; }
  table { width: 100%; border-collapse: collapse; font-size: 27px; }
  th { text-align: left; color: #8b8b86; font-weight: 600; padding: 0 0 14px; border-bottom: 1px solid #333; font-size: 22px; }
  td { padding: 15px 0; border-bottom: 1px solid #1f1f22; }
  td.n { font-weight: 700; width: 220px; }
  .jev { color: #e0b44a; } .par { color: #7fd18b; } .dim { color: #555; }
  .row2 { display: flex; gap: 40px; margin-top: 34px; }
  .box { flex: 1; background: #151517; border: 1px solid #2a2a2d; border-radius: 14px; padding: 22px 26px; font-size: 22px; line-height: 1.45; color: #cfcfcb; }
  .box b { color: #f4f4f2; }
  .foot { position: absolute; bottom: 34px; left: 90px; right: 90px; color: #8b8b86; font-size: 19px; display: flex; justify-content: space-between; }
</style>
<div class="kicker">JEV VS PARALLEL · ERIC SIU'S OWN JEV GATES · OCT 28, 2026</div>
<h1>Same questions, answers fixed before either tool ran</h1>
<table>
  <tr><th>Question (balanced accuracy)</th><th>Jev</th><th>Jev + sitemap</th><th>Parallel</th></tr>
  <tr><td>M&amp;A: HQ in the US?</td><td class="n jev">68%</td><td class="n dim">–</td><td class="n par">83%</td></tr>
  <tr><td>M&amp;A: 20–100 employees?</td><td class="n jev">43%</td><td class="n dim">–</td><td class="n par">98%</td></tr>
  <tr><td>ICP: sells to businesses?</td><td class="n jev">70%</td><td class="n dim">–</td><td class="n par">86%</td></tr>
  <tr><td>Outreach: open job on its YC page?</td><td class="n jev">54%</td><td class="n dim">–</td><td class="n par">96%</td></tr>
  <tr><td>AEO: already published on singlegrain.com?</td><td class="n jev">67%</td><td class="n par">97%</td><td class="n par">100%</td></tr>
</table>
<div class="row2">
  <div class="box"><b>Cost per 1,000 decisions</b><br>Jev ≈ $0.02–0.06 · Parallel $1.00<br>Whole test: $0.08</div>
  <div class="box"><b>The Dev Day false hold, again</b><br>Given nearby OpenAI posts, Jev leaned "published" (0.55). The post doesn't exist. Parallel: 0.27.</div>
  <div class="box"><b>Route it</b><br>Text you have → Jev<br>Your own site → Jev + your data<br>Public facts that change → Parallel</div>
</div>
<div class="foot"><span>50 YC companies + 30 topics · frozen answer key · hand check: key wrong on 9 of Parallel's 16 misses</span><span>Vedant Bhayani</span></div>
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1600, "height": 900})
    page.set_content(HTML)
    out = HERE / "results.png"
    page.screenshot(path=str(out))
    b.close()
    print(out)
