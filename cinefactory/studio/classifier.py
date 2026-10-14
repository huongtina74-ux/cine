from __future__ import annotations

from cinefactory.studio.contracts import CapabilityKind, MediaFormat, MediaPurpose, StudioProject


class UniversalMediaClassifier:
    """Deterministic first-pass classifier; creative reasoning may refine its result."""

    def classify(
        self,
        goal: str,
        *,
        language: str = "vi",
        duration_seconds: int | None = None,
        platform: str = "youtube",
    ) -> StudioProject:
        text = goal.lower()
        media_format = self._format(text)
        purpose = self._purpose(text, media_format)
        domain = self._domain(text)
        project = StudioProject(
            goal=goal,
            domain=domain,
            purpose=purpose,
            media_format=media_format,
        )
        project.output.language = language
        project.output.duration_seconds = duration_seconds
        project.output.platform = platform
        project.requested_capabilities = self._capabilities(media_format, text)
        return project
    @staticmethod
    def _format(text: str) -> MediaFormat:
        rules = [
            (("tutorial", "how to", "hướng dẫn", "screen recording"), MediaFormat.TUTORIAL),
            (("documentary", "tài liệu"), MediaFormat.DOCUMENTARY),
            (("review", "đánh giá"), MediaFormat.REVIEW),
            (("podcast",), MediaFormat.PODCAST),
            (("interview", "phỏng vấn"), MediaFormat.INTERVIEW),
            (("commercial", "advertisement", "quảng cáo", "product ad"), MediaFormat.COMMERCIAL),
            (("music video", "mv ", "lyric video"), MediaFormat.MUSIC_VIDEO),
            (("gameplay", "100 days", "survival challenge", "play the game"), MediaFormat.GAMEPLAY),
            (("explainer", "explain", "giải thích"), MediaFormat.EXPLAINER),
            (("data visualization", "chart", "dashboard"), MediaFormat.DATA_VISUALIZATION),
            (("screen demo", "software demo", "app demo"), MediaFormat.SCREEN_DEMO),
            (("shorts", "short-form", "tiktok", "reels"), MediaFormat.SHORT_FORM),
            (("animation", "animated", "hoạt hình"), MediaFormat.ANIMATION),
        ]
        for needles, media_format in rules:
            if any(needle in text for needle in needles):
                return media_format
        return MediaFormat.NARRATIVE_FILM

    @staticmethod
    def _purpose(text: str, media_format: MediaFormat) -> MediaPurpose:
        if media_format in {MediaFormat.TUTORIAL, MediaFormat.EXPLAINER}:
            return MediaPurpose.TEACH
        if media_format in {MediaFormat.DOCUMENTARY, MediaFormat.REVIEW, MediaFormat.DATA_VISUALIZATION}:
            return MediaPurpose.INFORM
        if media_format is MediaFormat.COMMERCIAL:
            return MediaPurpose.SELL
        if any(word in text for word in ("inform", "news", "analysis")):
            return MediaPurpose.INFORM
        return MediaPurpose.ENTERTAIN

    @staticmethod
    def _domain(text: str) -> str:
        domains = [
            ("minecraft", "gaming.minecraft"),
            ("roblox", "gaming.roblox"),
            ("finance", "finance"),
            ("insurance", "finance.insurance"),
            ("history", "history"),
            ("science", "science"),
            ("technology", "technology"),
            ("software", "technology.software"),
            ("product", "commercial.product"),
        ]
        for needle, domain in domains:
            if needle in text:
                return domain
        return "general"

    @staticmethod
    def _capabilities(media_format: MediaFormat, text: str) -> set[CapabilityKind]:
        base = {CapabilityKind.EDITORIAL, CapabilityKind.SPEECH, CapabilityKind.QC}
        mapping = {
            MediaFormat.GAMEPLAY: {CapabilityKind.GAME_RUNTIME, CapabilityKind.SCREEN_CAPTURE},
            MediaFormat.ANIMATION: {CapabilityKind.OFFLINE_3D},
            MediaFormat.NARRATIVE_FILM: {CapabilityKind.OFFLINE_3D},
            MediaFormat.DOCUMENTARY: {CapabilityKind.WEB_RESEARCH, CapabilityKind.FOOTAGE, CapabilityKind.MOTION_GRAPHICS},
            MediaFormat.TUTORIAL: {CapabilityKind.SCREEN_CAPTURE, CapabilityKind.MOTION_GRAPHICS},
            MediaFormat.EXPLAINER: {CapabilityKind.MOTION_GRAPHICS},
            MediaFormat.COMMERCIAL: {CapabilityKind.DESIGN, CapabilityKind.MOTION_GRAPHICS},
            MediaFormat.SCREEN_DEMO: {CapabilityKind.SCREEN_CAPTURE},
            MediaFormat.DATA_VISUALIZATION: {CapabilityKind.MOTION_GRAPHICS},
            MediaFormat.MUSIC_VIDEO: {CapabilityKind.MUSIC},
        }
        base |= mapping.get(media_format, set())
        if "unreal" in text:
            base.add(CapabilityKind.REALTIME_3D)
        if "ai video" in text:
            base.add(CapabilityKind.AI_VIDEO)
        if "ai image" in text:
            base.add(CapabilityKind.AI_IMAGE)
        return base
