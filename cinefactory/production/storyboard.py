from __future__ import annotations

from pathlib import Path

from cinefactory.domain.models import AssetBibleSpec, ShotSpec
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.production.contracts import KeyframeCandidate, StoryboardGateReport, StoryboardShotApproval
from cinefactory.production.image_pipeline import ComfyImagePipeline
from cinefactory.prompts.compiler import ShotPromptCompiler
from cinefactory.qc.visual_command import CommandVisualQC
from cinefactory.qc.visual_policy import normalized_visual_review


class StoryboardGate:
    """Generate/approve a locked keyframe before any video take is allowed."""

    def __init__(self, ctx, *, visual_qc: CommandVisualQC | None = None, min_visual_score: float = 0.72,
                 diagnostic_slate: bool = False) -> None:
        self.ctx = ctx
        self.media = FFmpegToolchain()
        self.prompts = ShotPromptCompiler()
        self.visual_qc = visual_qc
        self.min_visual_score = min_visual_score
        self.diagnostic_slate = diagnostic_slate

    def _review(self, path: Path, shot: ShotSpec) -> tuple[bool, float, list[str]]:
        if self.visual_qc is None:
            if self.diagnostic_slate:
                return True, 0.0, ["DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED"]
            return False, 0.0, ["VISUAL_QC_MISSING_FAIL_CLOSED"]
        r = self.visual_qc.review(path, {"kind": "storyboard_keyframe", "shot": shot.model_dump(mode="json")})
        passed, scores, findings = normalized_visual_review(r, min_score=self.min_visual_score)
        return passed, sum(scores.values()) / 4, findings


    def _reference_paths(self, shot: ShotSpec, bible: AssetBibleSpec) -> list[str]:
        ids: list[str] = []
        char_ids = set(shot.performance) | set(shot.entry_state.characters)
        for item in bible.characters:
            if item.character_id in char_ids:
                ids.extend(item.reference_asset_ids)
        for item in bible.scenes:
            if item.location_id == shot.entry_state.location_id:
                ids.extend(item.reference_asset_ids)
        prop_ids = set(shot.entry_state.props)
        for state in shot.entry_state.characters.values():
            prop_ids.update(state.held_props)
        for item in bible.props:
            if item.prop_id in prop_ids:
                ids.extend(item.reference_asset_ids)
        paths: list[str] = []
        for asset_id in ids:
            try:
                rec = self.ctx.assets.get(asset_id)
            except KeyError:
                continue
            if rec.source and rec.source not in paths:
                paths.append(rec.source)
        return paths

    def build(
        self,
        shots: list[ShotSpec],
        bible: AssetBibleSpec,
        root: Path,
        *,
        mode: str,
        workflow_id: str | None = None,
        workflow_version: str = "1",
        candidates_per_shot: int = 2,
        width: int = 1280,
        height: int = 720,
    ) -> StoryboardGateReport:
        if self.visual_qc is None and (mode != "slate" or not self.diagnostic_slate):
            raise RuntimeError("VISUAL_QC_MISSING_FAIL_CLOSED: storyboard visual validation is required")
        if self.diagnostic_slate and mode != "slate":
            raise ValueError("Diagnostic slate bypass cannot authorize generative storyboard")
        out = root / "storyboard" / "keyframes"
        out.mkdir(parents=True, exist_ok=True)
        approvals: list[StoryboardShotApproval] = []
        comfy = self.ctx.executors.get("local.comfyui") if mode == "comfyui" else None
        pipe = ComfyImagePipeline(self.ctx.workflows) if mode == "comfyui" else None
        if mode == "comfyui":
            if not workflow_id:
                raise RuntimeError("keyframe workflow id required for ComfyUI StoryboardGate")
            manifest = self.ctx.workflows.get(workflow_id, workflow_version)
            if not manifest.model_revision:
                raise RuntimeError(f"Workflow {workflow_id}@{workflow_version} must pin model_revision before production")
            self.ctx.models.require_approved(manifest.model_id, manifest.model_revision)

        for shot in shots:
            compiled = self.prompts.compile_keyframe(shot, bible)
            reference_images = self._reference_paths(shot, bible)
            candidates: list[KeyframeCandidate] = []
            for i in range(max(1, candidates_per_shot)):
                cid = f"{shot.shot_id}_KF{i+1:02d}"
                if mode == "slate":
                    path = self.media.make_image_slate(
                        f"{shot.shot_id} | {shot.camera.shot_size} | {shot.camera.narrative_purpose[:48]}",
                        out / f"{cid}.png", size=f"{width}x{height}",
                    )
                    seed = None
                elif mode == "comfyui":
                    if not workflow_id:
                        raise RuntimeError("keyframe workflow id required for ComfyUI StoryboardGate")
                    built = pipe.payload(
                        prompt=compiled.positive, negative=compiled.negative,
                        workflow_id=workflow_id, workflow_version=workflow_version,
                        width=width, height=height, reference_images=reference_images, asset_id=shot.shot_id,
                    )
                    result = comfy.execute({
                        "workflow": built.workflow,
                        "output_dir": str(out / cid),
                        "seed": built.seed,
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "model_id": manifest.model_id,
                        "model_revision": manifest.model_revision,
                    })
                    if not result.ok:
                        candidates.append(KeyframeCandidate(candidate_id=cid, shot_id=shot.shot_id, path="", prompt=compiled.positive, visual_pass=False, visual_score=0, findings=[result.error or "KEYFRAME_RENDER_FAILED"], seed=built.seed))
                        continue
                    image_paths = [Path(x) for x in result.artifacts if Path(x).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".avif"}]
                    if not image_paths:
                        candidates.append(KeyframeCandidate(candidate_id=cid, shot_id=shot.shot_id, path="", prompt=compiled.positive, visual_pass=False, visual_score=0, findings=["KEYFRAME_OUTPUT_MISSING"], seed=built.seed))
                        continue
                    path = image_paths[0]; seed = built.seed
                else:
                    raise ValueError("storyboard mode must be slate or comfyui")

                passed, score, findings = self._review(path, shot)
                candidates.append(KeyframeCandidate(candidate_id=cid, shot_id=shot.shot_id, path=str(path), prompt=compiled.positive, visual_pass=passed, visual_score=score, findings=findings, seed=seed))

            eligible = [x for x in candidates if x.visual_pass and x.path]
            if not eligible:
                approvals.append(StoryboardShotApproval(shot_id=shot.shot_id, approved=False, findings=sorted({f for x in candidates for f in x.findings}) or ["NO_APPROVED_KEYFRAME"]))
                continue
            best = max(eligible, key=lambda x: (x.visual_score, x.candidate_id))
            approvals.append(StoryboardShotApproval(shot_id=shot.shot_id, approved=True, selected_candidate_id=best.candidate_id, selected_path=best.path, score=best.visual_score))

        failed = [x.shot_id for x in approvals if not x.approved]
        return StoryboardGateReport(passed=not failed, shots=approvals, findings=[f"KEYFRAME_NOT_APPROVED:{x}" for x in failed])
