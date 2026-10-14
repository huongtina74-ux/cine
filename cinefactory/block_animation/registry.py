from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Generic,TypeVar
import yaml
from pydantic import BaseModel
from cinefactory.block_animation.contracts import *
T=TypeVar('T',bound=BaseModel)
class ManifestRegistry(Generic[T]):
    def __init__(self,model_type:type[T],key_field:str): self.model_type=model_type; self.key_field=key_field; self._items={}
    def add(self,item:T):
        key=str(getattr(item,self.key_field))
        if key in self._items: raise ValueError(f'duplicate {self.model_type.__name__} id: {key}')
        self._items[key]=item
    def load_file(self,path:Path,list_key:str):
        if not path.exists(): return self
        raw=yaml.safe_load(path.read_text(encoding='utf-8')) or {}; items=raw.get(list_key,raw if isinstance(raw,list) else [])
        if not isinstance(items,list): raise ValueError(f'{path}: expected a list under {list_key!r}')
        for data in items: self.add(self.model_type.model_validate(data))
        return self
    def get(self,key:str):
        try:return self._items[key]
        except KeyError as exc: raise KeyError(f'unknown {self.model_type.__name__}: {key}') from exc
    def maybe_get(self,key): return self._items.get(key)
    def values(self): return list(self._items.values())
    def keys(self): return list(self._items)
    def __contains__(self,key): return key in self._items
class CharacterRigRegistry(ManifestRegistry[CharacterRigDefinition]):
    def __init__(self): super().__init__(CharacterRigDefinition,'rig_id')
class AnimationClipLibrary(ManifestRegistry[AnimationClipDefinition]):
    def __init__(self): super().__init__(AnimationClipDefinition,'clip_id')
    def ensure_compatible(self,clip_id,skeleton_profile):
        clip=self.get(clip_id)
        if clip.skeleton_profile!=skeleton_profile and skeleton_profile not in clip.compatible_skeleton_profiles:
            raise ValueError(f'clip {clip_id} skeleton {clip.skeleton_profile} != rig skeleton {skeleton_profile}')
        return clip
class ExpressionLibrary(ManifestRegistry[ExpressionDefinition]):
    def __init__(self): super().__init__(ExpressionDefinition,'expression_id')
class ReactionRuleLibrary(ManifestRegistry[ReactionRuleDefinition]):
    def __init__(self): super().__init__(ReactionRuleDefinition,'rule_id')
    def for_trigger(self,trigger): return [x for x in self.values() if x.trigger==trigger]
class PropLibrary(ManifestRegistry[PropDefinition]):
    def __init__(self): super().__init__(PropDefinition,'prop_id')
class SceneTemplateLibrary(ManifestRegistry[SceneTemplateDefinition]):
    def __init__(self): super().__init__(SceneTemplateDefinition,'scene_id')
class CameraGrammarLibrary(ManifestRegistry[CameraPatternDefinition]):
    def __init__(self): super().__init__(CameraPatternDefinition,'pattern_id')
    def for_purpose(self,purpose):
        exact=[x for x in self.values() if x.purpose==purpose]; return exact or [x for x in self.values() if x.purpose=='default']
class CrowdBehaviorLibrary(ManifestRegistry[CrowdBehaviorDefinition]):
    def __init__(self): super().__init__(CrowdBehaviorDefinition,'behavior_id')
class EventLibrary(ManifestRegistry[EventDefinition]):
    def __init__(self): super().__init__(EventDefinition,'event_id')
class RenderQualityLibrary(ManifestRegistry[RenderQualityProfileDefinition]):
    def __init__(self): super().__init__(RenderQualityProfileDefinition,'profile_id')
class BlockAnimationLibraries:
    def __init__(self):
        self.rigs=CharacterRigRegistry(); self.clips=AnimationClipLibrary(); self.expressions=ExpressionLibrary(); self.reactions=ReactionRuleLibrary(); self.props=PropLibrary(); self.scenes=SceneTemplateLibrary(); self.cameras=CameraGrammarLibrary(); self.crowds=CrowdBehaviorLibrary(); self.events=EventLibrary(); self.render_quality=RenderQualityLibrary()
    @classmethod
    def load(cls,root:Path):
        base=Path(root)/'config'/'block_animation'; out=cls()
        for reg,name,key in [(out.rigs,'characters.yaml','characters'),(out.clips,'animations.yaml','animations'),(out.expressions,'expressions.yaml','expressions'),(out.reactions,'reactions.yaml','reactions'),(out.props,'props.yaml','props'),(out.scenes,'scenes.yaml','scenes'),(out.cameras,'camera_grammar.yaml','camera_patterns'),(out.crowds,'crowd_behaviors.yaml','crowd_behaviors'),(out.events,'events.yaml','events'),(out.render_quality,'render_quality.yaml','render_quality_profiles')]: reg.load_file(base/name,key)
        return out
    def fingerprint(self):
        payload={k:[x.model_dump(mode='json') for x in getattr(self,k).values()] for k in ['rigs','clips','expressions','reactions','props','scenes','cameras','crowds','events','render_quality']}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16]
