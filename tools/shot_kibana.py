#!/usr/bin/env python3
"""Screenshot Kibana Discover showing the grocery-logs-* data view."""
import sys

from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
BASE = "http://localhost:5601"

with sync_playwright() as b_p:
    b = b_p.chromium.launch(args=["--no-sandbox"])
    page = b.new_page(viewport={"width": 1500, "height": 950})
    # Land on Discover directly; with a single data view Kibana auto-selects it.
    page.goto(f"{BASE}/app/discover", wait_until="domcontentloaded", timeout=90000)

    # Wait for the Discover data grid to render (cold start can be slow).
    grid = None
    for sel in ('[data-test-subj="docTable"]',
                '[data-test-subj="discoverDocTable"]',
                '.euiDataGrid',
                '[data-test-subj="unifiedDataTableToolbar"]'):
        try:
            page.wait_for_selector(sel, timeout=60000)
            grid = sel
            break
        except Exception:
            continue

    # Dismiss any onboarding / security popups so the grid is visible.
    for label in ("Dismiss", "Don't show again"):
        for el in page.query_selector_all(f'button:has-text("{label}")'):
            try:
                el.click()
                page.wait_for_timeout(400)
            except Exception:
                pass

    # Wait for the actual result rows to render (search to complete).
    for sel in ('.euiDataGridRow', '[data-test-subj="dscTableRow"]',
                '[data-test-subj="discoverQueryHits"]'):
        try:
            page.wait_for_selector(sel, timeout=40000)
            break
        except Exception:
            continue
    page.wait_for_timeout(8000)
    page.screenshot(path=OUT, full_page=False)
    b.close()
print("saved", OUT, "grid=", grid)
