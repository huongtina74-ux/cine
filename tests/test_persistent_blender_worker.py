from pathlib import Path
import sys
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import EpisodeSpec,BlenderAnimationJob
from cinefactory.turbo.blender import PersistentBlenderWorker
ROOT=Path(__file__).resolve().parents[1]
def test_same_pid(tmp_path):
    e=EpisodeSpec.model_validate_json((ROOT/'examples/block_animation/original_episode.json').read_text()); c=EpisodeAssembler.from_root(ROOT).compile(e); w=PersistentBlenderWorker(tmp_path,command=[sys.executable,str(ROOT/'scripts/mock_blender_persistent_worker.py')],startup_timeout=5,job_timeout=5)
    try:
        pid=w.start()['pid']
        for i,s in enumerate(c.shots): w.execute_animation(BlenderAnimationJob(project_id='P',episode_id='E',shot=s,output_path=str(tmp_path/f'{i}.mp4'))); assert w.ping()['pid']==pid
    finally:w.close()
