#!/usr/bin/env python3
"""Log into Grafana (admin/admin) and screenshot the provisioned dashboard."""
import sys

from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else "grafana.png"
BASE = "http://localhost:3000"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    page = b.new_page(viewport={"width": 1500, "height": 950})
    page.goto(f"{BASE}/login", wait_until="networkidle", timeout=60000)
    try:
        page.fill('input[name="user"]', "admin")
        page.fill('input[name="password"]', "admin")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2500)
        # Skip the "change password" prompt if shown.
        for label in ("Skip", "skip"):
            el = page.query_selector(f'a:has-text("{label}")') or \
                 page.query_selector(f'button:has-text("{label}")')
            if el:
                el.click(); page.wait_for_timeout(1000); break
    except Exception as e:
        print("login step note:", e)
    # Open the dashboard in kiosk mode (hides Grafana chrome).
    page.goto(
        f"{BASE}/d/grocery-overview/grocery-delivery-platform"
        f"?from=now-30m&to=now&refresh=10s&kiosk",
        wait_until="networkidle", timeout=60000,
    )
    page.wait_for_timeout(6000)  # let panels render
    page.screenshot(path=OUT, full_page=False)
    b.close()
print("saved", OUT)
