from __future__ import annotations

import random
from dataclasses import dataclass

from cinefactory.domain.models import AssetBibleSpec, ShotSpec
from cinefactory.prompts.compiler import ShotPromptCompiler
from cinefactory.workflows.compiler import WorkflowTemplateCompiler


@dataclass(frozen=True)
class ComfyRenderPayload:
    workflow: dict
    positive: str
    negative: str
    seed: int


class ComfyShotPipeline:
    def __init__(self, workflows, prompt_compiler: ShotPromptCompiler | None = None) -> None:
        self.workflows = workflows
        self.prompts = prompt_compiler or ShotPromptCompiler()
        self.templates = WorkflowTemplateCompiler()

    def payload(
        self,
        shot: ShotSpec,
        bible: AssetBibleSpec,
        *,
        workflow_id: str,
        workflow_version: str,
        seed: int | None = None,
        width: int = 1280,
        height: int = 720,
        input_image: str = "",
        reference_images: list[str] | None = None,
        repair_hint: str | None = None,
    ) -> ComfyRenderPayload:
        manifest = self.workflows.get(workflow_id, workflow_version)
        if not manifest.local_only:
            raise RuntimeError("Production workflow is not marked local_only")
        prompt = self.prompts.compile_video(shot, bible, repair_hint=repair_hint)
        seed = seed if seed is not None else random.SystemRandom().randint(1, 2**31 - 1)
        template = self.workflows.read_workflow_json(workflow_id, workflow_version)
        refs = list(reference_images or [])
        values = {
            "PROMPT": prompt.positive,
            "NEGATIVE": prompt.negative,
            "SEED": seed,
            "WIDTH": width,
            "HEIGHT": height,
            "DURATION": shot.duration_seconds,
            "INPUT_IMAGE": input_image,
            "REFERENCE_IMAGES_JSON": __import__("json").dumps(refs, ensure_ascii=False),
            "SHOT_ID": shot.shot_id,
        }
        for i in range(1, 10):
            values[f"REFERENCE_IMAGE_{i}"] = refs[i-1] if len(refs) >= i else ""
        workflow = self.templates.compile(template, values)
        return ComfyRenderPayload(workflow=workflow, positive=prompt.positive, negative=prompt.negative, seed=seed)
