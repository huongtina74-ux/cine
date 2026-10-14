from __future__ import annotations
from pathlib import Path


class StagePromptLibrary:
    FILES={
        'research':'research.md','topic_strategy':'topic_strategy.md','packaging':'packaging.md','originality':'originality.md',
        'story':'story.md','script':'script.md','script_review':'script_review.md','asset_bible':'asset_bible.md',
        'director':'director.md','shot_specs':'shot_specs.md','qc':'qc.md','release_package':'release_package.md',
    }
    def __init__(self,root:str|Path): self.root=Path(root)
    def compose(self,stage:str,user_prompt:str)->str:
        name=self.FILES.get(stage)
        guidance=(self.root/name).read_text(encoding='utf-8') if name and (self.root/name).exists() else ''
        return f"{guidance.strip()}\n\nUSER PROJECT REQUEST:\n{user_prompt.strip()}".strip()
