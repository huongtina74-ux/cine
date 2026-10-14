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
