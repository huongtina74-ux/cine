# CineFactory v229 — User expert Agent Leap / cinema workflow intake audit

Status: READ-ONLY CAPABILITY MAPPING, **NOT** a completed full VFX studio integration. Date: 2026-10-11.

## What the user already provided

- `config/technology/agent_leap_user_study_20261010.md`: exact ~109-line October 2026 4-expert report about MCP DCC, Comfy headless, foundation models, agent orchestrators, AYON/production asset+shot management, OpenUSD, QC, professional film craft.
- `config/technology/cinematography_studio_user_encyclopedia_202510.md`: longer 711-line encyclopedic listing of DCC apps/plugins/render engines, cinema crafts, pipelines, licenses, security and media formats.
- `config/technology/professional_studio_research_v214.json`: preexisting research index of 18 professional production technologies, incl OTIO, OCIO, ACES 2, OpenRV and Prism; already compiled as research, NOT installed/adopted by CineFactory.

The report was indeed already in the user's repository; claiming it had not been seen or stored would be wrong. The lapse: research ingestion was not converted into a verified production-grade integration, e.g. asset/shot version receipts, DCC scene export, multi-agent review and self-repair tested on actual finished media.

## Original author report versus verified technical facts

| Report topic | As-stated in the user's uploaded document | Verified / qualification outcome |
|---|---|---|
| Pipeline model | Multi-agent planner / executor (Maya/Comfy/Tripo) / independent critic; human director approvals | Good **architectural reference**, not evidence that *all* top Hollywood studios use the precise agent swarm |
| AYON/Noya | AYON with 'Noya' MCP assistant | AYON is an official open pipeline tool, successor to OpenPype: https://docs.ayon.dev/ ; https://github.com/ynput/ayon-core . The exact 'Noya MCP' claim remains **unverified**. No AYON install or API configured. |
| Pixar OpenUSD | Common scene/camera/assets across DCCs | Pixar source confirms scene interchange: https://www.pixar.com/openusd . No 3D production-roundtrip in CineFactory proved yet. |
| ComfyUI official MCP | Community 178 tools and local headless graph workflows | Official Comfy-Org has `comfy-mcp` with **40 tools**, local runtime through comfy-cli. Paid partner-node and security/licensing risks, not auto enabled: https://github.com/Comfy-Org/comfy-mcp . |
| Maya MotionMaker | AI-assisted actor paths/retarget | Official docs exist, not proof locally runnable/licensed: https://help.autodesk.com/cloudhelp/2026/ENU/Maya-MotionMaker/files/GUID-473B9D09-124C-4A5C-94F8-F3B4B89FAB18.html . |
| Houdini 22 | New FX/procedural workflows | Official SideFX release is real: https://www.sidefx.com/products/whats-new-in-h22/ . Not locally confirmed installed. |
| UE6 Scene-Aware AI | Presented like available engine feature | Epic says UE6 is *in development*, while UE5.8 is shipped: https://www.unrealengine.com/news/the-road-to-ue-6 . Specific ready-to-integrate Scene-Aware AI claim not established. |
| Khronos 4DGS | Report says `KHR_gaussian_splatting` standardized 4D | Khronos defines **3D** splats, ratified: https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_gaussian_splatting/README.md . 4D dynamic format standard not thereby shown. |
| FLUX 3 | Multimodal model from Black Forest Labs | Official 2026 July announcement/early access, not proof it is a free local RTX 3060 production checkpoint: https://bfl.ai/blog/flux-3 . |
| Sora discontinuation | Web April, API September | The dates are vendor-confirmed, but the report's alleged **reason** (failure of controllable production pipeline) is not supported: https://help.openai.com/vi-vn/articles/20001152-what-to-know-about-the-sora-discontinuation . |
| Render farm savings | AI causes automatic 40–75% energy savings | No source-controlled GPU/energy/quality benchmark, therefore do not use as real budget impact. |

## Eight-stage production model CineFactory should prove in sequence

1. Source whole moving media and original audio verification (v227/v228).
2. Planner/director's explicit approved beat sheet, assets, story logic, shot list and original language audio notes.
3. Asset, scene, camera, prop, character and animation **version + lineage** management (AYON-like contracts, without mandatory AYON).
4. Safe executor routes per shot: existing Blender worker, optional licensed Maya/Houdini/UE and local Comfy only after source + trusted MCP/version audit.
5. OpenUSD or suitable interoperable scene-package evaluation using SAME original shot; don't assume USD stores every rig/script feature.
6. Editorial and sound/color: OTIO/OCIO/ACES-like timecodes and single consistent output space, real audio and QC.
7. Independent critic QC: frame/body/face/camera/prop/texture/audio/copyright, return failed shot to owning department, retry budget, provenance.
8. Director approval/publish gate: only after *entire* actual full output is reviewed, rights cleared, signoff and rollback path.

## Next engineering tasks (not yet executed in this study)

First benchmark an original CineFactory shot across its existing worker with exact asset ID/hash/shot version, full audio+video render, quality receipt, automated failure-to-owner routing and human director acceptance. Then compare OpenUSD import/export and asset versioning. Integrate **one** qualified new DCC/MCP at a time; never install every cited repo. Document exact GPU VRAM and wall-clock accepted seconds/hour, license, third-party commands, network and cost triggers.

New files:
- `config/technology/agentic_film_studio_adoption_v229.json`: official vs unverified claims, 15 technology evaluations and 8 real studio qualification stages.
- `cinefactory/studio/film_expert_adoption_v229.py`: fail-closed read-only evaluator of prior user studies and 26 company departments.
- `python -m cinefactory.cli film-expert-adoption [--department TECHNICAL_DIRECTION]`: full audit.
- `film_expert_adoption_audit` MCP tool for Claude Code; project trust approval remains operator action.

Do not confuse **source document inside repository**, **read-only tool eligibility**, **installed software**, **tested local executable adapter**, or **production-certified end-to-end pipeline**.
