from pathlib import Path
import pytest
from cinefactory.block_animation.assembler import EpisodeAssembler,EpisodeAssemblyError
from cinefactory.block_animation.contracts import EpisodeSpec
from cinefactory.turbo.contracts import ResourceClass,WorkerSpec
from cinefactory.turbo.store import TurboStore
ROOT=Path(__file__).resolve().parents[1]
def demo(): return EpisodeSpec.model_validate_json((ROOT/'examples/block_animation/original_episode.json').read_text())
def test_compile_all(tmp_path):
    c=EpisodeAssembler.from_root(ROOT).compile(demo(),output_dir=tmp_path); assert c.qc.passed and len(c.shots)==2; assert c.shots[0].reactions and c.shots[0].props and len(c.shots[0].camera_takes)==2
def test_repairs_timing(tmp_path):
    e=demo(); s=e.shots[0].model_copy(update={'duration_seconds':1.0,'actions':[e.shots[0].actions[0].model_copy(update={'start_seconds':.95,'end_seconds':4.0})]}); c=EpisodeAssembler.from_root(ROOT).compile(e.model_copy(update={'shots':[s]}),output_dir=tmp_path); assert c.qc.repairs_applied>=1 and c.shots[0].actions[0].end_seconds<=1
def test_blocks_brand():
    e=demo().model_copy(update={'title':'BigSchool clone'})
    with pytest.raises(EpisodeAssemblyError): EpisodeAssembler.from_root(ROOT).compile(e)
def test_prefill(tmp_path):
    asm=EpisodeAssembler.from_root(ROOT); c=asm.compile(demo(),output_dir=tmp_path); st=TurboStore(tmp_path/'t.db'); p=asm.enqueue(c,st,output_dir=tmp_path); w=WorkerSpec(worker_id='g',resources={ResourceClass.GPU},capabilities={'blender.animation.render'}); assert st.ready_work_count(w)==2 and len(p.render_work_ids)==2
