from __future__ import annotations
"""Pixel-visible Blender mask -> YOLO labels with strict train/val/test isolation.

Training image annotations are derived solely from independent flat render
mask pixel bounds, not rig-projected geometry or hand-entered fixed boxes.
No target test labels passed to training. Per-split seed families are disjoint.
"""
import hashlib
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
import yaml
from pydantic import BaseModel, Field


class MaskActorBox(BaseModel):
    actor: str
    image_box: list[int]
    normalized_xywh: list[float]
    visible_pixel_count: int
    mask_sha256: str


class MaskSampleQC(BaseModel):
    scene_id: str
    split: str
    seed: int
    image_sha256: str
    boxes: list[MaskActorBox]
    mask_overlap_pixels: int
    background_actor_leakage: bool = False


class BlenderMaskDatasetQC(BaseModel):
    status: str
    passed: bool
    production_qualified: bool = False
    source: str = "ACTUAL_BLENDER_WORKBENCH_INDEPENDENT_ACTOR_PIXEL_MASKS"
    raw_scenes: int
    split_counts: dict[str,int]
    per_split_identities: dict[str,list[str]]
    samples: list[MaskSampleQC] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    manifest_sha256: str


def hashfile(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


class BlenderVisibleMaskDatasetAssembler:
    def __init__(self, *,minimum_mask_pixels:int=150,
                 maximum_mask_overlap:int=15):
        self.minimum_mask_pixels=minimum_mask_pixels
        self.maximum_mask_overlap=maximum_mask_overlap

    def _sample(self,row:dict)->tuple[MaskSampleQC,list[str],list[str]]:
        image=Path(row["image"])
        raw=cv2.imread(str(image),cv2.IMREAD_COLOR)
        if raw is None:
            raise ValueError("BLENDER_RAW_RGB_FRAME_UNREADABLE")
        h,w=raw.shape[:2]
        if w!=row["width"] or h!=row["height"]:
            raise ValueError("BLENDER_RAW_RENDER_DIMENSIONS_MISMATCH")
        labels=[]
        boxes=[]
        binary_masks=[]
        problems=[]
        for actor,file in sorted(row["actor_masks"].items()):
            mask_path=Path(file)
            # RGB Blender PNG masks must be decoded safely even if another
            # test/session has changed OpenCV's imread grayscale behavior.
            # Explicitly handle 2D, BGR and BGRA instead of assuming that
            # cv2.IMREAD_GRAYSCALE always yields an HxW array.
            img=cv2.imread(str(mask_path),cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError("ACTOR_MASK_UNREADABLE_OR_WRONG_DIMENSIONS")
            if img.ndim==3 and img.shape[2] in (3,4):
                rgb=img[:,:,:3]
                if int(np.max(np.ptp(rgb.astype(np.int16),axis=2)))>3:
                    raise ValueError("ACTOR_MASK_HAS_NON_GRAY_RGB")
                img=cv2.cvtColor(
                    img,cv2.COLOR_BGRA2GRAY if img.shape[2]==4
                    else cv2.COLOR_BGR2GRAY,
                )
            if img.ndim!=2 or img.shape!=(h,w):
                raise ValueError("ACTOR_MASK_UNREADABLE_OR_WRONG_DIMENSIONS")
            mask=img>127
            binary_masks.append(mask.astype(np.uint8))
            yy,xx=np.where(mask)
            count=int(len(xx))
            if count<self.minimum_mask_pixels:
                problems.append(f"{row['scene_id']}:{actor}:MASK_TOO_SMALL")
                continue
            xmin,xmax=int(xx.min()),int(xx.max())+1
            ymin,ymax=int(yy.min()),int(yy.max())+1
            if not (0<=xmin<xmax<=w and 0<=ymin<ymax<=h):
                problems.append("MASK_IMAGE_BOX_OUTSIDE_FRAME")
                continue
            cx=(xmin+xmax)/2/w
            cy=(ymin+ymax)/2/h
            bw=(xmax-xmin)/w
            bh=(ymax-ymin)/h
            yolo=[cx,cy,bw,bh]
            if not all(0<z<1 for z in yolo):
                problems.append("YOLO_NORMALIZED_BOX_INVALID")
            labels.append("0 "+" ".join(f"{x:.8f}" for x in yolo))
            boxes.append(MaskActorBox(
                actor=actor,image_box=[xmin,ymin,xmax,ymax],
                normalized_xywh=yolo,visible_pixel_count=count,
                mask_sha256=hashfile(mask_path),
            ))
        overlap=0
        if binary_masks:
            merged=np.sum(np.stack(binary_masks),axis=0)
            overlap=int((merged>1).sum())
            if overlap>self.maximum_mask_overlap:
                problems.append(f"{row['scene_id']}:ACTOR_MASKS_OVERLAP:{overlap}")
        if len(boxes)<2 or len(boxes)!=len(row["actor_masks"]):
            problems.append(f"{row['scene_id']}:ACTOR_LABEL_SET_INCOMPLETE")
        sample=MaskSampleQC(
            scene_id=row["scene_id"],split=row["split"],seed=row["seed"],
            image_sha256=hashfile(image),boxes=boxes,
            mask_overlap_pixels=overlap,
        )
        return sample,labels,problems

    def assemble(self,*,render_index:str|Path,dataset_dir:str|Path
                 )->BlenderMaskDatasetQC:
        manifest=Path(render_index).resolve()
        dataset=Path(dataset_dir).resolve()
        content=manifest.read_bytes()
        records=json.loads(content.decode("utf-8"))
        problems=[]
        if not records:
            raise ValueError("BLENDER_RAW_SCENE_MANIFEST_EMPTY")
        identities={k:[] for k in ("train","val","test")}
        counts={k:0 for k in identities}
        seen_scene=set()
        seen_seeds=set()
        seen_images=set()
        samples=[]
        for row in records:
            split=row["split"]
            scene=row["scene_id"]
            seed=row["seed"]
            if split not in counts:
                problems.append(f"UNSUPPORTED_SPLIT:{split}")
                continue
            if not scene.startswith(split+"_"):
                problems.append("SPLIT_SCENE_LINEAGE_MISMATCH")
            if scene in seen_scene or seed in seen_seeds:
                problems.append("TRAIN_VAL_TEST_SCENE_SEED_COLLISION")
            if row["label_source"]!="INDEPENDENT_BLENDER_PIXEL_MASK_NOT_PROJECTED_BOX":
                problems.append("SYNTHETIC_LABEL_PROVENANCE_INVALID")
            seen_scene.add(scene)
            seen_seeds.add(seed)
            sample,labels,errors=self._sample(row)
            problems.extend(errors)
            if sample.image_sha256 in seen_images:
                problems.append("DUPLICATED_RGB_FRAME_ACROSS_SCENES")
            seen_images.add(sample.image_sha256)
            counts[split]+=1
            identities[split].append(scene)
            samples.append(sample)
            source=Path(row["image"])
            dest_image=dataset/"images"/split/(scene+".png")
            dest_label=dataset/"labels"/split/(scene+".txt")
            dest_image.parent.mkdir(parents=True,exist_ok=True)
            dest_label.parent.mkdir(parents=True,exist_ok=True)
            # Do not copy/write individual samples if quality problems exist.
            if not errors:
                shutil.copyfile(source,dest_image)
                dest_label.write_text("\n".join(labels)+"\n",encoding="utf-8")
        for split in identities:
            if counts[split]<1:
                problems.append(f"{split.upper()}_SPLIT_EMPTY")
        (dataset/"data.yaml").write_text(yaml.safe_dump({
            "path":str(dataset),
            "train":"images/train","val":"images/val","test":"images/test",
            "nc":1,"names":{0:"voxel_actor"},
        },sort_keys=False),encoding="utf-8")
        if problems:
            status="BLOCKED"
        else:
            status="MASK_DERIVED_YOLO_SCENE_SPLITS_PASS"
        report=BlenderMaskDatasetQC(
            status=status,passed=not problems,raw_scenes=len(records),
            split_counts=counts,per_split_identities=identities,
            samples=samples,blockers=sorted(set(problems)),
            manifest_sha256=hashlib.sha256(content).hexdigest(),
        )
        target=dataset.parent/"mask_dataset_qc.json"
        target.write_text(report.model_dump_json(indent=2),encoding="utf-8")
        return report


    @staticmethod
    def verify_preinference_integrity(*,dataset_dir: str | Path,
                                      report: BlenderMaskDatasetQC)->list[str]:
        """Forbid altered evaluation images/labels between QC and inference."""
        dataset=Path(dataset_dir).resolve()
        errors=[]
        if not report.passed:
            errors.append("INVALID_SOURCE_BLENDER_MASK_REPORT")
        known=set()
        for sample in report.samples:
            frame=dataset/"images"/sample.split/(sample.scene_id+".png")
            label=dataset/"labels"/sample.split/(sample.scene_id+".txt")
            known.add((sample.split,sample.scene_id))
            if not frame.is_file() or hashfile(frame)!=sample.image_sha256:
                errors.append("DATASET_EVALUATION_IMAGE_HASH_MISMATCH:"+sample.scene_id)
                continue
            if not label.is_file():
                errors.append("DATASET_LABEL_MISSING:"+sample.scene_id)
                continue
            actual=label.read_text(encoding="utf-8").strip().splitlines()
            expected=[
                "0 "+" ".join(f"{x:.8f}" for x in box.normalized_xywh)
                for box in sample.boxes
            ]
            if actual!=expected:
                errors.append("BLENDER_PIXEL_MASK_LABEL_CHANGED:"+sample.scene_id)
        for split in ("train","val","test"):
            found={
                (split,item.stem)
                for item in (dataset/"images"/split).glob("*.png")
            }
            if found-{x for x in known if x[0]==split}:
                errors.append("UNVERIFIED_DATASET_IMAGE_ADDED:"+split)
        return sorted(set(errors))
