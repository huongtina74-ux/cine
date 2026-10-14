# CineFactory v215 — Shared Technology Knowledge Base (26 departments)

**Implemented in actual Windows Git repository:** research only. No tool/model installation, network call, credit consumption, or backend switch is made by this feature.

## Source archives and coverage

- `config/technology/cinematography_studio_user_inventory_202510.txt`: exact submitted user source, 18 numbered sections, 512 lines.
- `config/technology/cinematography_studio_user_encyclopedia_202510.md`: exact submitted 711-line full original encyclopedia, including detailed workflow prose.
- `config/technology/ai_media_radar_20261010.json`: unchanged curated 96 baseline entries.
- `config/technology/professional_studio_research_v214.json`: 18 reviewed R&D references from the prior scoped study.

The earlier 373-row CSV accidentally counted 10 subtable headers as tool rows (eight `Repo/Tool` headings in section 4, one `Tính năng` and one `Framework`). Actual **source entries: 363** across sections 1–10 and 12–18, plus **eight 11th-section workflow definitions**, and their complete source texts. Combined search index has **477 records (96 + 18 + 363)**, but this is **not** a deduplicated count of 477 separately usable software products.

The raw index retains all source names/descriptions, section, subsection and source line. It annotates conservative exact/curated aliases; it never deletes a row due to fuzzy guesses.

## Usage from Windows PowerShell (repository root)

```powershell
python -m cinefactory.cli technology-knowledge --query "compositing" --minor-niche minecraft_story_adventure --department EDITORIAL --limit 12
python -m cinefactory.cli technology-knowledge --query "MCP" --department RND
python -m cinefactory.cli technology-knowledge --kind STUDIO_CRAFT_SKILL --limit 30
python -m cinefactory.cli technology-knowledge --kind PROPRIETARY_INHOUSE_REFERENCE_ONLY
python -m cinefactory.cli technology-knowledge-summary --minor-niche long_slices_game --top-k 5
python -m cinefactory.cli niche-technology-plan --minor-niche long_slices_game
```

Module API: `cinefactory.studio.technology_knowledge_v215.load_company_knowledge()`,
`query_company_knowledge(query=..., minor_niche=..., department=..., kind=..., limit=...)`, `department_knowledge_index(...)`.

The company v212 **stage DAG** now adds `knowledge_reference_ids` for each owning department; the v213 **niche strategy** includes `all_department_knowledge_references`. These references are suggestions for research, **not selections to automatically execute**. Specific software installation/running requires separate validated adapters and licensing/benchmark checks.

## Taxonomy and safe workflow

18 kinds: DCC, specialist plugins, rendering, AI models/repos, AI video, SaaS, reference/asset sites, craft skills, MCP server ideas, agents/frameworks, workflow references, hardware/storage, open file/color standards, security, design/motion, audio, proprietary systems and pipeline frameworks.

Each department can query the same knowledge source with format-specific routing; e.g. Creative/Research examines the reference and methods, Editing examines editorial/video/sound/finishing, Art/Animation inspects rig/motion, Audio inspects audio chain, R&D and Tech Direction check candidates, QC/Operations check risk, performance and provenance.

**Per-niche required decision process:** competitor evidence → authorized timestamped video+audio review → derive original techniques and intent → search candidate methods per scene/stage → rights/license/security/hardware check → isolated difficult shot pilots → quality floor → speed in accepted finished seconds/hour → owner approval → update versioned capabilities.

Every user-encyclopedia record has `USER_REFERENCE_NOT_INDEPENDENTLY_VERIFIED`, `installed=UNKNOWN`, `benchmark=NOT_RUN`, `license=NOT_CHECKED`, `production_permission=false`. Many are hardware, skills or proprietary examples, not executable packages. A public name such as "Blender MCP" is **not** a verified server identity. Cloud/SaaS and premium DCC have cost/terms gates; licensing must be checked independently. Changing a line in the source files changes its SHA256 digest in output.

## Current-update integration

The **existing** v211 GitHub/Hugging Face pending discovery and v212 official Claude/MCP/AI/SaaS watch remain the source of future new candidates. New discoveries must be vetted before inclusion into the reviewed registry and skill catalog; v215 does not silently install or automatically promote a pending tool. No new Windows scheduled task was created by v215. The existing research schedule is independent of the manual official-source `technology-watch` run unless explicitly configured.

## Tests and limitations

`tests/test_technology_knowledge_v215.py` verifies 18 source sections, all eight workflows, 96+18+363 counts, archive hash lineage, 26-department lookup, safe flags, alias matching, CLI, and fail-closed arguments.

Limitations: tag-based match is an initial retrieval/routing aid, **not** semantic video observation, quality ranking, rights clearance, actual support for a model, or working Claude/MCP installation. Source claims from October 2025 may be outdated. `niche-technology-plan` keeps all new tooling as advisory until authentic evidence exists.
