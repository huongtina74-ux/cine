from __future__ import annotations
import json, sys
from pathlib import Path
import bpy

root=Path(sys.argv[sys.argv.index("--")+1]).resolve()
rows=[]
for p in sorted(root.rglob("*.blend")):
    try:
        with bpy.data.libraries.load(str(p), link=False) as (src,_):
            row={
              "file": str(p.relative_to(root)),
              "objects": list(src.objects),
              "armatures": list(src.armatures),
              "actions": list(src.actions),
              "materials": list(src.materials),
            }
        row.update({
          "object_count": len(row["objects"]),
          "armature_count": len(row["armatures"]),
          "action_count": len(row["actions"]),
          "has_rig": bool(row["armatures"]),
          "has_animation": bool(row["actions"]),
          "error": None,
        })
    except Exception as e:
        row={"file":str(p.relative_to(root)),"error":f"{type(e).__name__}:{e}"}
    rows.append(row)
print(json.dumps(rows))
