---
name: policy-check
description: Check an episode's upload package against what the video actually says and shows (misleading title/thumbnail, tag stuffing, off-platform calls to action, kids safety, AI disclosure, third-party footage) with tools/cf_policy_check.py before packaging is offered to the owner. Use after QC approval and before any upload decision.
---
# Policy check (before the owner sees the package)

1. `python tools/cf_policy_check.py --package <episode>/upload_package.json --dc <episode>/director_cut.json --srt <episode>/edit/<ID>_edit.srt --thumb-text "<words on the thumbnail>" --json <episode>/policy_report.json`
2. FAIL -> fix before anything else (title > 100 chars, title promises things the video never says/shows, third-party footage without license).
   WARN -> fix or write one line in HANDOFF.md why it is acceptable. Typical fixes: put the thumbnail words on screen or in the VO; cut tags that are not in the video (5-15 relevant tags); replace "join our group / link in bio" with an on-platform question; remove clickbait phrasing.
3. Rules from YouTube's own systems that this check encodes: title, thumbnail and tags are compared with speech-to-text and frames; the thumbnail must appear in the video; AI disclosure is a conscious yes/no in `ai_disclosure_required`; never re-upload third-party footage.
4. Upload remains the owner's action (or an explicitly authorized publish step). Draft/private first, schedule after the owner checks the draft.

## Muse/HaoHao content and account safety specialization (2026-11-09)
For `bell_leaf` image and video generation, also read `../cine-bell-leaf-stylized-3d-prompt-director/references/MUSE_HAOHAO_OPERATING_STANDARD_20261109.md` section 6. No official exhaustive Muse banned-token list is verified; review scene actions, child depictions, owner rights, attached images, voice usage, account behavior and provider terms contextually. Non-graphic magical peril is not automatically forbidden; sexualization of minors, explicit cruelty/gore, unlicensed real-person impersonation and attempts to evade policy or account limits must be blocked/rewritten for legitimate safety. A refusal is a review gate, not a prompt-obfuscation/retry challenge. This is separate from YouTube upload-policy QC.
