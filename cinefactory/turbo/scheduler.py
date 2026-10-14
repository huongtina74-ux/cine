from __future__ import annotations

from cinefactory.turbo.contracts import WorkerSpec, WorkItem
from cinefactory.turbo.store import TurboStore


class ModelAffinityScheduler:
    """Durable cross-project scheduler.

    It keeps project truth outside the scheduler and optimizes only execution order.
    Same-model jobs receive a hot-model bonus so a single-GPU machine avoids needless
    model swapping. Dependencies are hard gates, not hints.
    """
    def __init__(self,store:TurboStore)->None:
        self.store=store

    def enqueue(self,item:WorkItem)->tuple[WorkItem,bool]:
        return self.store.enqueue_work(item)

    def claim(self,worker:WorkerSpec)->WorkItem|None:
        self.store.upsert_worker(worker)
        return self.store.claim_work(worker)
