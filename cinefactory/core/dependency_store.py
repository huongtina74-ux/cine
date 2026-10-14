from __future__ import annotations

import json
from pathlib import Path

from .dependency_graph import DependencyGraph


class PersistentDependencyGraph(DependencyGraph):
    def __init__(self, path: str | Path) -> None:
        super().__init__(); self.path=Path(path); self.load()

    def load(self) -> None:
        if not self.path.exists(): return
        data=json.loads(self.path.read_text(encoding='utf-8'))
        for upstream, children in data.get('edges',{}).items():
            for child in children: super().add_edge(upstream,child)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True,exist_ok=True)
        payload={'edges':{k:sorted(v) for k,v in sorted(self._children.items())}}
        self.path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

    def add_edge(self, upstream: str, downstream: str) -> None:
        super().add_edge(upstream,downstream); self.save()
