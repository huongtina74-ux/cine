from __future__ import annotations

import random
from dataclasses import dataclass

from cinefactory.workflows.compiler import WorkflowTemplateCompiler


@dataclass(frozen=True)
class ComfyImagePayload:
    workflow: dict
    prompt: str
    negative: str
    seed: int


class ComfyImagePipeline:
    """Generic local ComfyUI image/keyframe compiler using pinned workflow templates."""

    def __init__(self, workflows) -> None:
        self.workflows = workflows
        self.templates = WorkflowTemplateCompiler()

    def payload(
        self,
        *,
        prompt: str,
        negative: str,
        workflow_id: str,
        workflow_version: str,
        seed: int | None = None,
        width: int = 1024,
        height: int = 1024,
        input_image: str = "",
        reference_images: list[str] | None = None,
        asset_id: str = "",
    ) -> ComfyImagePayload:
        manifest = self.workflows.get(workflow_id, workflow_version)
        if not manifest.local_only:
            raise RuntimeError("Production workflow is not marked local_only")
        if manifest.media_type.lower() not in {"image", "keyframe", "still"}:
            raise RuntimeError(f"Workflow {workflow_id}@{workflow_version} is not an image/keyframe workflow")
        seed = seed if seed is not None else random.SystemRandom().randint(1, 2**31 - 1)
        template = self.workflows.read_workflow_json(workflow_id, workflow_version)
        refs = list(reference_images or [])
        values = {
            "PROMPT": prompt,
            "NEGATIVE": negative,
            "SEED": seed,
            "WIDTH": width,
            "HEIGHT": height,
            "INPUT_IMAGE": input_image or (refs[0] if refs else ""),
            "REFERENCE_IMAGES_JSON": __import__("json").dumps(refs, ensure_ascii=False),
            "ASSET_ID": asset_id,
        }
        for i in range(1, 10):
            values[f"REFERENCE_IMAGE_{i}"] = refs[i-1] if len(refs) >= i else ""
        workflow = self.templates.compile(template, values)
        return ComfyImagePayload(workflow=workflow, prompt=prompt, negative=negative, seed=seed)
