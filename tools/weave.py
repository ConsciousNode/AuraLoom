#!/usr/bin/env python3
"""
weave.py: render an AuraLoom score without a screen.

Made for the crew: write a score as text, run this, and get back
  <name>.wav        one pass of the loop (for Kham's ears)
  <name>-tile.png   an AuraGraph-format tile of it (for your eyes: open it and look)
  <name>-loom.png   the loom as AuraLoom draws it
  <name>.link.txt   a share link that opens AuraLoom with the score already woven

Usage:
  python3 tools/weave.py scores/my-piece.loom.txt [out_dir]

Needs Playwright with Chromium (pre-installed in Claude's cloud sandboxes:
`pip install playwright && playwright install chromium` anywhere else).
Runs the real index.html from this repo, so what you hear is what Kham hears.
"""
import asyncio, base64, os, sys, pathlib
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent.parent
PAGE = (HERE / "index.html").as_uri()
LIVE = "https://consciousnode.github.io/AuraLoom/"

async def main(score_path, out_dir):
    text = pathlib.Path(score_path).read_text(encoding="utf-8")
    name = pathlib.Path(score_path).name.split(".")[0]
    os.makedirs(out_dir, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto(PAGE)
        await pg.wait_for_function("() => !!(window.__loom && window.__loom.weaveScore)")
        res = await pg.evaluate("t => { const r = window.__loom.weaveScore(t); return r; }", text)
        wav = await pg.evaluate("() => window.__loom.wavB64()")
        tile = await pg.evaluate("() => window.__loom.tilePng()")
        loom = await pg.evaluate("() => window.__loom.loomPng()")
        link = await pg.evaluate("t => { const u = new TextEncoder().encode(t); let s = ''; for (const x of u) s += String.fromCharCode(x); return btoa(s).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''); }", text)
        await b.close()
    base = os.path.join(out_dir, name)
    if wav:
        open(base + ".wav", "wb").write(base64.b64decode(wav))
    open(base + "-tile.png", "wb").write(base64.b64decode(tile.split(",", 1)[1]))
    open(base + "-loom.png", "wb").write(base64.b64decode(loom.split(",", 1)[1]))
    open(base + ".link.txt", "w").write(LIVE + "#score=" + link + "\n")
    print(f"woven: {res['woven']} threads, {res['bars']} bars at {res['bpm']} BPM")
    for e in res["errs"]:
        print("  skipped line", e)
    for e in errors:
        print("  page error:", e)
    print("wrote:", ", ".join(os.path.basename(base) + s for s in ([".wav"] if wav else []) + ["-tile.png", "-loom.png", ".link.txt"]))
    if not wav:
        print("  (the loom was silent, so no WAV)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "out"))
