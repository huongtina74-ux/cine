from __future__ import annotations

import re

from .contracts import (
    CapabilityKind,
    MediaFormat,
    MediaProductSpec,
    MediaPurpose,
    MediaSegment,
    SegmentKind,
)


class UniversalMediaClassifier:
    """Deterministic first-pass classifier. Reasoning agents may refine later."""

    def classify(self, prompt: str) -> MediaProductSpec:
        t = prompt.lower()

        if any(x in t for x in ("tutorial", "how to", "hướng dẫn", "screen recording", "record my screen")):
            return MediaProductSpec(
                purpose=MediaPurpose.TEACH,
                format=MediaFormat.TUTORIAL,
                evidence_required=True,
                story_required=False,
                source_modalities=["screen_capture", "voice", "motion_graphics"],
                output_profile="YOUTUBE_LONGFORM",
            )
        if any(x in t for x in ("documentary", "tài liệu", "history", "lịch sử", "investigation", "điều tra")):
            return MediaProductSpec(
                purpose=MediaPurpose.INFORM,
                format=MediaFormat.DOCUMENTARY,
                evidence_required=True,
                story_required=False,
                source_modalities=["footage", "voice", "motion_graphics", "ai_visual"],
            )
        if any(x in t for x in ("review", "đánh giá", "comparison", "so sánh")):
            return MediaProductSpec(
                purpose=MediaPurpose.INFORM,
                format=MediaFormat.REVIEW,
                evidence_required=True,
                story_required=False,
                source_modalities=["footage", "screen_capture", "voice", "graphics"],
            )
        if any(x in t for x in ("podcast", "talk show")):
            return MediaProductSpec(
                purpose=MediaPurpose.ENGAGE,
                format=MediaFormat.PODCAST,
                story_required=False,
                source_modalities=["voice", "multicam", "graphics"],
            )
        if any(x in t for x in ("interview", "phỏng vấn")):
            return MediaProductSpec(
                purpose=MediaPurpose.INFORM,
                format=MediaFormat.INTERVIEW,
                story_required=False,
                source_modalities=["camera", "voice", "graphics"],
            )
        if any(x in t for x in ("commercial", "advertisement", "quảng cáo", "product ad", "tvc")):
            return MediaProductSpec(
                purpose=MediaPurpose.PERSUADE,
                format=MediaFormat.COMMERCIAL,
                brand_compliance_required=True,
                story_required=False,
                source_modalities=["3d", "ai_visual", "motion_graphics", "voice"],
            )
        if any(x in t for x in ("music video", "mv ", "lyric video")):
            return MediaProductSpec(
                purpose=MediaPurpose.ENTERTAIN,
                format=MediaFormat.MUSIC_VIDEO,
                story_required=False,
                source_modalities=["performance", "ai_visual", "3d", "music"],
            )
        if any(x in t for x in ("shorts", "tiktok", "reel", "short-form", "short form")):
            return MediaProductSpec(
                purpose=MediaPurpose.ENGAGE,
                format=MediaFormat.SOCIAL_SHORT,
                story_required=False,
                source_modalities=["hybrid", "captions", "voice"],
                output_profile="VERTICAL_SHORT",
            )
        long_slide_intent = any(
            x in t
            for x in (
                "long slide",
                "long slice",
                "animal fountain",
                "fountain crossing",
                "paint animals",
                "animal crossing animation",
                "3d animal game",
                "funanimation",
            )
        )
        if long_slide_intent:
            return MediaProductSpec(
                purpose=MediaPurpose.ENTERTAIN,
                format=MediaFormat.ANIMATION,
                story_required=False,
                source_modalities=["3d", "sfx", "editorial"],
                constraints={
                    "domain": "animation.animal_long_slide",
                    "vertical": "animal_long_slide",
                    "procedural_animation": True,
                    "game_runtime_required": False,
                    "dialogue_required": False,
                },
            )
        animation_intent = any(
            x in t
            for x in (
                "animation",
                "animated",
                "hoạt hình",
                "animated story",
                "cinematic story",
                "animated cinematic",
                "minecraft movie",
                "roblox movie",
            )
        )
        gameplay_intent = any(
            x in t
            for x in (
                "gameplay",
                "100 days",
                "survival challenge",
                "build battle",
                "play the game",
                "let's play",
                "lets play",
                "walkthrough",
                "speedrun",
            )
        )
        if animation_intent and not gameplay_intent:
            domain = (
                "gaming.minecraft"
                if "minecraft" in t
                else "gaming.roblox"
                if "roblox" in t
                else "animation"
            )
            return MediaProductSpec(
                purpose=MediaPurpose.ENTERTAIN,
                format=MediaFormat.ANIMATION,
                story_required=True,
                source_modalities=["3d", "voice", "editorial"],
                constraints={"domain": domain, "game_runtime_required": False},
            )
        if gameplay_intent:
            domain = (
                "gaming.minecraft"
                if "minecraft" in t
                else "gaming.roblox"
                if "roblox" in t
                else "gaming"
            )
            return MediaProductSpec(
                purpose=MediaPurpose.ENTERTAIN,
                format=MediaFormat.GAMEPLAY,
                actual_gameplay_required=True,
                story_required=False,
                source_modalities=["game_runtime", "voice", "editorial"],
                constraints={"domain": domain, "game_runtime_required": True},
            )
        if any(x in t for x in ("explain", "giải thích", "explainer", "whiteboard", "animated chart")):
            return MediaProductSpec(
                purpose=MediaPurpose.INFORM,
                format=MediaFormat.EXPLAINER,
                evidence_required=True,
                story_required=False,
                source_modalities=["voice", "motion_graphics", "ai_visual"],
            )
        return MediaProductSpec(
            purpose=MediaPurpose.ENTERTAIN,
            format=MediaFormat.NARRATIVE,
            story_required=True,
            source_modalities=["3d", "ai_visual", "voice", "editorial"],
        )
