import threading
from dataclasses import dataclass

from cinefactory.turbo.contracts import ResourceClass, WorkerSpec
from cinefactory.turbo.daemon import FactoryDaemon


@dataclass
class FactoryLane:
    name: str
    daemon: FactoryDaemon


class ContinuousBlockFactory:
    def __init__(self, ctx, *, poll_seconds=.05):
        self.ctx = ctx
        self.poll_seconds = poll_seconds
        self.stop_event = threading.Event()
        self.gpu = FactoryLane(
            "gpu",
            FactoryDaemon(
                ctx,
                WorkerSpec(
                    worker_id="block-gpu-0",
                    resources={ResourceClass.GPU},
                    capabilities={
                        "blender.animation.render",
                        "lab.comfyui.execute",
                        "block.video.comfy",
                    },
                    active_model_affinity=(
                        "BLENDER:BLENDER_EEVEE_NEXT"
                    ),
                ),
                poll_seconds=poll_seconds,
            ),
        )
        self.io = FactoryLane(
            "io",
            FactoryDaemon(
                ctx,
                WorkerSpec(
                    worker_id="block-io-0",
                    resources={ResourceClass.IO},
                    capabilities={
                        "timeline.accept",
                        "block.episode.assemble",
                    },
                ),
                poll_seconds=poll_seconds,
            ),
        )
        self.agent = FactoryLane(
            "agent",
            FactoryDaemon(
                ctx,
                WorkerSpec(
                    worker_id="block-rnd-agent-0",
                    resources={ResourceClass.AGENT},
                    capabilities={
                        "rnd.capability.acquire",
                    },
                ),
                poll_seconds=max(.25, poll_seconds),
            ),
        )

    def _loop(self, lane):
        try:
            while not self.stop_event.is_set():
                if not lane.daemon.tick():
                    self.stop_event.wait(
                        lane.daemon.poll_seconds
                    )
        finally:
            lane.daemon.close()

    def run_forever(self):
        threads = [
            threading.Thread(
                target=self._loop,
                args=(self.io,),
                daemon=True,
            ),
            threading.Thread(
                target=self._loop,
                args=(self.agent,),
                daemon=True,
            ),
        ]
        for thread in threads:
            thread.start()
        try:
            self._loop(self.gpu)
        except KeyboardInterrupt:
            self.stop_event.set()
        finally:
            self.stop_event.set()
            for thread in threads:
                thread.join(timeout=5)
            self.gpu.daemon.close()
            self.io.daemon.close()
            self.agent.daemon.close()

    def tick(self):
        return {
            "gpu": self.gpu.daemon.tick(),
            "io": self.io.daemon.tick(),
            "agent": self.agent.daemon.tick(),
        }
