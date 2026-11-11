# Case: Day Zero (@DayZeroMinecraft) - new long-form channel in our zombie lane (2026-11-11)

## Why today's API run missed it
- It WAS scanned on 2026-11-03 and 2026-11-04 (watchlist + new_le_30d) and listed in the 2026-11-05 daily report.
- Today's `cf_mc_api_dataset.py` only searches videos published in the last 7/15 days and had no watchlist pass.
  Day Zero's newest upload is 2026-10-23 (19 days old), so it fell out of the window -> missing from the long-form table.
- Fix (on the PC, backup `cf_mc_api_dataset.py.bak_2026-11-11`): new `watchlist_channels.txt` (32 channels incl. Day Zero)
  is always fetched (channels.list + uploads), group "watchlist". Compiles; not re-run today (quota already used: 9,130 units).

## Facts (OBSERVED)
- Channel created 2026-10-05 (API, 11-03). Turkey. 14.9K subs, "4 videos", 2 visible on the Videos tab (2026-11-11 page).
- "I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft" 52:00 - 2M views, ~1 month (1.91M on 11-04).
- "I Survived 100 Days in a DEADLY OUTBREAK in Minecraft" 40:30 - 431K, ~2 weeks.
- Descriptions (read 2026-11-11):
  - Maps from Planet Minecraft: "Pine River - highly realistic small town" by heyitskad ("customized and detailed by me");
    "Mosslorn 1000x1000 custom abandoned city" (CurseForge author milkshake_mp3, licence shown "All Rights Reserved", 394 MB, 1.20.1-26.1.2).
  - Own video-only modpack; main mods: The Hordes (zombie hordes), TaCZ (guns), Immersive Vehicles (MTS), Legendary Survival Overhaul.
  - "focuses on cinematic story-telling... may contain planned events... but the gameplay itself is real".
  - Inspired by ForgeLabs, CoffeeFuelledGenius, OkRobert (100-day hardcore cinematic creators).
- planetminecraft.com shows a Cloudflare bot check to the built-in browser; not bypassed. Map pages read via CurseForge/search instead.

## INFERRED
- Strongest proof so far that a 0-sub channel can break in with long-form in our exact lane: 2 videos, 2.4M views, 5 weeks.
- Formula: "I Survived 100 Days in a <DISASTER> in Minecraft", 40-52 min, first-person narrated cinematic hardcore,
  planned story events on a pre-built detailed map, horde mod for big zombie crowds, vehicles/guns for set pieces.
- Their speed comes from (a) downloaded maps instead of building, (b) real gameplay recorded, not keyframe animation.
- Risks for us: map licences ("All Rights Reserved" - permission needed before monetised use); guns/realistic gore narrow
  the "all ages" target; mods need owner-approved installs (Forge/NeoForge, shaders, replay mod).
