# CineFactory v231 — YouTube original browser playback can be controlled through PowerShell

Scope: 2026-10-11 Chrome/Playwright isolated no-login browser *feasibility test*, original Maizen reference `ZmT0ITUGUII`, not a completed full audiovisual episode review.

## Actual demonstrated evidence

- On DESKTOP-HJE6A6D, Windows Google Chrome installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`, Playwright and Selenium installed, Python OpenCV/PIL/mss installed, FFmpeg available.
- Launched NEW isolated Chrome headless using Playwright, did not change user's open interactive Chrome session.
- Navigated `https://www.youtube.com/watch?v=ZmT0ITUGUII` using official YouTube browser UI: **HTTP 200**, correct Maizen video title.
- Actual HTML video element exists; `currentTime=7.602886` seconds, `duration=1684.461` seconds, `paused=false`, `readyState=4`, `error=null`, `muted=false`. This proves 7.6s media playback through browser. Does NOT prove local audio capture, native audio understanding or full 28:04 played.
- Took real browser screenshot at `.tools/maizen_browser_probe_v231.png`. Visually inspected: in-game view with heads-up display (hearts/hunger/hotbar), two large colored pipe openings, subtitles, game landscape, no black frame. Screenshot is an example, not proof that the whole episode or soundtrack was reviewed.
- Probe script kept in local Git-ignored `.tools/maizen_browser_probe_v231.py`, JSON machine trace `.tools/maizen_browser_probe_v231.json`.
- Previous `yt-dlp` direct media stream URL had HTTP403, but using original public YouTube browser returned HTTP200 and playback. Do not equate these two access methods.
- Windows FFmpeg has `dshow` and `gdigrab` devices, but `ffmpeg -f dshow -list_devices true -i dummy` enumerated **no audio capture devices**. This does not prove WASAPI/audio loopback can never work; it has not yet been built or tested in controlled capture. Do not assert full original soundtrack was listened to.
- No credits were spent for browser test, no source video copied/downloaded, no login or copyright bypass.
- One prior vidIQ external provider watch report exists (v230), but v227 full source review still **BLOCKED**.

## Important exact capability difference

1. **YouTube browser playback: VERIFIED**; can use Python/Playwright via PowerShell to navigate/watch real source.
2. **Periodic actual visual inspection via browser screenshots: VERIFIED for one screenshot**; need automatic full-time playback trace and aligned samples.
3. **Full moving video review, covering all frames/timecodes: NOT COMPLETED**, and frame screenshots alone do not equal exhaustive moving-film comprehension.
4. **Full original audio loopback capture, speech, Foley, music and sync review: NOT CONFIGURED/VERIFIED**.
5. **Full 28:04 film watched and QC signed: NOT COMPLETED**.
6. **Exact Maizen production technology identified: NOT VERIFIED**, regardless of source viewing.

## Next R&D for CineFactory, before certifying full watch

Use the official browser playback path for the legally viewable original. Implement continuous actual player-position evidence and timecoded screenshots/video comprehension along the *entire* 28:04 with playback monitoring to detect stalls/skipped segments. Configure an authorized audio monitoring path (Chrome audio loopback via Windows WASAPI/appropriate capturer or owner-supplied authorized media) with whole-episode speech/sound verification and synchronized timeline. Review all <=30s windows and require independent QC. Respect YouTube terms and copyright; do not silently store or redistribute full third-party content or use unauthorized downloads. No v227 gate bypass by headless browser playback/probe alone.

## Commands for checking progress (from CineFactory root)

```powershell
python .tools/maizen_browser_probe_v231.py
python -m cinefactory.cli maizen-full-video-review
python -m cinefactory.cli maizen-research-stage --stage-id G03 --enforce
```
