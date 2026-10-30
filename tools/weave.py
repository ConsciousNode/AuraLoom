#!/usr/bin/env python3
"""
weave.py: render an AuraLoom score without a screen.

Made for the crew: write a score as text, run this, and get back
  <name>.wav        one pass of the loop (for Kham's ears)
  <name>-loop.wav   loop-ready: exactly one loop long, reverb tail folded over the start
  <name>-read-1.png  the reading tile(s): AuraGraph's machine view of the sound (gray, the C6·d3
                    grid, every semitone ticked). This is the one to look at: it's built from the two
                    drawings 24 blind readers read best (LEGIBILITY-1), drawn by the AuraGraph app itself.
  <name>-tile.aura.png   the data tile (for tools: AuraLoom and AuraGraph read it back)
  <name>-loom.png   the loom as AuraLoom draws it
  <name>.link.txt   a share link that opens AuraLoom with the score already woven

Usage:
  python3 tools/weave.py scores/my-piece.loom.txt [out_dir]

Needs Playwright with Chromium (pre-installed in Claude's cloud sandboxes:
`pip install playwright && playwright install chromium` anywhere else).
Runs the real index.html from this repo, so what you hear is what Kham hears.
The reading tiles come from AuraGraph's app.html: set AURAGRAPH_APP to its path, or keep an AuraGraph
clone next to this repo, or it's fetched from GitHub. If none of those work, you still get everything else.
"""
import asyncio, base64, io, os, sys, pathlib, struct, urllib.request, wave
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent.parent
PAGE = (HERE / "index.html").as_uri()
LIVE = "https://consciousnode.github.io/AuraLoom/"
APP_RAW = "https://raw.githubusercontent.com/ConsciousNode/AuraGraph/main/app.html"


def auragraph_app():
    """The AuraGraph app's HTML, from the first place that has it."""
    for p in [os.environ.get("AURAGRAPH_APP"), HERE.parent / "AuraGraph" / "app.html", HERE.parent / "auragraph" / "app.html"]:
        if p and pathlib.Path(p).is_file():
            return pathlib.Path(p).read_text(encoding="utf-8"), str(p)
    try:
        return urllib.request.urlopen(APP_RAW, timeout=20).read().decode("utf-8"), APP_RAW
    except Exception as e:
        return None, f"not found ({e})"


def mono(wav_bytes):
    """16-bit WAV -> mono float samples."""
    w = wave.open(io.BytesIO(wav_bytes)); n, ch = w.getnframes(), w.getnchannels()
    v = struct.unpack("<%dh" % (n * ch), w.readframes(n))
    return [sum(v[i:i + ch]) / ch / 32768 for i in range(0, len(v), ch)], w.getframerate()

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
        wav = await pg.evaluate("() => window.__loom.wavB64(false)")
        loopwav = await pg.evaluate("() => window.__loom.wavB64(true)")
        tile = await pg.evaluate("() => window.__loom.tilePng()")
        loom = await pg.evaluate("() => window.__loom.loomPng()")
        reads, app_from = [], None
        if wav:
            html, app_from = auragraph_app()
            if html:
                ag = await b.new_page(viewport={"width": 1280, "height": 900})
                ag.on("pageerror", lambda e: errors.append("auragraph: " + str(e)))
                await ag.set_content(html)
                await ag.wait_for_function("() => !!window.__ag")
                x, sr = mono(base64.b64decode(wav))
                if sr == 22050:
                    await ag.evaluate("([x, n]) => __ag.make(Float32Array.from(x), n)", [x, name + ".loom"])
                    for k in range(await ag.evaluate("() => __ag.tiles.length")):
                        reads.append(await ag.evaluate("k => __ag.readingPng(k)", k))
                else:
                    errors.append(f"reading tiles skipped: the WAV is {sr} Hz, AuraGraph expects 22050")
        link = await pg.evaluate("t => { const u = new TextEncoder().encode(t); let s = ''; for (const x of u) s += String.fromCharCode(x); return btoa(s).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''); }", text)
        await b.close()
    base = os.path.join(out_dir, name)
    if wav:
        open(base + ".wav", "wb").write(base64.b64decode(wav))
        open(base + "-loop.wav", "wb").write(base64.b64decode(loopwav))
    open(base + "-tile.aura.png", "wb").write(base64.b64decode(tile.split(",", 1)[1]))
    open(base + "-loom.png", "wb").write(base64.b64decode(loom.split(",", 1)[1]))
    open(base + ".link.txt", "w").write(LIVE + "#score=" + link + "\n")
    for k, r in enumerate(reads):
        open(f"{base}-read-{k + 1}.png", "wb").write(base64.b64decode(r.split(",", 1)[1]))
    print(f"woven: {res['woven']} threads, {res['bars']} bars at {res['bpm']} BPM")
    for e in res["errs"]:
        print("  skipped line", e)
    for e in errors:
        print("  page error:", e)
    print("wrote:", ", ".join(os.path.basename(base) + s for s in ([".wav", "-loop.wav"] if wav else []) + [f"-read-{k + 1}.png" for k in range(len(reads))] + ["-tile.aura.png", "-loom.png", ".link.txt"]))
    if wav and not reads:
        print("  (no reading tiles: AuraGraph's app.html", app_from + ")")
    if not wav:
        print("  (the loom was silent, so no WAV)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "out"))
