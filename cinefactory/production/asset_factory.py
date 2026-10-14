from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from cinefactory.domain.enums import RightsStatus
from cinefactory.domain.models import AssetBibleSpec, AssetRecord, RightsEnvelope
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.production.contracts import AssetCandidate, AssetFactoryReport, CanonicalAssetSelection
from cinefactory.production.image_pipeline import ComfyImagePipeline
from cinefactory.qc.visual_command import CommandVisualQC
from cinefactory.qc.visual_policy import normalized_visual_review


class AssetFactory:
    """Builds canonical local character/scene/prop reference assets before shot production."""

    def __init__(self, ctx, *, visual_qc: CommandVisualQC | None = None, min_visual_score: float = 0.72,
                 diagnostic_slate: bool = False) -> None:
        self.ctx = ctx
        self.media = FFmpegToolchain()
        self.visual_qc = visual_qc
        self.min_visual_score = min_visual_score
        self.diagnostic_slate = diagnostic_slate

    @staticmethod
    def _prompt(kind: str, item, bible: AssetBibleSpec) -> tuple[str, str]:
        if kind == "character":
            pos = (
                f"Canonical character reference sheet for {item.name}. Identity lock: {item.identity_lock}. "
                f"Appearance: {item.appearance}. Body: {item.body or 'natural consistent proportions'}. "
                f"Hair: {item.hair or 'keep exactly consistent'}. Expressions: {', '.join(item.expression_set) or 'neutral'}. "
                f"Style: {bible.visual_style_lock}. Neutral readable lighting, identity-first, no dramatic reinterpretation."
            )
            neg = "different person, celebrity likeness, face drift, age drift, hairstyle drift, extra limbs, text, watermark"
        elif kind == "scene":
            pos = (
                f"Canonical empty environment reference for {item.name}. Topology lock: {item.topology_lock}. "
                f"Lighting anchors: {', '.join(item.lighting_anchors) or 'consistent motivated lighting'}. "
                f"Style: {bible.visual_style_lock}. No people. Preserve doors, windows, furniture and spatial anchors."
            )
            neg = "people, changed room geometry, impossible architecture, random doors, text, watermark"
        else:
            pos = (
                f"Canonical prop reference for {item.name}. Identity lock: {item.identity_lock}. "
                f"Required states: {', '.join(item.states) or 'default'}. Style: {bible.visual_style_lock}. "
                f"Neutral product-style reference, stable scale, material and visible faces."
            )
            neg = "different object, shape drift, unreadable geometry, hands, text, watermark"
        return pos, neg

    def _score_visual(self, path: Path, contract: dict) -> tuple[bool, float, list[str]]:
        if self.visual_qc is None:
            if self.diagnostic_slate:
                return True, 0.0, ["DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED"]
            return False, 0.0, ["VISUAL_QC_MISSING_FAIL_CLOSED"]
        r = self.visual_qc.review(path, contract)
        passed, scores, findings = normalized_visual_review(r, min_score=self.min_visual_score)
        return passed, sum(scores.values()) / 4, findings

    def build(
        self,
        project_id: str,
        bible: AssetBibleSpec,
        root: Path,
        *,
        mode: str,
        workflow_id: str | None = None,
        workflow_version: str = "1",
        candidates_per_asset: int = 2,
        width: int = 1024,
        height: int = 1024,
    ) -> AssetFactoryReport:
        if self.visual_qc is None and (mode != "slate" or not self.diagnostic_slate):
            raise RuntimeError("VISUAL_QC_MISSING_FAIL_CLOSED: only explicitly diagnostic slate can bypass visual assessment")
        if self.diagnostic_slate and mode != "slate":
            raise ValueError("Diagnostic slate bypass is forbidden for generative media")
        out_root = root / "assets" / "generated"
        out_root.mkdir(parents=True, exist_ok=True)
        candidates: list[AssetCandidate] = []
        selections: list[CanonicalAssetSelection] = []
        comfy = self.ctx.executors.get("local.comfyui") if mode == "comfyui" else None
        image_pipe = ComfyImagePipeline(self.ctx.workflows) if mode == "comfyui" else None
        if mode == "comfyui":
            if not workflow_id:
                raise RuntimeError("asset workflow id required for ComfyUI AssetFactory")
            manifest = self.ctx.workflows.get(workflow_id, workflow_version)
            if not manifest.model_revision:
                raise RuntimeError(f"Workflow {workflow_id}@{workflow_version} must pin model_revision before production")
            self.ctx.models.require_approved(manifest.model_id, manifest.model_revision)

        items = [("character", x.character_id, x) for x in bible.characters]
        items += [("scene", x.location_id, x) for x in bible.scenes]
        items += [("prop", x.prop_id, x) for x in bible.props]

        for kind, key, item in items:
            pos, neg = self._prompt(kind, item, bible)
            local: list[AssetCandidate] = []
            for i in range(max(1, candidates_per_asset)):
                cid = f"{key}_C{i+1:02d}"
                if mode == "slate":
                    path = self.media.make_image_slate(f"{kind.upper()} {key} | candidate {i+1}", out_root / kind / f"{cid}.png", size=f"{width}x{height}")
                    seed = None
                elif mode == "comfyui":
                    if not workflow_id:
                        raise RuntimeError("asset workflow id required for ComfyUI AssetFactory")
                    built = image_pipe.payload(prompt=pos, negative=neg, workflow_id=workflow_id, workflow_version=workflow_version, width=width, height=height, asset_id=key)
                    result = comfy.execute({
                        "workflow": built.workflow,
                        "output_dir": str(out_root / kind / cid),
                        "seed": built.seed,
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "model_id": manifest.model_id,
                        "model_revision": manifest.model_revision,
                    })
                    if not result.ok:
                        local.append(AssetCandidate(candidate_id=cid, asset_key=key, asset_kind=kind, path="", prompt=pos, technical_pass=False, visual_pass=False, visual_score=0, findings=[result.error or "ASSET_RENDER_FAILED"], seed=built.seed))
                        continue
                    image_paths = [Path(x) for x in result.artifacts if Path(x).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".avif"}]
                    if not image_paths:
                        local.append(AssetCandidate(candidate_id=cid, asset_key=key, asset_kind=kind, path="", prompt=pos, technical_pass=False, visual_pass=False, visual_score=0, findings=["ASSET_OUTPUT_MISSING"], seed=built.seed))
                        continue
                    path = image_paths[0]; seed = built.seed
                else:
                    raise ValueError("asset mode must be slate or comfyui")

                passed, score, findings = self._score_visual(path, {"kind": kind, "asset_key": key, "spec": item.model_dump(mode="json"), "visual_style_lock": bible.visual_style_lock})
                rec = AssetCandidate(candidate_id=cid, asset_key=key, asset_kind=kind, path=str(path), prompt=pos, technical_pass=True, visual_pass=passed, visual_score=score, findings=findings, seed=seed)
                local.append(rec); candidates.append(rec)

            eligible = [x for x in local if x.technical_pass and x.visual_pass and x.path]
            if not eligible:
                continue
            selected = max(eligible, key=lambda x: (x.visual_score, x.candidate_id))
            rejections = [x.candidate_id for x in local if x.candidate_id != selected.candidate_id]
            selections.append(CanonicalAssetSelection(asset_key=key, asset_kind=kind, selected_candidate_id=selected.candidate_id, selected_path=selected.path, score=selected.visual_score, rejected_candidate_ids=rejections))

            data = Path(selected.path).read_bytes()
            record = AssetRecord(
                asset_id=f"CANON_{project_id}_{key}", asset_type=f"canonical_{kind}_reference", origin="local_generation",
                source=selected.path, creator="CineFactory Local AssetFactory", rights_status=RightsStatus.GREEN,
                rights=RightsEnvelope(commercial_use=True, notes=["Locally generated. Production use still requires the exact model/workflow to be approved in ModelRegistry/WorkflowRegistry."]),
                content_hash=sha256(data).hexdigest(), metadata={"candidate_id": selected.candidate_id, "score": selected.visual_score},
            )
            self.ctx.assets.save(project_id, record)
            if kind == "character": item.reference_asset_ids[:] = [record.asset_id]
            elif kind == "scene": item.reference_asset_ids[:] = [record.asset_id]
            else: item.reference_asset_ids[:] = [record.asset_id]

        expected = len(items)
        passed = len(selections) == expected
        findings = [] if passed else [f"CANONICAL_ASSET_SELECTION_INCOMPLETE:{len(selections)}/{expected}"]
        return AssetFactoryReport(passed=passed, selections=selections, candidates=candidates, findings=findings)
