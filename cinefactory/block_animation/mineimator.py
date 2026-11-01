"""Mine-imator 2.x export for the block animation pipeline.

Mine-imator has no API, but its project file (.miproject) is JSON. This
adapter takes a CompiledEpisode (the same one the Blender worker renders) and
writes its performance into a COPY of an owner-made template project:

* the template already contains the original characters (with their skins and
  all body-part timelines), one camera and optionally one audio track;
* the exporter only replaces keyframes: character position/yaw/visibility,
  limb swing/bend and head turn per clip, camera orbit/FOV per camera take,
  and the voice/mix track.

Building characters from scratch would mean re-implementing Mine-imator's
model loader, so the template is the contract. Axis signs and camera
behaviour come from config/block_animation/mineimator.yaml and stay
UNCALIBRATED until one export has been opened in Mine-imator on the owner's
PC; every export report carries that status.
"""
from __future__ import annotations

import copy
import json
import math
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from cinefactory.block_animation.contracts import CompiledEpisode, CompiledShot

HUMAN_PARTS = ("body", "head", "right_arm", "left_arm", "right_leg", "left_leg")
ARMS = ("right_arm", "left_arm")
LEGS = ("right_leg", "left_leg")
UPPER_PARTS = ("head", "right_arm", "left_arm")


class MineImatorError(ValueError):
    """The template or episode cannot be exported."""


# --------------------------------------------------------------------------
# Project file
# --------------------------------------------------------------------------

def load_project(path: Path) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise MineImatorError(
            f"{path} is not a JSON .miproject (Mine-imator 1.1+). "
            "Older .mproj files are binary: open and re-save them in Mine-imator 2.x."
        ) from exc


