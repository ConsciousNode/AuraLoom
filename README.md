# AuraLoom
Weave sound on a loom. Pitch threads run across, time runs along, and brightness is loudness. Paint notes, plucks, drums and noise, then play the picture as a loop.

**Play it:** https://consciousnode.github.io/AuraLoom/

AuraLoom is the playable half of [AuraGraph](https://github.com/ConsciousNode/AuraGraph). AuraGraph turns audio into picture tiles that a model can read. AuraLoom turns pictures back into music you can play with.

## What it does
- **The loom:** 200 rows, one per quarter-tone, from C1 to about 10 kHz. Every octave is the same height. The columns are 16th notes on a tempo grid (BPM and 1–8 bars).
- **Threads (brushes):** Tone (held, can glide), Pluck (struck, then rings and fades; drag to strum), Kick, Snare, Hat, Noise and Erase.
- **Voices** for Tone and Pluck: Pure, Flute, String, Reed, Organ and Bell (real inharmonic bell partials). You can see each overtone ladder on the loom.
- **Key and scale snap:** Chromatic, Major, Minor, both Pentatonics, Dorian, Blues, or Free. In-key rows are lit and the root rows are cyan.
- **Two renderers:**
  - **Clean:** each tone row is a phase-continuous oscillator, so painted notes play in tune. A4 measures 439.9 Hz. Noise threads become real spectral noise.
  - **Ghost:** the whole picture is rebuilt with Griffin-Lim, the same way AuraGraph tiles play back. Use it for imported audio and pictures.
- **Genesis FM voices:** FM Lead, FM Bass, FM Keys, FM Brass, FM Bell and FM Clang. These are two-operator FM in the spirit of the Mega Drive's YM2612, after Synth Radio's voices. Each note's brightness moves over its life, and you can watch the sidebands open and close on the loom. **Crunch** rounds the output to fewer bits, the way a console's digital-to-analog converter does.
- **Scores: music as text.** Write a score in the ✎ Score panel or hand AuraLoom a link with the score in it (`#score=…`). This is how the Claude crew composes: they write text, `tools/weave.py` renders it headless to WAV + an AuraGraph tile they can look at, and Kham presses ▶. **⇡ Write score** goes the other way: everything you've painted with the brushes is written back out as a score, so you can paint a beat, turn it into text, and hand it to the crew to edit, or the reverse. (Imported audio and pictures can't become a score; that would need transcription.) See [CREW.md](CREW.md). The first piece is [`scores/peepers.loom.txt`](scores/peepers.loom.txt).
- **It plays as a loop while you paint.** Changes are woven in on the fly.
- **Imports:** a recording, any picture, or an AuraGraph / Paint-a-Tile tile (placed on its real 30 Hz–11 kHz axis).
- **Exports:**
  - WAV: one pass of the loop, with the Space reverb tail
  - Loop WAV: exactly one loop long (sample-accurate to the tempo), with the tail folded over the start, so it repeats seamlessly in any player, DAW or game engine
  - PNG of the loom
  - AuraGraph-format tile: 160 bands that any crew member can read
  - Project file, to reopen later

One HTML file. Zero dependencies. Works offline. Nothing is uploaded.

Keys: `Space` play/stop · `1`–`7` threads · `[` `]` size · `Ctrl+Z` undo · `G` Clean/Ghost

**Siblings:** [Chromatrack](https://github.com/ConsciousNode/chromatrack) · [Synth Radio](https://github.com/ConsciousNode/Synth-Radio) · [Speaker Box Magnum](https://github.com/ConsciousNode/Speaker-Box-Magnum)

Named by Kehai Interim (Kham gave da the naming); idea Kham Kizer; built by Kehai Interim. ConsciousNode SoftWorks. MIT licensed.
