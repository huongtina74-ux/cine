from __future__ import annotations
from pathlib import Path
import yaml


class ProfileLoader:
    def __init__(self,root:str|Path): self.root=Path(root)
    def load(self,profile_id:str)->dict:
        path=self.root/profile_id/'profile.yaml'
        if not path.exists(): raise KeyError(f'Unknown profile: {profile_id}')
        current=yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        parent=current.get('inherits')
        if parent:
            base=self.load(parent)
            return self._merge(base,current)
        return current
    def _merge(self,a:dict,b:dict)->dict:
        out=dict(a)
        for k,v in b.items():
            if isinstance(v,dict) and isinstance(out.get(k),dict): out[k]=self._merge(out[k],v)
            else: out[k]=v
        return out