def save_project(doc: dict[str, Any], path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")


@dataclass
class CharacterHandle:
    name: str
    root: dict[str, Any]
    parts: dict[str, dict[str, Any]] = field(default_factory=dict)


class MineImatorTemplate:
    """Index of the timelines and resources in a .miproject document."""

    def __init__(self, doc: dict[str, Any]):
        if not isinstance(doc.get("timelines"), list):
            raise MineImatorError("template has no 'timelines' list")
        self.doc = doc
        self.timelines: list[dict[str, Any]] = doc["timelines"]
        self.resources: list[dict[str, Any]] = doc.setdefault("resources", [])
        by_id = {str(t.get("id")): t for t in self.timelines}
        self.characters: dict[str, CharacterHandle] = {}
        for tl in self.timelines:
            if tl.get("type") == "char":
                self.characters[_key(tl.get("name", ""))] = CharacterHandle(name=tl.get("name", ""), root=tl)
        for tl in self.timelines:
            if tl.get("type") != "bodypart" or tl.get("part_of") is None:
                continue
            owner = by_id.get(str(tl["part_of"]))
            part = str(tl.get("model_part_name") or "").lower()
            if owner is not None and owner.get("type") == "char" and part:
                self.characters[_key(owner.get("name", ""))].parts[part] = tl
        self.cameras = {_key(t.get("name", "")): t for t in self.timelines if t.get("type") == "camera"}
        self.audio = [t for t in self.timelines if t.get("type") == "audio"]

    @property
    def tempo(self) -> int:
        return int(self.doc.get("project", {}).get("tempo") or 20)

    def character(self, name: str) -> CharacterHandle | None:
        return self.characters.get(_key(name))

    def resource(self, res_id: Any) -> dict[str, Any] | None:
        return next((r for r in self.resources if str(r.get("id")) == str(res_id)), None)


def _key(name: str) -> str:
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def inspect_project(path: Path) -> dict[str, Any]:
    """Summarise a .miproject so the owner's template can be checked before export."""
    doc = load_project(path)
    tpl = MineImatorTemplate(doc)
    project = doc.get("project", {})
    chars = []
    for handle in tpl.characters.values():
        missing = [p for p in HUMAN_PARTS if p not in handle.parts]
        chars.append({"name": handle.name, "id": handle.root.get("id"), "parts": sorted(handle.parts), "missing_parts": missing})
    audio = []
    for tl in tpl.audio:
        res_ids = {str(v.get("SOUND_OBJ")) for v in tl.get("keyframes", {}).values() if isinstance(v, dict) and v.get("SOUND_OBJ")}
        audio.append({"name": tl.get("name"), "sounds": [(tpl.resource(r) or {}).get("filename") for r in sorted(res_ids)]})
    problems = []
    if not chars:
        problems.append("NO_CHARACTER_TIMELINE")
    for c in chars:
        if c["missing_parts"]:
            problems.append(f"CHARACTER_PARTS_MISSING:{c['name']}:{','.join(c['missing_parts'])}")
    if not tpl.cameras:
        problems.append("NO_CAMERA_TIMELINE")
    return {
        "file": str(Path(path).resolve()),
        "format": doc.get("format"),
        "created_in": doc.get("created_in"),
        "tempo": tpl.tempo,
        "video": [project.get("video_width"), project.get("video_height")],
        "characters": chars,
        "cameras": [t.get("name") for t in tpl.cameras.values()],
        "audio_tracks": audio,
        "timeline_count": len(tpl.timelines),
        "resource_count": len(tpl.resources),
        "ready_as_template": not problems,
        "problems": problems,
    }


# --------------------------------------------------------------------------
# Procedural clip poses (degrees; swing > 0 = limb forward)
# --------------------------------------------------------------------------

def _zero_pose() -> dict[str, Any]:
    return {"limbs": {p: {"swing": 0.0, "spread": 0.0, "bend": 0.0} for p in ARMS + LEGS},
            "head": {"yaw": 0.0, "pitch": 0.0}, "body_pitch": 0.0, "lift": 0.0}


def clip_pose(clip_id: str, phase: float, u: float, intensity: float = 1.0) -> dict[str, Any] | None:
    """Pose of one clip at `phase` seconds into it (`u` = 0..1 progress).

    Returns only the channels the clip drives, or None for an unknown clip.
    """
    s, k = math.sin, intensity
    env = s(math.pi * min(1.0, max(0.0, u)))  # in-and-out envelope for one-shot gestures
    L, A, H = {}, {}, {}
    body_pitch = lift = 0.0
    if clip_id == "idle":
        A = {"right_arm": {"swing": 2 * s(phase * 2)}, "left_arm": {"swing": -2 * s(phase * 2)}}
        lift = 0.01 * s(phase * 2.4)
    elif clip_id in ("walk", "run"):
        amp, freq = (35, 9) if clip_id == "walk" else (60, 14)
        w = s(phase * freq) * k
        L = {"right_leg": {"swing": amp * w, "bend": max(0, -w) * 25}, "left_leg": {"swing": -amp * w, "bend": max(0, w) * 25}}
        A = {"right_arm": {"swing": -amp * 0.9 * w, "bend": 15}, "left_arm": {"swing": amp * 0.9 * w, "bend": 15}}
        lift = abs(math.cos(phase * freq)) * (0.05 if clip_id == "walk" else 0.1)
        body_pitch = 0 if clip_id == "walk" else 10
    elif clip_id == "turn_head":
        H = {"yaw": 55 * env * k}
    elif clip_id == "point":
        A = {"right_arm": {"swing": 88 * env * k, "bend": 5}}
        H = {"pitch": 4 * env}
    elif clip_id == "wave":
        A = {"right_arm": {"swing": 160 * env * k, "spread": 25 * s(phase * 12) * env, "bend": 30}}
    elif clip_id == "laugh_body":
        body_pitch = -8 * env * k + 4 * s(phase * 16) * env
        A = {"right_arm": {"swing": 20 * env, "bend": 60}, "left_arm": {"swing": 20 * env, "bend": 60}}
        H = {"pitch": -15 * env}
    elif clip_id == "cry_body":
        body_pitch = 15 * env * k
        A = {"right_arm": {"swing": 70 * env, "bend": 110 * env}, "left_arm": {"swing": 70 * env, "bend": 110 * env}}
        H = {"pitch": 20 * env + 3 * s(phase * 10) * env}
    elif clip_id == "shock_recoil":
        e = min(1.0, u * 4) * (1 - max(0.0, u - 0.6) / 0.4)
        body_pitch = -12 * e * k
        A = {"right_arm": {"swing": 50 * e, "spread": 35 * e, "bend": 40 * e}, "left_arm": {"swing": 50 * e, "spread": -35 * e, "bend": 40 * e}}
        H = {"pitch": -10 * e}
    elif clip_id == "flinch":
        e = env * k
        A = {"right_arm": {"swing": 75 * e, "bend": 100 * e}, "left_arm": {"swing": 75 * e, "bend": 100 * e}}
        H = {"pitch": 15 * e}
        body_pitch = 8 * e
    elif clip_id == "jump":
        crouch = max(0.0, 1 - u * 5) if u < 0.2 else 0.0
        air = s(math.pi * min(1.0, max(0.0, (u - 0.2) / 0.7)))
        lift = 1.1 * air * k
        L = {"right_leg": {"swing": 20 * crouch + 25 * air, "bend": 60 * crouch + 40 * air}, "left_leg": {"swing": 20 * crouch + 25 * air, "bend": 60 * crouch + 40 * air}}
        A = {"right_arm": {"swing": -30 * crouch + 150 * air, "spread": 15 * air}, "left_arm": {"swing": -30 * crouch + 150 * air, "spread": -15 * air}}
    elif clip_id == "fall":
        f = s(phase * 20)
        A = {"right_arm": {"swing": 160 + 20 * f, "spread": 35}, "left_arm": {"swing": 160 - 20 * f, "spread": -35}}
        L = {"right_leg": {"swing": 25 * f, "bend": 20}, "left_leg": {"swing": -25 * f, "bend": 20}}
    elif clip_id == "push":
        A = {"right_arm": {"swing": 85 * env * k, "bend": 50 * (1 - env)}, "left_arm": {"swing": 85 * env * k, "bend": 50 * (1 - env)}}
        body_pitch = 12 * env
        L = {"right_leg": {"swing": 25 * env}, "left_leg": {"swing": -20 * env}}
    elif clip_id == "grab":
        A = {"right_arm": {"swing": 70 * env * k, "bend": 60 * env}}
        body_pitch = 10 * env
    else:
        return None
    pose: dict[str, Any] = {"limbs": {}, "head": H, "body_pitch": body_pitch, "lift": lift}
    for part, chans in {**L, **A}.items():
        pose["limbs"][part] = chans
    return pose


def _merge(base: dict[str, Any], top: dict[str, Any], *, upper_only: bool) -> None:
    for part, chans in top["limbs"].items():
        if upper_only and part not in UPPER_PARTS:
            continue
        base["limbs"][part].update({k: float(v) for k, v in chans.items()})
    base["head"].update({k: float(v) for k, v in top["head"].items()})
    if not upper_only:
        base["body_pitch"] = top["body_pitch"]
        base["lift"] = top["lift"]
    elif top["body_pitch"]:
        base["body_pitch"] = top["body_pitch"]


# --------------------------------------------------------------------------
# Exporter
# --------------------------------------------------------------------------

@dataclass
class ExportReport:
    output: str
    tempo: int
    frames: int
    shots: int
    characters: dict[str, str]
    keyframes_written: int
    calibration_status: str
    warnings: list[str] = field(default_factory=list)
    audio: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class MineImatorExporter:
    def __init__(self, conventions: dict[str, Any]):
        self.cv = conventions

    @classmethod
    def from_root(cls, root: Path) -> "MineImatorExporter":
        path = Path(root) / "config/block_animation/mineimator.yaml"
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")))

    # ---- helpers -------------------------------------------------------
    def _pos(self, x: float, y: float, z: float) -> dict[str, float]:
        upb = float(self.cv["units_per_block"])
        out = {}
        for axis, val in (("x", x), ("y", y), ("z", z)):
            m = self.cv["axis_map"][axis]
            out[m["value"]] = round(m["sign"] * val * upb, 3)
        return out

    def _chan(self, name: str, degrees: float) -> tuple[str, float]:
        m = self.cv[name]
        return m["value"], round(m["sign"] * degrees, 3)

    def _actor_track(self, shot: CompiledShot, actor_id: str, t: float) -> dict[str, Any]:
        """Root position (blocks), yaw (deg) and merged pose for one actor at shot time t."""
        placement = next(a for a in shot.actors if a.actor_id == actor_id)
        tr = placement.transform
        x, y, z = (tr.location.x, tr.location.y, tr.location.z) if tr else (0.0, 0.0, 0.0)
        yaw = math.degrees(tr.rotation_euler.z) if tr else 0.0
        pose = _zero_pose()
        idle = clip_pose("idle", t, 0)
        if idle:
            _merge(pose, idle, upper_only=False)
        cues = [(a.start_seconds, a.end_seconds, a.clip_id, a.intensity, a.speed, a.layer) for a in shot.actions if a.actor_id == actor_id]
        cues += [(r.start_seconds, None, r.clip_id, r.intensity, 1.0, None) for r in shot.reactions if r.actor_id == actor_id and r.clip_id]
        travelled = 0.0
        for start, end, clip_id, intensity, speed, layer in sorted(cues, key=lambda c: c[0]):
            clip = shot.clips.get(clip_id)
            dur = (end - start) if end is not None else (clip.duration_seconds / speed if clip else 1.0)
            # root motion accumulates over the elapsed part of the action
            spd = self.cv.get("root_motion_speed", {}).get(clip_id)
            if spd and clip is not None and clip.root_motion and t > start:
                travelled += spd * speed * (min(t, start + dur) - start)
            if not (start <= t <= start + dur):
                continue
            p = clip_pose(clip_id, (t - start) * speed, (t - start) / max(dur, 1e-6), intensity)
            if p is None:
                continue
            upper = (layer or (clip.layer if clip else "base")) == "upper"
            _merge(pose, p, upper_only=upper)
        if travelled:
            x += travelled * -math.sin(math.radians(yaw))
            y += travelled * math.cos(math.radians(yaw))
        for g in shot.gaze:
            if g.actor_id != actor_id or t < g.start_seconds or (g.end_seconds is not None and t > g.end_seconds):
                continue
            target = None
            if g.target_actor_id:
                other = next((a for a in shot.actors if a.actor_id == g.target_actor_id and a.transform), None)
                target = other.transform.location if other else None
            elif g.target_point is not None:
                target = g.target_point
            if target is not None:
                want = math.degrees(math.atan2(-(target.x - x), target.y - y))
                rel = (want - yaw + 180) % 360 - 180
                pose["head"]["yaw"] = max(-70.0, min(70.0, rel)) * g.intensity
        return {"pos": (x, y, z + pose["lift"]), "yaw": yaw, "pose": pose}

    def _camera_values(self, shot: CompiledShot, take_index: int, t: float, positions: dict[str, tuple]) -> dict[str, Any] | None:
        if not shot.camera_takes:
            return None
        take = shot.camera_takes[min(take_index, len(shot.camera_takes) - 1)]
        cam = self.cv["camera"]
        pts = [positions[a] for a in take.targets if a in positions] or list(positions.values())
        if not pts:
            return None
        cx = sum(p["pos"][0] for p in pts) / len(pts)
        cy = sum(p["pos"][1] for p in pts) / len(pts)
        cz = min(p["pos"][2] for p in pts) + float(cam["eye_height_blocks"])
        spread = max((math.dist(a["pos"][:2], b["pos"][:2]) for a in pts for b in pts), default=0.0)
        dist = float(cam["shot_size_distance_blocks"].get(take.shot_size, 3.0)) + spread * 0.6
        span = max(take.end_seconds - take.start_seconds, 1e-6)
        u = min(1.0, max(0.0, (t - take.start_seconds) / span))
        if take.motion in ("push_in", "dolly_in"):
            dist *= 1.0 + take.motion_strength * (1 - 2 * u)
        elif take.motion in ("pull_out", "dolly_out"):
            dist *= 1.0 - take.motion_strength * (1 - 2 * u)
        facing = sum(p["yaw"] for p in pts) / len(pts)
        angle = facing + 180 + float(cam["anchor_angle_degrees"].get(take.anchor or "front", 0)) + float(cam["angle_xy_offset_degrees"])
        if take.motion in ("orbit", "arc"):
            angle += 40 * take.motion_strength * (u - 0.5) * 2
        fov = 2 * math.degrees(math.atan(float(cam["sensor_height_mm"]) / 2 / take.lens_mm))
        vals = self._pos(cx, cy, cz)
        vals.update({"CAM_FOV": round(fov, 2), "CAM_ROTATE": True, "CAM_ROTATE_DISTANCE": round(dist * self.cv["units_per_block"], 2),
                     "CAM_ROTATE_ANGLE_XY": round(angle % 360, 2), "CAM_ROTATE_ANGLE_Z": float(cam["pitch_degrees"])})
        return vals

    # ---- main entry ----------------------------------------------------
    def export(self, compiled: CompiledEpisode, template_path: Path, output_path: Path, *,
               actor_map: dict[str, str] | None = None, camera_name: str | None = None,
               audio_path: Path | None = None, take_index: int = 0) -> ExportReport:
        doc = copy.deepcopy(load_project(template_path))
        tpl = MineImatorTemplate(doc)
        warnings: list[str] = []
        fps = tpl.tempo
        step = max(1, int(self.cv.get("sample_step_frames", 2)))
        transition = self.cv.get("transition", "linear")
        actor_map = dict(actor_map or {})
        all_actors = sorted({a.actor_id for s in compiled.shots for a in s.actors})
        handles: dict[str, CharacterHandle] = {}
        for actor_id in all_actors:
            handle = tpl.character(actor_map.get(actor_id, actor_id))
            if handle is None:
                raise MineImatorError(f"template has no character named {actor_map.get(actor_id, actor_id)!r} for actor {actor_id!r}; "
                                      f"available: {[h.name for h in tpl.characters.values()]}. Use --map {actor_id}=<name>.")
            missing = [p for p in HUMAN_PARTS if p not in handle.parts]
            if missing:
                warnings.append(f"PARTS_MISSING:{handle.name}:{','.join(missing)}")
            handles[actor_id] = handle
        camera = tpl.cameras.get(_key(camera_name)) if camera_name else next(iter(tpl.cameras.values()), None)
        if camera is None:
            raise MineImatorError("template has no camera timeline" + (f" named {camera_name!r}" if camera_name else ""))
        # reset animated timelines
        for h in handles.values():
            h.root["keyframes"] = {}
            for part in h.parts.values():
                part["keyframes"] = {}
        camera["keyframes"] = {}
        written = 0
        offset = 0
        last_frames: dict[str, dict] = {}
        for shot in compiled.shots:
            n = max(1, round(shot.duration_seconds * fps))
            frames = sorted(set(list(range(0, n, step)) + [n - 1]))
            present = {a.actor_id for a in shot.actors}
            for f in frames:
                t = f / fps
                pos = {a: self._actor_track(shot, a, t) for a in present}
                key = str(offset + f)
                first = f == 0
                trans = "instant" if f == frames[-1] else transition
                for actor_id, handle in handles.items():
                    if actor_id not in present:
                        if first:
                            prev = last_frames.get(actor_id, {})
                            handle.root["keyframes"][key] = {**prev, "VISIBLE": False, "TRANSITION": "instant"}
                            written += 1
                        continue
                    tr = pos[actor_id]
                    root_vals = self._pos(*tr["pos"])
                    yv, yd = self._chan("yaw", tr["yaw"] + float(self.cv["yaw"].get("offset_degrees", 0)))
                    root_vals[yv] = yd
                    root_vals.update({"VISIBLE": True, "TRANSITION": trans})
                    handle.root["keyframes"][key] = root_vals
                    last_frames[actor_id] = {k: v for k, v in root_vals.items() if k not in ("VISIBLE", "TRANSITION")}
                    written += 1
                    pose = tr["pose"]
                    for part_name, part_tl in handle.parts.items():
                        vals: dict[str, Any] = {"TRANSITION": trans}
                        if part_name in pose["limbs"]:
                            limb = pose["limbs"][part_name]
                            for chan, cname in (("swing", "limb_swing"), ("spread", "limb_spread"), ("bend", "bend")):
                                v, d = self._chan(cname, limb.get(chan, 0.0))
                                vals[v] = d
                        elif part_name == "head":
                            v, d = self._chan("head_yaw", pose["head"].get("yaw", 0.0)); vals[v] = d
                            v, d = self._chan("head_pitch", pose["head"].get("pitch", 0.0)); vals[v] = d
                        elif part_name == "body":
                            v, d = self._chan("limb_swing", -pose["body_pitch"]); vals[v] = d
                        part_tl["keyframes"][key] = vals
                        written += 1
                cam_vals = self._camera_values(shot, take_index, t, pos)
                if cam_vals is not None:
                    cam_vals["TRANSITION"] = trans
                    camera["keyframes"][key] = cam_vals
                    written += 1
            offset += n
        project = doc.setdefault("project", {})
        project["video_width"], project["video_height"] = compiled.width, compiled.height
        audio_note = None
        if audio_path is not None:
            audio_note = self._attach_audio(tpl, Path(audio_path), Path(output_path), warnings)
        save_project(doc, output_path)
        status = str(self.cv.get("calibration_status", "UNCALIBRATED"))
        if status != "CALIBRATED":
            warnings.append("UNCALIBRATED_AXES: open the export in Mine-imator and confirm limbs/camera before production use")
        if any(e.expression_id for s in compiled.shots for e in s.expressions):
            warnings.append("EXPRESSIONS_NOT_EXPORTED: Mine-imator faces come from the skin; swap skin textures for expressions")
        if any(s.props for s in compiled.shots):
            warnings.append("PROPS_NOT_EXPORTED: place props in the template")
        return ExportReport(output=str(Path(output_path).resolve()), tempo=fps, frames=offset, shots=len(compiled.shots),
                            characters={a: h.name for a, h in handles.items()}, keyframes_written=written,
                            calibration_status=status, warnings=warnings, audio=audio_note)

    def _attach_audio(self, tpl: MineImatorTemplate, audio: Path, output_path: Path, warnings: list[str]) -> str | None:
        if not audio.exists():
            raise MineImatorError(f"audio file not found: {audio}")
        if not tpl.audio:
            warnings.append("NO_AUDIO_TRACK_IN_TEMPLATE: add one audio track in the template to carry the episode mix")
            return None
        track = tpl.audio[0]
        res_ids = [v.get("SOUND_OBJ") for v in track.get("keyframes", {}).values() if isinstance(v, dict) and v.get("SOUND_OBJ")]
        res = tpl.resource(res_ids[0]) if res_ids else next((r for r in tpl.resources if r.get("type") == "sound"), None)
        if res is None:
            warnings.append("NO_SOUND_RESOURCE_IN_TEMPLATE: the template audio track has no sound file")
            return None
        target = output_path.parent / audio.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if audio.resolve() != target.resolve():
            shutil.copy2(audio, target)
        res["filename"] = audio.name
        track["keyframes"] = {"0": {"SOUND_OBJ": res["id"]}}
        return audio.name
