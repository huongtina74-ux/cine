from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable
from uuid import uuid4

from pydantic import BaseModel, Field


class ResolveRuntimeProbe(BaseModel):
    installed: bool = False
    module_path: str | None = None
    developer_readme: str | None = None
    connected: bool = False
    version: str | None = None
    product_name: str | None = None
    method_surface: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class ResolveOperationEvidence(BaseModel):
    operation: str
    passed: bool
    findings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    duration_ms: int = Field(default=0, ge=0)


class ResolveSandboxResult(BaseModel):
    project_name: str
    connected: bool
    version: str | None = None
    operation_evidence: list[ResolveOperationEvidence] = Field(default_factory=list)
    render_output: str | None = None
    provenance_path: str | None = None
    cleaned_up: bool = False
    findings: list[str] = Field(default_factory=list)


class ResolveRuntimeAdapter:
    """Fail-closed DaVinci Resolve scripting adapter.

    The adapter discovers Blackmagic's locally installed Developer/Scripting module,
    connects through scriptapp("Resolve"), and only exercises methods that the runtime
    actually exposes. It does not use UI automation as a hidden fallback.
    """

    REQUIRED_OPERATIONS = (
        "edit",
        "Fusion comp",
        "color",
        "Fairlight mix",
        "deliver",
    )

    def __init__(
        self,
        root: str | Path,
        *,
        module_override: ModuleType | Any | None = None,
    ) -> None:
        self.root = Path(root)
        self.module_override = module_override

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _callable(obj: Any, name: str) -> bool:
        return obj is not None and callable(getattr(obj, name, None))

    @staticmethod
    def _safe_call(obj: Any, name: str, *args, default=None):
        method = getattr(obj, name, None)
        if not callable(method):
            return default
        try:
            return method(*args)
        except Exception:
            return default

    def discover(self) -> tuple[Path | None, Path | None]:
        program_data = Path(
            os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        )
        roots: list[Path] = []
        env_root = os.environ.get("RESOLVE_SCRIPT_API")
        if env_root:
            roots.append(Path(env_root))
        roots.extend(
            [
                program_data
                / "Blackmagic Design"
                / "DaVinci Resolve"
                / "Support"
                / "Developer"
                / "Scripting",
                program_data
                / "Blackmagic Design"
                / "DaVinci Resolve"
                / "Developer"
                / "Scripting",
            ]
        )
        module_path = None
        readme_path = None
        for root in roots:
            candidate = root / "Modules" / "DaVinciResolveScript.py"
            if module_path is None and candidate.is_file():
                module_path = candidate
            readme = root / "README.txt"
            if readme_path is None and readme.is_file():
                readme_path = readme
        return module_path, readme_path

    def _load_module(self):
        if self.module_override is not None:
            return self.module_override
        try:
            return importlib.import_module("DaVinciResolveScript")
        except ImportError:
            pass
        module_path, _ = self.discover()
        if module_path is None:
            raise RuntimeError("DAVINCI_RESOLVE_SCRIPT_MODULE_NOT_FOUND")
        spec = importlib.util.spec_from_file_location(
            "DaVinciResolveScript",
            module_path,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                f"DAVINCI_RESOLVE_SCRIPT_MODULE_LOAD_FAILED:{module_path}"
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def connect(self):
        module = self._load_module()
        scriptapp = getattr(module, "scriptapp", None)
        if not callable(scriptapp):
            raise RuntimeError("DAVINCI_RESOLVE_SCRIPTAPP_MISSING")
        resolve = scriptapp("Resolve")
        if resolve is None:
            raise RuntimeError("DAVINCI_RESOLVE_RUNTIME_NOT_CONNECTED")
        return resolve

    def probe(self) -> ResolveRuntimeProbe:
        module_path, readme_path = self.discover()
        findings: list[str] = []
        installed = bool(
            (
                Path(
                    os.environ.get(
                        "ProgramFiles",
                        r"C:\Program Files",
                    )
                )
                / "Blackmagic Design"
                / "DaVinci Resolve"
                / "Resolve.exe"
            ).is_file()
            or self.module_override is not None
            or module_path is not None
        )
        try:
            resolve = self.connect()
        except Exception as exc:
            findings.append(f"RUNTIME_UNAVAILABLE:{exc}")
            return ResolveRuntimeProbe(
                installed=installed,
                module_path=str(module_path) if module_path else None,
                developer_readme=str(readme_path) if readme_path else None,
                connected=False,
                findings=findings,
            )

        version = None
        if self._callable(resolve, "GetVersionString"):
            version = self._safe_call(resolve, "GetVersionString")
        if not version and self._callable(resolve, "GetVersion"):
            raw = self._safe_call(resolve, "GetVersion")
            if isinstance(raw, (list, tuple)):
                version = ".".join(str(item) for item in raw)
            elif raw:
                version = str(raw)
        product_name = self._safe_call(
            resolve,
            "GetProductName",
        )
        surface = [
            name
            for name in (
                "GetProjectManager",
                "GetMediaStorage",
                "OpenPage",
                "GetCurrentPage",
            )
            if self._callable(resolve, name)
        ]
        return ResolveRuntimeProbe(
            installed=installed,
            module_path=str(module_path) if module_path else None,
            developer_readme=str(readme_path) if readme_path else None,
            connected=True,
            version=str(version) if version else None,
            product_name=str(product_name) if product_name else None,
            method_surface=surface,
            findings=findings,
        )

    @staticmethod
    def _record(
        operation: str,
        fn: Callable[[], tuple[bool, dict[str, Any], list[str], list[str]]],
    ) -> ResolveOperationEvidence:
        started = time.perf_counter()
        try:
            passed, metadata, findings, artifacts = fn()
        except Exception as exc:
            passed = False
            metadata = {}
            findings = [f"{type(exc).__name__}:{exc}"]
            artifacts = []
        return ResolveOperationEvidence(
            operation=operation,
            passed=passed,
            findings=findings,
            metadata=metadata,
            artifacts=artifacts,
            duration_ms=max(
                0,
                int((time.perf_counter() - started) * 1000),
            ),
        )

    @staticmethod
    def _first_video_item(timeline):
        get_items = getattr(timeline, "GetItemListInTrack", None)
        if not callable(get_items):
            return None
        items = get_items("video", 1)
        if not items:
            return None
        return list(items)[0]

    @staticmethod
    def _fusion_names(item) -> list[str]:
        for name in ("GetFusionCompNameList", "GetFusionCompNames"):
            method = getattr(item, name, None)
            if callable(method):
                result = method()
                if result:
                    return list(result)
        return []

    @staticmethod
    def _pick_render_format(project) -> tuple[str, str] | None:
        get_formats = getattr(project, "GetRenderFormats", None)
        get_codecs = getattr(project, "GetRenderCodecs", None)
        set_format = getattr(project, "SetCurrentRenderFormatAndCodec", None)
        if not (
            callable(get_formats)
            and callable(get_codecs)
            and callable(set_format)
        ):
            return None
        formats = get_formats() or {}
        if not isinstance(formats, dict) or not formats:
            return None
        preferred_formats = []
        for key, value in formats.items():
            label = f"{key} {value}".lower()
            rank = 0 if "mp4" in label else 1
            preferred_formats.append((rank, str(key), value))
        preferred_formats.sort(key=lambda item: (item[0], item[1]))
        for _, format_key, _ in preferred_formats:
            codecs = get_codecs(format_key) or {}
            if not isinstance(codecs, dict) or not codecs:
                continue
            codec_items = list(codecs.items())
            codec_items.sort(
                key=lambda item: (
                    0
                    if "264" in f"{item[0]} {item[1]}".lower()
                    else 1,
                    str(item[0]),
                )
            )
            for codec_key, _ in codec_items:
                if set_format(format_key, codec_key):
                    return str(format_key), str(codec_key)
        return None

    def sandbox_exercise(
        self,
        *,
        input_media: str | Path,
        output_dir: str | Path,
        project_name: str | None = None,
        timeout_seconds: int = 180,
    ) -> ResolveSandboxResult:
        source = Path(input_media).resolve()
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        if not source.is_file():
            raise FileNotFoundError(source)

        resolve = self.connect()
        version = self._safe_call(resolve, "GetVersionString")
        project_manager = self._safe_call(
            resolve,
            "GetProjectManager",
        )
        if project_manager is None:
            raise RuntimeError("RESOLVE_PROJECT_MANAGER_UNAVAILABLE")

        project_name = project_name or (
            f"CineFactory_Master_{uuid4().hex[:10]}"
        )
        project = None
        cleanup_ok = False
        evidence: list[ResolveOperationEvidence] = []
        render_output: Path | None = None
        provenance_path: Path | None = None
        findings: list[str] = []

        try:
            create_project = getattr(
                project_manager,
                "CreateProject",
                None,
            )
            if not callable(create_project):
                raise RuntimeError(
                    "RESOLVE_CREATE_PROJECT_API_UNAVAILABLE"
                )
            project = create_project(project_name)
            if project is None:
                raise RuntimeError(
                    f"RESOLVE_SANDBOX_PROJECT_CREATE_FAILED:{project_name}"
                )

            media_pool = self._safe_call(
                project,
                "GetMediaPool",
            )
            if media_pool is None:
                raise RuntimeError("RESOLVE_MEDIA_POOL_UNAVAILABLE")

            state: dict[str, Any] = {}

            def edit_op():
                importer = getattr(media_pool, "ImportMedia", None)
                create_timeline = getattr(
                    media_pool,
                    "CreateTimelineFromClips",
                    None,
                )
                if not callable(importer) or not callable(create_timeline):
                    return False, {}, [
                        "EDIT_API_SURFACE_INCOMPLETE"
                    ], []
                imported = importer([str(source)])
                if not imported:
                    return False, {}, ["MEDIA_IMPORT_FAILED"], []
                clips = list(imported)
                timeline = create_timeline(
                    "CineFactory Mastery Timeline",
                    clips,
                )
                if timeline is None:
                    return False, {}, ["TIMELINE_CREATE_FAILED"], []
                setter = getattr(project, "SetCurrentTimeline", None)
                if callable(setter):
                    setter(timeline)
                item = self._first_video_item(timeline)
                if item is None:
                    return False, {}, ["TIMELINE_VIDEO_ITEM_MISSING"], []
                state["timeline"] = timeline
                state["item"] = item
                return True, {
                    "imported_clips": len(clips),
                    "timeline": self._safe_call(
                        timeline,
                        "GetName",
                        default="CineFactory Mastery Timeline",
                    ),
                }, [], [str(source)]

            evidence.append(self._record("edit", edit_op))

            def fusion_op():
                item = state.get("item")
                if item is None:
                    return False, {}, ["EDIT_PREREQUISITE_FAILED"], []
                add_comp = getattr(item, "AddFusionComp", None)
                delete_comp = getattr(
                    item,
                    "DeleteFusionCompByName",
                    None,
                )
                if not callable(add_comp) or not callable(delete_comp):
                    return False, {}, [
                        "FUSION_API_SURFACE_INCOMPLETE"
                    ], []
                before = self._fusion_names(item)
                comp = add_comp()
                after = self._fusion_names(item)
                if comp is None or len(after) <= len(before):
                    return False, {}, ["FUSION_COMP_CREATE_FAILED"], []
                new_names = [name for name in after if name not in before]
                if not new_names:
                    return False, {}, [
                        "FUSION_COMP_NAME_NOT_DISCOVERABLE"
                    ], []
                deleted = all(delete_comp(name) for name in new_names)
                if not deleted:
                    return False, {}, ["FUSION_COMP_CLEANUP_FAILED"], []
                return True, {
                    "created_comps": new_names,
                    "cleanup": True,
                }, [], []

            evidence.append(self._record("Fusion comp", fusion_op))

            def color_op():
                item = state.get("item")
                if item is None:
                    return False, {}, ["EDIT_PREREQUISITE_FAILED"], []
                set_cdl = getattr(item, "SetCDL", None)
                if not callable(set_cdl):
                    return False, {}, ["COLOR_CDL_API_UNAVAILABLE"], []
                cdl = {
                    "NodeIndex": "1",
                    "Slope": "1.0 1.0 1.0",
                    "Offset": "0.0 0.0 0.0",
                    "Power": "1.0 1.0 1.0",
                    "Saturation": "1.0",
                }
                passed = bool(set_cdl(cdl))
                return passed, {
                    "neutral_cdl": cdl,
                }, [] if passed else ["NEUTRAL_CDL_APPLY_FAILED"], []

            evidence.append(self._record("color", color_op))

            def fairlight_op():
                timeline = state.get("timeline")
                if timeline is None:
                    return False, {}, ["EDIT_PREREQUISITE_FAILED"], []
                get_count = getattr(timeline, "GetTrackCount", None)
                set_name = getattr(timeline, "SetTrackName", None)
                set_enable = getattr(
                    timeline,
                    "SetTrackEnable",
                    None,
                )
                if not (
                    callable(get_count)
                    and callable(set_name)
                    and callable(set_enable)
                ):
                    return False, {}, [
                        "FAIRLIGHT_TRACK_API_SURFACE_INCOMPLETE"
                    ], []
                count = int(get_count("audio") or 0)
                if count < 1:
                    add_track = getattr(timeline, "AddTrack", None)
                    if not callable(add_track) or not add_track(
                        "audio",
                        "stereo",
                    ):
                        return False, {}, ["AUDIO_TRACK_CREATE_FAILED"], []
                    count = int(get_count("audio") or 0)
                if count < 1:
                    return False, {}, ["AUDIO_TRACK_MISSING"], []
                named = bool(
                    set_name(
                        "audio",
                        1,
                        "CineFactory Mastery Mix",
                    )
                )
                enabled = bool(set_enable("audio", 1, True))
                passed = named and enabled
                return passed, {
                    "audio_tracks": count,
                    "track_named": named,
                    "track_enabled": enabled,
                }, [] if passed else [
                    "FAIRLIGHT_TRACK_CONTROL_FAILED"
                ], []

            evidence.append(
                self._record("Fairlight mix", fairlight_op)
            )

            def deliver_op():
                timeline = state.get("timeline")
                if timeline is None:
                    return False, {}, ["EDIT_PREREQUISITE_FAILED"], []
                selected = self._pick_render_format(project)
                if selected is None:
                    return False, {}, [
                        "RENDER_FORMAT_CODEC_UNAVAILABLE"
                    ], []
                set_settings = getattr(
                    project,
                    "SetRenderSettings",
                    None,
                )
                add_job = getattr(project, "AddRenderJob", None)
                start_render = getattr(
                    project,
                    "StartRendering",
                    None,
                )
                is_rendering = getattr(
                    project,
                    "IsRenderingInProgress",
                    None,
                )
                get_status = getattr(
                    project,
                    "GetRenderJobStatus",
                    None,
                )
                if not all(
                    callable(method)
                    for method in (
                        set_settings,
                        add_job,
                        start_render,
                        is_rendering,
                        get_status,
                    )
                ):
                    return False, {}, [
                        "DELIVER_API_SURFACE_INCOMPLETE"
                    ], []

                custom_name = "cinefactory_resolve_mastery"
                settings = {
                    "SelectAllFrames": True,
                    "TargetDir": str(output),
                    "CustomName": custom_name,
                    "ExportVideo": True,
                    "ExportAudio": True,
                }
                if not set_settings(settings):
                    return False, {}, [
                        "RENDER_SETTINGS_APPLY_FAILED"
                    ], []
                job_id = add_job()
                if not job_id:
                    return False, {}, ["RENDER_JOB_CREATE_FAILED"], []
                try:
                    started = bool(start_render(job_id))
                except TypeError:
                    started = bool(start_render())
                if not started:
                    return False, {}, ["RENDER_START_FAILED"], []
                deadline = time.monotonic() + timeout_seconds
                while time.monotonic() < deadline:
                    if not is_rendering():
                        break
                    time.sleep(0.25)
                else:
                    return False, {}, ["RENDER_TIMEOUT"], []

                status = get_status(job_id) or {}
                status_text = ""
                if isinstance(status, dict):
                    status_text = str(
                        status.get("JobStatus")
                        or status.get("Status")
                        or ""
                    )
                candidates = sorted(
                    (
                        path
                        for path in output.glob(custom_name + "*")
                        if path.is_file() and path.stat().st_size > 0
                    ),
                    key=lambda path: path.stat().st_mtime,
                    reverse=True,
                )
                if not candidates:
                    return False, {
                        "render_status": status_text,
                        "format": selected[0],
                        "codec": selected[1],
                    }, ["RENDER_OUTPUT_MISSING"], []
                nonlocal render_output
                render_output = candidates[0]
                return True, {
                    "render_status": status_text,
                    "format": selected[0],
                    "codec": selected[1],
                    "bytes": render_output.stat().st_size,
                }, [], [str(render_output)]

            evidence.append(self._record("deliver", deliver_op))

            provenance = {
                "adapter": "DaVinciResolveScript",
                "resolve_version": str(version) if version else None,
                "project_name": project_name,
                "input_media": str(source),
                "input_sha256": self._hash_file(source),
                "render_output": (
                    str(render_output) if render_output else None
                ),
                "render_sha256": (
                    self._hash_file(render_output)
                    if render_output and render_output.is_file()
                    else None
                ),
                "operations": [
                    item.model_dump(mode="json")
                    for item in evidence
                ],
            }
            provenance_path = output / "cinefactory_resolve_provenance.json"
            provenance_path.write_text(
                json.dumps(
                    provenance,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        finally:
            if project is not None:
                close = getattr(project_manager, "CloseProject", None)
                delete = getattr(project_manager, "DeleteProject", None)
                closed = True
                if callable(close):
                    try:
                        closed = bool(close(project))
                    except Exception:
                        closed = False
                deleted = False
                if callable(delete):
                    try:
                        deleted = bool(delete(project_name))
                    except Exception:
                        deleted = False
                cleanup_ok = closed and deleted
                if not cleanup_ok:
                    findings.append("SANDBOX_PROJECT_CLEANUP_INCOMPLETE")

        return ResolveSandboxResult(
            project_name=project_name,
            connected=True,
            version=str(version) if version else None,
            operation_evidence=evidence,
            render_output=str(render_output) if render_output else None,
            provenance_path=(
                str(provenance_path)
                if provenance_path
                else None
            ),
            cleaned_up=cleanup_ok,
            findings=findings,
        )
