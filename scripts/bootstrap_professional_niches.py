from __future__ import annotations

from pathlib import Path
import sys
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cinefactory.studio.niche_os import DEFAULT_NICHES


FILES = {
    "research.yaml": {
        "audience_questions": [],
        "competitor_questions": [],
        "trend_sources": [],
        "production_forensics_questions": [],
    },
    "seo.yaml": {
        "keyword_clusters": {},
        "search_intents": {},
        "serp_snapshots": [],
        "content_gaps": [],
        "post_publish_search_feedback": [],
    },
    "competitors.yaml": {
        "channels": [],
        "breakout_channels": [],
        "breakout_videos": [],
        "production_hypotheses": [],
    },
    "formats.yaml": {
        "formats": {},
        "validated_workflows": [],
        "experiments": [],
    },
    "production.yaml": {
        "recipes": {},
        "approved_toolchains": {},
        "asset_libraries": {},
        "benchmark_cases": [],
    },
    "packaging_retention.yaml": {
        "title_patterns": [],
        "thumbnail_patterns": [],
        "opening_patterns": [],
        "retention_baselines": {},
        "experiments": [],
    },
    "risk_analytics.yaml": {
        "rights_and_policy": {},
        "monetization": {},
        "analytics_baselines": {},
        "validated_rules": [],
        "failure_patterns": [],
    },
}


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    root = repo / "config" / "niches"
    root.mkdir(parents=True, exist_ok=True)

    readme = [
        "# CineFactory Niche Operating Systems",
        "",
        "Each niche owns its audience, competitor, SEO, format, production, packaging,",
        "retention, risk and analytics state. Shared company/filmmaking principles live",
        "outside these folders. Cross-niche promotion requires evidence.",
        "",
    ]
    (root / "README.md").write_text("\n".join(readme), encoding="utf-8")

    for niche_id, manifest in DEFAULT_NICHES.items():
        folder = root / niche_id
        folder.mkdir(parents=True, exist_ok=True)
        payload = manifest.model_dump(mode="json")
        (folder / "niche.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        for filename, template in FILES.items():
            target = folder / filename
            if not target.exists():
                target.write_text(
                    yaml.safe_dump(template, sort_keys=False, allow_unicode=True),
                    encoding="utf-8",
                )

    print(f"bootstrapped {len(DEFAULT_NICHES)} niche operating-system folders at {root}")


if __name__ == "__main__":
    main()
