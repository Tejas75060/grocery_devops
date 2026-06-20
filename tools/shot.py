#!/usr/bin/env python3
"""Screenshot helper for capturing evidence per stack.

Modes:
  url   <url> <out.png> [wait_ms] [width height]   - screenshot a web page
  term  <out.png> "<title>"                         - render stdin as a terminal

Web pages are captured with headless Chromium (Playwright). CLI output is piped
on stdin and rendered into a terminal-styled PNG so it looks like a real shot.
"""
import html
import sys

from playwright.sync_api import sync_playwright


def shot_url(url, out, wait_ms=2500, width=1366, height=900):
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": int(width), "height": int(height)})
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(int(wait_ms))
        page.screenshot(path=out, full_page=False)
        browser.close()
    print(f"saved {out}")


TERM_TMPL = """<!doctype html><html><head><meta charset='utf-8'><style>
body{{margin:0;background:#1d1f21;font-family:'SF Mono',Menlo,Consolas,monospace}}
.win{{margin:18px;border-radius:10px;overflow:hidden;box-shadow:0 8px 30px #000a;
      border:1px solid #333}}
.bar{{background:#323232;height:34px;display:flex;align-items:center;padding:0 12px;gap:8px}}
.dot{{width:12px;height:12px;border-radius:50%}}
.r{{background:#ff5f56}}.y{{background:#ffbd2e}}.g{{background:#27c93f}}
.title{{color:#bbb;font-size:13px;margin-left:10px}}
pre{{margin:0;padding:16px 18px;color:#e6e6e6;font-size:13.5px;line-height:1.45;
     white-space:pre-wrap;word-break:break-word;background:#1d1f21}}
.p{{color:#27c93f}}
</style></head><body><div class='win'>
<div class='bar'><span class='dot r'></span><span class='dot y'></span>
<span class='dot g'></span><span class='title'>{title}</span></div>
<pre>{body}</pre></div></body></html>"""


def shot_term(out, title="terminal"):
    body = sys.stdin.read()
    page_html = TERM_TMPL.format(title=html.escape(title), body=html.escape(body))
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1100, "height": 200})
        page.set_content(page_html)
        page.wait_for_timeout(300)
        el = page.query_selector(".win")
        el.screenshot(path=out)
        browser.close()
    print(f"saved {out}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "url":
        shot_url(*sys.argv[2:])
    elif mode == "term":
        out = sys.argv[2]
        title = sys.argv[3] if len(sys.argv) > 3 else "terminal"
        shot_term(out, title)
    else:
        sys.exit("unknown mode")
