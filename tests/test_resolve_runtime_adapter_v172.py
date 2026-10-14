from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace

from cinefactory.executors.resolve import (
    ResolveRuntimeAdapter,
)
from cinefactory.studio.execution_mastery import (
    ExecutionMasteryRunner,
    ResolveExecutionEvaluator,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment
from cinefactory.studio.tooling import ToolDoctor


class FakeTimelineItem:
    def __init__(self):
        self._fusion = []

    def AddFusionComp(self):
        self._fusion.append("Composition 1")
        return object()

    def GetFusionCompNameList(self):
        return list(self._fusion)

    def DeleteFusionCompByName(self, name):
        if name in self._fusion:
            self._fusion.remove(name)
            return True
        return False

    def SetCDL(self, cdl):
        return cdl.get("NodeIndex") == "1"


class FakeTimeline:
    def __init__(self, source: Path):
        self.source = source
        self.item = FakeTimelineItem()
        self.track_name = None
        self.track_enabled = None

    def GetName(self):
        return "CineFactory Mastery Timeline"

    def GetItemListInTrack(self, kind, index):
        if kind == "video" and index == 1:
            return [self.item]
        return []

    def GetTrackCount(self, kind):
        return 1 if kind == "audio" else 1

    def SetTrackName(self, kind, index, name):
        self.track_name = (kind, index, name)
        return True

    def SetTrackEnable(self, kind, index, enabled):
        self.track_enabled = (kind, index, enabled)
        return True

    def AddTrack(self, kind, subtype):
        return True


class FakeMediaPool:
    def __init__(self, project):
        self.project = project

    def ImportMedia(self, paths):
        self.project.source = Path(paths[0])
        return [object()]

    def CreateTimelineFromClips(self, name, clips):
        self.project.timeline = FakeTimeline(self.project.source)
        return self.project.timeline


class FakeProject:
    def __init__(self):
        self.source = None
        self.timeline = None
        self.settings = {}
        self.render_format = None
        self.render_codec = None
        self._job = "job-1"

    def GetMediaPool(self):
        return FakeMediaPool(self)

    def SetCurrentTimeline(self, timeline):
        self.timeline = timeline
        return True

    def GetRenderFormats(self):
        return {"MP4": "mp4", "QuickTime": "mov"}

    def GetRenderCodecs(self, render_format):
        return {"H.264": "H264"}

    def SetCurrentRenderFormatAndCodec(self, render_format, codec):
        self.render_format = render_format
        self.render_codec = codec
        return True

    def SetRenderSettings(self, settings):
        self.settings = dict(settings)
        return True

    def AddRenderJob(self):
        return self._job

    def StartRendering(self, *args):
        target = Path(self.settings["TargetDir"])
        target.mkdir(parents=True, exist_ok=True)
        output = target / (self.settings["CustomName"] + ".mp4")
        shutil.copy2(self.source, output)
        return True

    def IsRenderingInProgress(self):
        return False

    def GetRenderJobStatus(self, job_id):
        return {"JobStatus": "Complete"}


class FakeProjectManager:
    def __init__(self):
        self.project = None
        self.deleted = []

    def CreateProject(self, name):
        self.project = FakeProject()
        return self.project

    def CloseProject(self, project):
        return project is self.project

    def DeleteProject(self, name):
        self.deleted.append(name)
        return True


class FakeResolve:
    def __init__(self):
        self.manager = FakeProjectManager()

    def GetVersionString(self):
        return "DaVinci Resolve 21.1 Test"

    def GetProductName(self):
        return "DaVinci Resolve Studio"

    def GetProjectManager(self):
        return self.manager


class FakeResolveModule:
    def __init__(self):
        self.resolve = FakeResolve()

    def scriptapp(self, name):
        assert name == "Resolve"
        return self.resolve


def test_tool_doctor_detects_resolve_module_and_local_docs(
    tmp_path: Path,
    monkeypatch,
):
    program_files = tmp_path / "PF"
    exe = (
        program_files
        / "Blackmagic Design"
        / "DaVinci Resolve"
        / "Resolve.exe"
    )
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"fake")

    scripting = tmp_path / "RS"
    module = scripting / "Modules" / "DaVinciResolveScript.py"
    module.parent.mkdir(parents=True, exist_ok=True)
    module.write_text("# fake module", encoding="utf-8")
    (scripting / "README.txt").write_text(
        "Last Updated: 24 Jul 2026\nResolve scripting docs",
        encoding="utf-8",
    )

    monkeypatch.setenv("ProgramFiles", str(program_files))
    monkeypatch.setenv("RESOLVE_SCRIPT_API", str(scripting))

    env = ToolDoctor(tmp_path).inspect("resolve")
    assert env.installed is True
    assert "python_scripting" in env.capabilities
    assert "Fusion comp".lower().split()[0] not in env.known_issues
    assert env.api_version == "Last Updated: 24 Jul 2026"


def test_resolve_runtime_adapter_sandbox_executes_all_operations(
    tmp_path: Path,
):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"fixture")
    adapter = ResolveRuntimeAdapter(
        tmp_path,
        module_override=FakeResolveModule(),
    )
    probe = adapter.probe()
    assert probe.connected is True
    assert probe.version == "DaVinci Resolve 21.1 Test"

    result = adapter.sandbox_exercise(
        input_media=source,
        output_dir=tmp_path / "out",
        project_name="CF_TEST_RESOLVE",
    )
    assert result.cleaned_up is True
    assert Path(result.provenance_path or "").is_file()
    assert Path(result.render_output or "").is_file()

    by_op = {item.operation: item for item in result.operation_evidence}
    assert set(by_op) == {
        "edit",
        "Fusion comp",
        "color",
        "Fairlight mix",
        "deliver",
    }
    assert all(item.passed for item in by_op.values())
    assert by_op["Fusion comp"].metadata["cleanup"] is True
    assert by_op["Fairlight mix"].metadata["track_enabled"] is True


def test_resolve_execution_mastery_can_validate_with_runtime_evidence(
    tmp_path: Path,
):
    kernel = build_studio_kernel(tmp_path)
    original_inspect = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="resolve",
            installed=True,
            version="DaVinci Resolve 21.1 Test",
            api_version="Last Updated: 24 Jul 2026",
            executable_path="C:/fake/Resolve.exe",
            capabilities={
                "edit",
                "fusion",
                "color",
                "fairlight",
                "deliver",
                "python_scripting",
            },
        )
        if tool_id == "resolve"
        else original_inspect(tool_id)
    )

    fake_module = FakeResolveModule()
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["resolve"] = ResolveExecutionEvaluator(
        adapter_factory=lambda root: ResolveRuntimeAdapter(
            root,
            module_override=fake_module,
        )
    )

    report = runner.evaluate("resolve")
    assert report.runtime_available is True
    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "edit",
        "Fusion comp",
        "color",
        "Fairlight mix",
        "deliver",
    }
    assert (
        kernel.skills.get(
            "tool.resolve.post",
            "21.1",
        ).status.value
        == "VALIDATED"
    )