class FormatDirector:
    """Compiles a media product into format-appropriate segment grammar."""

    GRAMMARS: dict[MediaFormat, list[tuple[SegmentKind, str]]] = {
        MediaFormat.NARRATIVE: [
            (SegmentKind.NARRATIVE_SCENE, "Hook"),
            (SegmentKind.NARRATIVE_SCENE, "Setup"),
            (SegmentKind.NARRATIVE_SCENE, "Goal and conflict"),
            (SegmentKind.NARRATIVE_SCENE, "Escalation"),
            (SegmentKind.NARRATIVE_SCENE, "Reversal"),
            (SegmentKind.NARRATIVE_SCENE, "Climax"),
            (SegmentKind.NARRATIVE_SCENE, "Payoff"),
        ],
        MediaFormat.ANIMATION: [
            (SegmentKind.NARRATIVE_SCENE, "Hook"),
            (SegmentKind.NARRATIVE_SCENE, "Setup"),
            (SegmentKind.NARRATIVE_SCENE, "Goal and conflict"),
            (SegmentKind.NARRATIVE_SCENE, "Escalation"),
            (SegmentKind.NARRATIVE_SCENE, "Reversal"),
            (SegmentKind.NARRATIVE_SCENE, "Climax"),
            (SegmentKind.NARRATIVE_SCENE, "Payoff"),
        ],
        MediaFormat.GAMEPLAY: [
            (SegmentKind.GAMEPLAY_BEAT, "Objective"),
            (SegmentKind.GAMEPLAY_BEAT, "Early progress"),
            (SegmentKind.GAMEPLAY_BEAT, "Obstacle"),
            (SegmentKind.GAMEPLAY_BEAT, "Adaptation"),
            (SegmentKind.GAMEPLAY_BEAT, "Escalation"),
            (SegmentKind.GAMEPLAY_BEAT, "Final test"),
            (SegmentKind.GAMEPLAY_BEAT, "Result and reaction"),
        ],
        MediaFormat.DOCUMENTARY: [
            (SegmentKind.DOCUMENTARY_CHAPTER, "Question"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Context"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Evidence"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Complication"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Investigation"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Synthesis"),
            (SegmentKind.DOCUMENTARY_CHAPTER, "Resolution"),
        ],
        MediaFormat.TUTORIAL: [
            (SegmentKind.TUTORIAL_STEP, "Problem and promise"),
            (SegmentKind.TUTORIAL_STEP, "Prerequisites"),
            (SegmentKind.SCREEN_DEMO, "Demonstration step 1"),
            (SegmentKind.SCREEN_DEMO, "Demonstration step 2"),
            (SegmentKind.TUTORIAL_STEP, "Verification"),
            (SegmentKind.TUTORIAL_STEP, "Common failures and recovery"),
            (SegmentKind.TUTORIAL_STEP, "Result"),
        ],
        MediaFormat.EXPLAINER: [
            (SegmentKind.EXPLAINER_CONCEPT, "Question"),
            (SegmentKind.EXPLAINER_CONCEPT, "Mental model"),
            (SegmentKind.DATA_VISUALIZATION, "Evidence or example"),
            (SegmentKind.EXPLAINER_CONCEPT, "Mechanism"),
            (SegmentKind.EXPLAINER_CONCEPT, "Implication"),
        ],
        MediaFormat.REVIEW: [
            (SegmentKind.REVIEW_BLOCK, "Review question"),
            (SegmentKind.REVIEW_BLOCK, "Criteria"),
            (SegmentKind.REVIEW_BLOCK, "Evidence and tests"),
            (SegmentKind.REVIEW_BLOCK, "Tradeoffs"),
            (SegmentKind.REVIEW_BLOCK, "Use-case conclusion"),
        ],
        MediaFormat.COMMERCIAL: [
            (SegmentKind.AD_BEAT, "Attention"),
            (SegmentKind.AD_BEAT, "Problem or desire"),
            (SegmentKind.AD_BEAT, "Product reveal"),
            (SegmentKind.AD_BEAT, "Proof"),
            (SegmentKind.AD_BEAT, "Payoff"),
            (SegmentKind.AD_BEAT, "Call to action"),
        ],
        MediaFormat.PODCAST: [
            (SegmentKind.PODCAST_BLOCK, "Cold open"),
            (SegmentKind.PODCAST_BLOCK, "Topic framing"),
            (SegmentKind.PODCAST_BLOCK, "Discussion"),
            (SegmentKind.PODCAST_BLOCK, "Key insight"),
            (SegmentKind.PODCAST_BLOCK, "Close"),
        ],
        MediaFormat.INTERVIEW: [
            (SegmentKind.INTERVIEW_TURN, "Introduction"),
            (SegmentKind.INTERVIEW_TURN, "Opening question"),
            (SegmentKind.INTERVIEW_TURN, "Deepening questions"),
            (SegmentKind.INTERVIEW_TURN, "Key insight"),
            (SegmentKind.INTERVIEW_TURN, "Close"),
        ],
        MediaFormat.MUSIC_VIDEO: [
            (SegmentKind.MUSIC_SECTION, "Intro"),
            (SegmentKind.MUSIC_SECTION, "Verse"),
            (SegmentKind.MUSIC_SECTION, "Chorus"),
            (SegmentKind.MUSIC_SECTION, "Bridge"),
            (SegmentKind.MUSIC_SECTION, "Peak"),
            (SegmentKind.MUSIC_SECTION, "Outro"),
        ],
        MediaFormat.SOCIAL_SHORT: [
            (SegmentKind.NARRATIVE_SCENE, "Immediate hook"),
            (SegmentKind.NARRATIVE_SCENE, "Fast setup"),
            (SegmentKind.NARRATIVE_SCENE, "Value or escalation"),
            (SegmentKind.NARRATIVE_SCENE, "Payoff"),
        ],
    }

    def compile(self, product: MediaProductSpec, *, duration_seconds: int | None = None) -> list[MediaSegment]:
        grammar = self.GRAMMARS.get(product.format)
        if not grammar:
            grammar = [(SegmentKind.NARRATIVE_SCENE, "Hybrid segment")]

        total = float(duration_seconds or max(30, len(grammar) * 20))
        each = total / len(grammar)
        segments: list[MediaSegment] = []
        for idx, (kind, purpose) in enumerate(grammar):
            requirements = self._capabilities(product, kind)
            segments.append(
                MediaSegment(
                    segment_id=f"SEG_{idx + 1:03d}",
                    kind=kind,
                    purpose=purpose,
                    order=idx,
                    duration_seconds=round(each, 3),
                    dependencies=[] if idx == 0 else [f"SEG_{idx:03d}"],
                    capability_requirements=requirements,
                    creative_intent={"format": product.format.value, "beat": purpose},
                    execution_constraints={
                        "evidence_required": product.evidence_required,
                        "actual_gameplay_required": product.actual_gameplay_required,
                    },
                )
            )
        return segments

    def compile_outline(self, project):
        from .segments import MediaSegment as GraphSegment, SegmentGraph, SegmentRequirement

        if project.media_format is MediaFormat.TUTORIAL:
            purposes = [
                "Problem and promise",
                "Prerequisites",
                "Demonstration",
                "Verification",
                "Troubleshooting",
                "Result",
            ]
            kind = SegmentKind.TUTORIAL_STEP
            requirements = [
                SegmentRequirement(capability=CapabilityKind.SPEECH),
                SegmentRequirement(capability=CapabilityKind.EDITORIAL),
            ]
        elif project.media_format is MediaFormat.GAMEPLAY:
            purposes = ["Objective", "Progress", "Obstacle", "Adaptation", "Final test", "Result"]
            kind = SegmentKind.GAMEPLAY_BEAT
            requirements = [
                SegmentRequirement(capability=CapabilityKind.GAME_RUNTIME),
                SegmentRequirement(capability=CapabilityKind.EDITORIAL),
            ]
        elif project.media_format is MediaFormat.DOCUMENTARY:
            purposes = ["Question", "Context", "Evidence", "Complication", "Synthesis", "Resolution"]
            kind = SegmentKind.DOCUMENTARY_CHAPTER
            requirements = [
                SegmentRequirement(capability=CapabilityKind.FOOTAGE),
                SegmentRequirement(capability=CapabilityKind.SPEECH),
                SegmentRequirement(capability=CapabilityKind.EDITORIAL),
            ]
        else:
            purposes = ["Hook", "Setup", "Development", "Payoff"]
            kind = SegmentKind.NARRATIVE_SCENE
            requirements = [
                SegmentRequirement(capability=CapabilityKind.OFFLINE_3D),
                SegmentRequirement(capability=CapabilityKind.EDITORIAL),
            ]

        segments = []
        for idx, purpose in enumerate(purposes):
            segments.append(
                GraphSegment(
                    segment_id=f"SEG_{idx + 1:03d}",
                    kind=kind,
                    purpose=purpose,
                    dependencies=[] if idx == 0 else [f"SEG_{idx:03d}"],
                    requirements=[item.model_copy(deep=True) for item in requirements],
                )
            )
        return SegmentGraph(segments=segments)

    @staticmethod
    def _capabilities(product: MediaProductSpec, kind: SegmentKind) -> list[CapabilityKind]:
        if kind is SegmentKind.SCREEN_DEMO:
            return [CapabilityKind.SCREEN_CAPTURE, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.DATA_VISUALIZATION:
            return [CapabilityKind.MOTION_GRAPHICS, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.GAMEPLAY_BEAT:
            return [CapabilityKind.GAME_RUNTIME, CapabilityKind.EDITORIAL]
        if kind in {SegmentKind.PODCAST_BLOCK, SegmentKind.INTERVIEW_TURN}:
            return [CapabilityKind.SPEECH, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.MUSIC_SECTION:
            return [CapabilityKind.MUSIC, CapabilityKind.AI_VIDEO, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.AD_BEAT:
            return [CapabilityKind.OFFLINE_3D, CapabilityKind.MOTION_GRAPHICS, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.DOCUMENTARY_CHAPTER:
            return [CapabilityKind.FOOTAGE, CapabilityKind.SPEECH, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.EXPLAINER_CONCEPT:
            return [CapabilityKind.SPEECH, CapabilityKind.MOTION_GRAPHICS, CapabilityKind.EDITORIAL]
        if kind is SegmentKind.TUTORIAL_STEP:
            return [CapabilityKind.SPEECH, CapabilityKind.EDITORIAL]
        return [CapabilityKind.OFFLINE_3D, CapabilityKind.EDITORIAL]
