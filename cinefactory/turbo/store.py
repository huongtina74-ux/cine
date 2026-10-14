from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from cinefactory.turbo.contracts import (
    EventState, ExecutionCostSample, FactoryEvent, RepairMemoryEntry,
    ResourceClass, ThroughputSample, WorkerSpec, WorkItem, WorkState,
)


def _dt(v: str | None):
    return datetime.fromisoformat(v) if v else None


class TurboStore:
    """Durable SQLite control-plane store for always-on factory scheduling.

    This is intentionally separate from creative/project truth. It stores only transient
    execution control, worker heartbeats, events, repair statistics and throughput data.
    Restarting the daemon does not lose queued work.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    def _connect(self):
        con = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _init_schema(self) -> None:
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS factory_events(
              event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, project_id TEXT,
              entity_id TEXT, payload_json TEXT NOT NULL, priority INTEGER NOT NULL,
              state TEXT NOT NULL, created_at TEXT NOT NULL, claimed_by TEXT,
              lease_until TEXT, error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_factory_events_state ON factory_events(state, priority, created_at);

            CREATE TABLE IF NOT EXISTS work_items(
              work_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL,
              handler TEXT NOT NULL, resource TEXT NOT NULL, priority INTEGER NOT NULL,
              model_affinity TEXT, dependencies_json TEXT NOT NULL, payload_json TEXT NOT NULL,
              state TEXT NOT NULL, attempts INTEGER NOT NULL, max_attempts INTEGER NOT NULL,
              worker_id TEXT, created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
              lease_until TEXT, last_error TEXT, result_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_work_state ON work_items(state, resource, priority, created_at);
            CREATE INDEX IF NOT EXISTS idx_work_project ON work_items(project_id, state);

            CREATE TABLE IF NOT EXISTS workers(
              worker_id TEXT PRIMARY KEY, resources_json TEXT NOT NULL, capabilities_json TEXT NOT NULL,
              max_concurrent INTEGER NOT NULL, active_model_affinity TEXT, healthy INTEGER NOT NULL,
              last_heartbeat TEXT NOT NULL, metadata_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS repair_memory(
              key TEXT PRIMARY KEY, failure_code TEXT NOT NULL, workflow_id TEXT, shot_class TEXT,
              strategy TEXT NOT NULL, prompt_directive TEXT, attempts INTEGER NOT NULL,
              successes INTEGER NOT NULL, score_sum REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS throughput_samples(
              sample_id TEXT PRIMARY KEY, worker_id TEXT NOT NULL, kind TEXT NOT NULL,
              model_affinity TEXT, duration_seconds REAL NOT NULL, output_units REAL NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_throughput ON throughput_samples(kind, model_affinity, created_at);

            CREATE TABLE IF NOT EXISTS execution_cost_samples(
              sample_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, project_id TEXT NOT NULL,
              worker_id TEXT NOT NULL, kind TEXT NOT NULL, resource TEXT NOT NULL,
              state TEXT NOT NULL, duration_seconds REAL NOT NULL,
              output_units REAL NOT NULL, accepted INTEGER NOT NULL,
              repair_round INTEGER NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_execution_cost_project
              ON execution_cost_samples(project_id, resource, state, created_at);
            """)
            columns={r[1] for r in con.execute("PRAGMA table_info(work_items)").fetchall()}
            if "result_json" not in columns:
                con.execute("ALTER TABLE work_items ADD COLUMN result_json TEXT NOT NULL DEFAULT '{}'")

    # ---------- events ----------
    def publish_event(self, event: FactoryEvent) -> FactoryEvent:
        with self._connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO factory_events(event_id,event_type,project_id,entity_id,payload_json,priority,state,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (event.event_id,event.event_type,event.project_id,event.entity_id,json.dumps(event.payload,ensure_ascii=False),event.priority,event.state.value,event.created_at.isoformat()),
            )
        return event

    def claim_event(self, consumer_id: str, lease_seconds: int = 60) -> FactoryEvent | None:
        now=datetime.now(timezone.utc); lease=now+timedelta(seconds=lease_seconds)
        with self._lock, self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row=con.execute(
                "SELECT * FROM factory_events WHERE (state=? OR (state=? AND lease_until<?)) ORDER BY priority DESC, created_at LIMIT 1",
                (EventState.PENDING.value,EventState.CLAIMED.value,now.isoformat()),
            ).fetchone()
            if not row:
                con.execute("COMMIT"); return None
            con.execute("UPDATE factory_events SET state=?,claimed_by=?,lease_until=? WHERE event_id=?",
                        (EventState.CLAIMED.value,consumer_id,lease.isoformat(),row['event_id']))
            con.execute("COMMIT")
            return FactoryEvent(event_id=row['event_id'],event_type=row['event_type'],project_id=row['project_id'],entity_id=row['entity_id'],payload=json.loads(row['payload_json']),priority=row['priority'],state=EventState.CLAIMED,created_at=_dt(row['created_at']))

    def finish_event(self, event_id: str, success: bool=True, error: str|None=None) -> None:
        state=EventState.DONE if success else EventState.FAILED
        with self._connect() as con:
            con.execute("UPDATE factory_events SET state=?,lease_until=NULL,error=? WHERE event_id=?",(state.value,error,event_id))

    def list_events(self, limit:int=100) -> list[dict]:
        with self._connect() as con:
            rows=con.execute("SELECT * FROM factory_events ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
            return [dict(r) | {"payload":json.loads(r['payload_json'])} for r in rows]

    # ---------- work ----------
    def enqueue_work(self, item: WorkItem) -> tuple[WorkItem,bool]:
        with self._connect() as con:
            cur=con.execute(
                "INSERT OR IGNORE INTO work_items(work_id,project_id,kind,handler,resource,priority,model_affinity,dependencies_json,payload_json,state,attempts,max_attempts,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (item.work_id,item.project_id,item.kind,item.handler,item.resource.value,item.priority,item.model_affinity,json.dumps(item.dependencies),json.dumps(item.payload,ensure_ascii=False),item.state.value,item.attempts,item.max_attempts,item.created_at.isoformat()),
            )
            return item, bool(cur.rowcount)

    def _work_from_row(self,r) -> WorkItem:
        return WorkItem(work_id=r['work_id'],project_id=r['project_id'],kind=r['kind'],handler=r['handler'],resource=ResourceClass(r['resource']),priority=r['priority'],model_affinity=r['model_affinity'],dependencies=json.loads(r['dependencies_json']),payload=json.loads(r['payload_json']),state=WorkState(r['state']),attempts=r['attempts'],max_attempts=r['max_attempts'],worker_id=r['worker_id'],created_at=_dt(r['created_at']),started_at=_dt(r['started_at']),finished_at=_dt(r['finished_at']),last_error=r['last_error'],result=json.loads(r['result_json']) if 'result_json' in r.keys() and r['result_json'] else {})

    def get_work(self, work_id:str) -> WorkItem:
        with self._connect() as con:
            r=con.execute("SELECT * FROM work_items WHERE work_id=?",(work_id,)).fetchone()
            if not r: raise KeyError(work_id)
            return self._work_from_row(r)

    def list_work(self, states:Iterable[WorkState]|None=None, limit:int=500) -> list[WorkItem]:
        with self._connect() as con:
            if states:
                vals=[s.value for s in states]; marks=','.join('?' for _ in vals)
                rows=con.execute(f"SELECT * FROM work_items WHERE state IN ({marks}) ORDER BY priority DESC,created_at LIMIT ?",(*vals,limit)).fetchall()
            else:
                rows=con.execute("SELECT * FROM work_items ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
            return [self._work_from_row(r) for r in rows]

    def dependency_states(self, ids:list[str]) -> dict[str,WorkState]:
        if not ids: return {}
        marks=','.join('?' for _ in ids)
        with self._connect() as con:
            rows=con.execute(f"SELECT work_id,state FROM work_items WHERE work_id IN ({marks})",ids).fetchall()
        return {r['work_id']:WorkState(r['state']) for r in rows}

    def propagate_blocked_dependencies(self) -> int:
        terminal={WorkState.QC_REJECTED,WorkState.DEAD_LETTER,WorkState.CANCELLED,WorkState.BLOCKED}; total=0
        with self._lock:
            while True:
                changed=0
                with self._connect() as con:
                    rows=con.execute("SELECT work_id,dependencies_json FROM work_items WHERE state IN (?,?)",(WorkState.QUEUED.value,WorkState.RETRY.value)).fetchall()
                    for r in rows:
                        deps=json.loads(r['dependencies_json'])
                        if not deps:continue
                        marks=','.join('?' for _ in deps); states={x['work_id']:WorkState(x['state']) for x in con.execute(f"SELECT work_id,state FROM work_items WHERE work_id IN ({marks})",deps).fetchall()}; failed=[d for d,state in states.items() if state in terminal]
                        if failed:
                            con.execute("UPDATE work_items SET state=?,finished_at=?,lease_until=NULL,last_error=? WHERE work_id=?",(WorkState.BLOCKED.value,datetime.now(timezone.utc).isoformat(),f"DEPENDENCY_FAILED:{','.join(failed)}",r['work_id'])); changed+=1
                total+=changed
                if changed==0:break
        return total

    def ready_work_count(self, worker:WorkerSpec) -> int:
        allowed={r.value for r in worker.resources}; ready=0
        now=datetime.now(timezone.utc)
        for item in self.list_work(states=[WorkState.QUEUED,WorkState.RETRY],limit=2000):
            if item.resource.value not in allowed or (worker.capabilities and item.handler not in worker.capabilities):continue
            not_before=item.payload.get("_not_before_utc")
            if not_before:
                try:
                    if datetime.fromisoformat(str(not_before)) > now:
                        continue
                except ValueError:
                    pass
            states=self.dependency_states(item.dependencies)
            if item.dependencies and (len(states)!=len(item.dependencies) or any(x is not WorkState.SUCCESS for x in states.values())):continue
            ready+=1
        return ready

    def claim_work(self, worker:WorkerSpec, lease_seconds:int=900) -> WorkItem|None:
        self.propagate_blocked_dependencies()
        now=datetime.now(timezone.utc); lease=now+timedelta(seconds=lease_seconds)
        allowed=[r.value for r in worker.resources]
        with self._lock, self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            marks=','.join('?' for _ in allowed)
            rows=con.execute(
                f"SELECT * FROM work_items WHERE resource IN ({marks}) AND (state IN (?,?) OR (state=? AND lease_until<?)) ORDER BY priority DESC, created_at LIMIT 250",
                (*allowed,WorkState.QUEUED.value,WorkState.RETRY.value,WorkState.CLAIMED.value,now.isoformat()),
            ).fetchall()
            candidates=[]
            for r in rows:
                deps=json.loads(r['dependencies_json'])
                states=self.dependency_states(deps)
                if deps and (len(states)!=len(deps) or any(s is not WorkState.SUCCESS for s in states.values())):
                    continue
                capability_ok = not worker.capabilities or r['handler'] in worker.capabilities
                if not capability_ok: continue
                payload=json.loads(r['payload_json'])
                not_before=payload.get("_not_before_utc")
                if not_before:
                    try:
                        if datetime.fromisoformat(str(not_before)) > now:
                            continue
                    except ValueError:
                        pass
                required_vram=float(payload.get('required_vram_gb',0) or 0)
                affinity_match=bool(
                    worker.active_model_affinity
                    and r['model_affinity']==worker.active_model_affinity
                )
                runtime_managed_vram=bool(
                    payload.get('runtime_managed_vram',False)
                )
                effective_vram=required_vram
                if affinity_match or runtime_managed_vram:
                    effective_vram=float(
                        payload.get(
                            'hot_model_incremental_vram_gb',
                            required_vram,
                        )
                        or 0
                    )
                if r['resource']==ResourceClass.GPU.value:
                    snapshot=worker.metadata.get('gpu') or {}
                    gpus=snapshot.get('gpus') or []
                    if gpus:
                        gpu=gpus[0]
                        total_gb=float(gpu.get('vram_mb',0))/1024
                        free_gb=(float(gpu.get('vram_mb',0))-float(gpu.get('vram_used_mb',0)))/1024
                        reserve_gb=float(worker.metadata.get('vram_reserve_gb',0) or 0)
                        if (
                            runtime_managed_vram
                            and required_vram>0
                            and required_vram>total_gb
                        ):
                            continue
                        if effective_vram>max(0,free_gb-reserve_gb):
                            continue
                affinity_bonus=100 if affinity_match else 0
                # Prefer hot-model work first, then priority, then FIFO.
                candidates.append((affinity_bonus + int(r['priority']), r))
            if not candidates:
                con.execute("COMMIT"); return None
            _,r=max(candidates,key=lambda x:(x[0],-datetime.fromisoformat(x[1]['created_at']).timestamp()))
            attempts=int(r['attempts'])+1
            con.execute("UPDATE work_items SET state=?,worker_id=?,attempts=?,started_at=?,lease_until=? WHERE work_id=?",
                        (WorkState.CLAIMED.value,worker.worker_id,attempts,now.isoformat(),lease.isoformat(),r['work_id']))
            con.execute("COMMIT")
            out=self._work_from_row(r); out.state=WorkState.CLAIMED; out.worker_id=worker.worker_id; out.attempts=attempts; out.started_at=now
            return out

    def mark_running(self,work_id:str) -> None:
        with self._connect() as con: con.execute("UPDATE work_items SET state=? WHERE work_id=?",(WorkState.RUNNING.value,work_id))

    def finish_work(self,work_id:str,success:bool,error:str|None=None,result:dict|None=None) -> WorkState:
        now=datetime.now(timezone.utc)
        item=self.get_work(work_id)
        if success: state=WorkState.SUCCESS
        elif item.attempts < item.max_attempts: state=WorkState.RETRY
        else: state=WorkState.DEAD_LETTER
        with self._connect() as con:
            con.execute("UPDATE work_items SET state=?,finished_at=?,lease_until=NULL,last_error=?,result_json=? WHERE work_id=?",(state.value,now.isoformat(),error,json.dumps(result or {},ensure_ascii=False),work_id))
        return state

    def defer_work(
        self,
        work_id: str,
        *,
        delay_seconds: int,
        reason: str,
        result: dict | None = None,
    ) -> WorkState:
        item=self.get_work(work_id)
        payload=dict(item.payload)
        payload["_not_before_utc"]=(
            datetime.now(timezone.utc)
            + timedelta(seconds=max(1,int(delay_seconds)))
        ).isoformat()
        attempts=max(0,int(item.attempts)-1)
        with self._connect() as con:
            con.execute(
                "UPDATE work_items SET state=?,attempts=?,worker_id=NULL,started_at=NULL,finished_at=NULL,lease_until=NULL,last_error=?,result_json=?,payload_json=? WHERE work_id=?",
                (
                    WorkState.RETRY.value,
                    attempts,
                    reason,
                    json.dumps(result or {},ensure_ascii=False),
                    json.dumps(payload,ensure_ascii=False),
                    work_id,
                ),
            )
        return WorkState.RETRY

    def reject_work(
        self,
        work_id: str,
        error: str,
        *,
        result: dict | None = None,
    ) -> WorkState:
        now = datetime.now(timezone.utc)
        with self._connect() as con:
            con.execute(
                "UPDATE work_items SET state=?,finished_at=?,lease_until=NULL,last_error=?,result_json=? WHERE work_id=?",
                (
                    WorkState.QC_REJECTED.value,
                    now.isoformat(),
                    error,
                    json.dumps(result or {}, ensure_ascii=False),
                    work_id,
                ),
            )
        return WorkState.QC_REJECTED

    def cancel_work(self,work_id:str) -> None:
        with self._connect() as con: con.execute("UPDATE work_items SET state=?,lease_until=NULL WHERE work_id=?",(WorkState.CANCELLED.value,work_id))

    # ---------- workers ----------
    def upsert_worker(self,w:WorkerSpec) -> None:
        with self._connect() as con:
            con.execute("""INSERT INTO workers(worker_id,resources_json,capabilities_json,max_concurrent,active_model_affinity,healthy,last_heartbeat,metadata_json)
            VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(worker_id) DO UPDATE SET resources_json=excluded.resources_json,capabilities_json=excluded.capabilities_json,max_concurrent=excluded.max_concurrent,active_model_affinity=excluded.active_model_affinity,healthy=excluded.healthy,last_heartbeat=excluded.last_heartbeat,metadata_json=excluded.metadata_json""",
            (w.worker_id,json.dumps(sorted(x.value for x in w.resources)),json.dumps(sorted(w.capabilities)),w.max_concurrent,w.active_model_affinity,1 if w.healthy else 0,w.last_heartbeat.isoformat(),json.dumps(w.metadata,ensure_ascii=False)))

    def list_workers(self)->list[dict]:
        with self._connect() as con:
            return [dict(r) | {"resources":json.loads(r['resources_json']),"capabilities":json.loads(r['capabilities_json']),"metadata":json.loads(r['metadata_json'])} for r in con.execute("SELECT * FROM workers ORDER BY worker_id").fetchall()]

    def set_worker_health(self,worker_id:str,healthy:bool)->None:
        with self._connect() as con:
            con.execute(
                "UPDATE workers SET healthy=? WHERE worker_id=?",
                (1 if healthy else 0,worker_id),
            )

    # ---------- repair memory ----------
    def record_repair(self, *, key:str, failure_code:str, workflow_id:str|None, shot_class:str|None, strategy:str, prompt_directive:str|None, success:bool, score:float=0.0) -> None:
        with self._connect() as con:
            row=con.execute("SELECT * FROM repair_memory WHERE key=?",(key,)).fetchone()
            if row:
                con.execute("UPDATE repair_memory SET attempts=attempts+1,successes=successes+?,score_sum=score_sum+? WHERE key=?",(1 if success else 0,float(score),key))
            else:
                con.execute("INSERT INTO repair_memory(key,failure_code,workflow_id,shot_class,strategy,prompt_directive,attempts,successes,score_sum) VALUES(?,?,?,?,?,?,?,?,?)",(key,failure_code,workflow_id,shot_class,strategy,prompt_directive,1,1 if success else 0,float(score)))

    def best_repair(self, *, failure_code:str, workflow_id:str|None, shot_class:str|None) -> RepairMemoryEntry|None:
        with self._connect() as con:
            rows=con.execute("SELECT * FROM repair_memory WHERE failure_code=? AND (workflow_id=? OR workflow_id IS NULL) AND (shot_class=? OR shot_class IS NULL)",(failure_code,workflow_id,shot_class)).fetchall()
            if not rows: return None
            def score(r):
                attempts=max(1,int(r['attempts'])); rate=int(r['successes'])/attempts; avg=float(r['score_sum'])/attempts
                return (rate,avg,attempts)
            r=max(rows,key=score); attempts=int(r['attempts'])
            return RepairMemoryEntry(key=r['key'],failure_code=r['failure_code'],workflow_id=r['workflow_id'],shot_class=r['shot_class'],strategy=r['strategy'],prompt_directive=r['prompt_directive'],attempts=attempts,successes=int(r['successes']),average_score=float(r['score_sum'])/max(1,attempts))

    # ---------- execution cost ----------
    def add_execution_cost(self, s: ExecutionCostSample) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO execution_cost_samples(
                  sample_id,work_id,project_id,worker_id,kind,resource,state,
                  duration_seconds,output_units,accepted,repair_round,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    s.sample_id,
                    s.work_id,
                    s.project_id,
                    s.worker_id,
                    s.kind,
                    s.resource.value,
                    s.state.value,
                    s.duration_seconds,
                    s.output_units,
                    1 if s.accepted else 0,
                    s.repair_round,
                    s.created_at.isoformat(),
                ),
            )

    def execution_cost_for_work_ids(
        self,
        work_ids: list[str],
    ) -> dict:
        if not work_ids:
            return {
                "samples": 0,
                "total_seconds": 0.0,
                "gpu_seconds": 0.0,
                "gpu_wasted_seconds": 0.0,
                "gpu_waste_ratio": 0.0,
                "mean_gpu_attempt_seconds": 0.0,
                "accepted_gpu_samples": 0,
                "rejected_gpu_samples": 0,
            }
        marks = ",".join("?" for _ in work_ids)
        with self._connect() as con:
            rows = con.execute(
                f"""
                SELECT resource,state,duration_seconds,accepted,repair_round,kind
                FROM execution_cost_samples
                WHERE work_id IN ({marks})
                ORDER BY created_at
                """,
                tuple(work_ids),
            ).fetchall()

        total_seconds = sum(
            float(row["duration_seconds"] or 0.0)
            for row in rows
        )
        gpu_rows = [
            row
            for row in rows
            if row["resource"] == ResourceClass.GPU.value
        ]
        gpu_seconds = sum(
            float(row["duration_seconds"] or 0.0)
            for row in gpu_rows
        )
        gpu_wasted = sum(
            float(row["duration_seconds"] or 0.0)
            for row in gpu_rows
            if not bool(row["accepted"])
        )
        accepted_gpu = sum(
            1
            for row in gpu_rows
            if bool(row["accepted"])
        )
        rejected_gpu = len(gpu_rows) - accepted_gpu
        return {
            "samples": len(rows),
            "total_seconds": total_seconds,
            "gpu_seconds": gpu_seconds,
            "gpu_wasted_seconds": gpu_wasted,
            "gpu_waste_ratio": (
                gpu_wasted / gpu_seconds
                if gpu_seconds > 0
                else 0.0
            ),
            "mean_gpu_attempt_seconds": (
                gpu_seconds / len(gpu_rows)
                if gpu_rows
                else 0.0
            ),
            "accepted_gpu_samples": accepted_gpu,
            "rejected_gpu_samples": rejected_gpu,
        }

    def execution_cost_summary(
        self,
        *,
        project_id: str | None = None,
    ) -> dict:
        where = ""
        args: tuple = ()
        if project_id is not None:
            where = " WHERE project_id=?"
            args = (project_id,)
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT resource,state,COUNT(*) samples,
                       SUM(duration_seconds) seconds,
                       SUM(output_units) units,
                       SUM(CASE WHEN accepted=1 THEN duration_seconds ELSE 0 END)
                         accepted_seconds,
                       SUM(CASE WHEN accepted=0 THEN duration_seconds ELSE 0 END)
                         wasted_seconds
                FROM execution_cost_samples
                """
                + where
                + " GROUP BY resource,state ORDER BY resource,state",
                args,
            ).fetchall()
            render_rows = con.execute(
                """
                SELECT resource,state,kind,repair_round,accepted,
                       duration_seconds,output_units
                FROM execution_cost_samples
                """
                + where
                + (
                    " AND kind LIKE 'block.render%'"
                    if where
                    else " WHERE kind LIKE 'block.render%'"
                )
                + " ORDER BY created_at",
                args,
            ).fetchall()
        by_state = []
        total_seconds = 0.0
        accepted_seconds = 0.0
        wasted_seconds = 0.0
        gpu_seconds = 0.0
        gpu_wasted_seconds = 0.0
        for row in rows:
            seconds = float(row["seconds"] or 0.0)
            accepted = float(row["accepted_seconds"] or 0.0)
            wasted = float(row["wasted_seconds"] or 0.0)
            total_seconds += seconds
            accepted_seconds += accepted
            wasted_seconds += wasted
            if row["resource"] == ResourceClass.GPU.value:
                gpu_seconds += seconds
                gpu_wasted_seconds += wasted
            by_state.append(
                {
                    "resource": row["resource"],
                    "state": row["state"],
                    "samples": int(row["samples"]),
                    "seconds": seconds,
                    "units": float(row["units"] or 0.0),
                    "accepted_seconds": accepted,
                    "wasted_seconds": wasted,
                }
            )

        gpu_render_rows = [
            row
            for row in render_rows
            if row["resource"] == ResourceClass.GPU.value
        ]
        first_pass = [
            row
            for row in gpu_render_rows
            if row["kind"] == "block.render"
            and int(row["repair_round"] or 0) == 0
        ]
        repairs = [
            row
            for row in gpu_render_rows
            if row["kind"] == "block.render.repair"
        ]
        method_switches = [
            row
            for row in gpu_render_rows
            if row["kind"] == "block.render.method_switch"
        ]
        first_pass_accepted = sum(
            1 for row in first_pass if bool(row["accepted"])
        )
        repair_successes = sum(
            1 for row in repairs if bool(row["accepted"])
        )
        method_switch_successes = sum(
            1
            for row in method_switches
            if bool(row["accepted"])
        )
        accepted_render_count = sum(
            1 for row in gpu_render_rows if bool(row["accepted"])
        )
        gpu_render_seconds = sum(
            float(row["duration_seconds"] or 0.0)
            for row in gpu_render_rows
        )

        return {
            "project_id": project_id,
            "samples": sum(row["samples"] for row in by_state),
            "total_seconds": total_seconds,
            "accepted_seconds": accepted_seconds,
            "wasted_seconds": wasted_seconds,
            "gpu_seconds": gpu_seconds,
            "gpu_wasted_seconds": gpu_wasted_seconds,
            "waste_ratio": (
                wasted_seconds / total_seconds
                if total_seconds > 0
                else 0.0
            ),
            "gpu_waste_ratio": (
                gpu_wasted_seconds / gpu_seconds
                if gpu_seconds > 0
                else 0.0
            ),
            "render_samples": len(gpu_render_rows),
            "first_pass_samples": len(first_pass),
            "first_pass_accepted": first_pass_accepted,
            "first_pass_yield": (
                first_pass_accepted / len(first_pass)
                if first_pass
                else 0.0
            ),
            "repair_samples": len(repairs),
            "repair_successes": repair_successes,
            "repair_success_rate": (
                repair_successes / len(repairs)
                if repairs
                else 0.0
            ),
            "method_switch_samples": len(method_switches),
            "method_switch_successes": (
                method_switch_successes
            ),
            "method_switch_success_rate": (
                method_switch_successes
                / len(method_switches)
                if method_switches
                else 0.0
            ),
            "accepted_render_count": accepted_render_count,
            "gpu_render_seconds": gpu_render_seconds,
            "gpu_seconds_per_accepted_render": (
                gpu_render_seconds / accepted_render_count
                if accepted_render_count
                else None
            ),
            "by_state": by_state,
        }

    # ---------- throughput ----------
    def add_throughput(self,s:ThroughputSample)->None:
        with self._connect() as con:
            con.execute("INSERT INTO throughput_samples(sample_id,worker_id,kind,model_affinity,duration_seconds,output_units,created_at) VALUES(?,?,?,?,?,?,?)",(s.sample_id,s.worker_id,s.kind,s.model_affinity,s.duration_seconds,s.output_units,s.created_at.isoformat()))

    def throughput_summary(self)->list[dict]:
        with self._connect() as con:
            rows=con.execute("""SELECT kind,model_affinity,COUNT(*) samples,SUM(output_units) units,SUM(duration_seconds) seconds FROM throughput_samples GROUP BY kind,model_affinity ORDER BY kind,model_affinity""").fetchall()
            out=[]
            for r in rows:
                secs=float(r['seconds']); units=float(r['units'])
                out.append({"kind":r['kind'],"model_affinity":r['model_affinity'],"samples":r['samples'],"units":units,"seconds":secs,"seconds_per_unit":secs/units if units else None})
            return out

    def status(self)->dict:
        with self._connect() as con:
            work={r['state']:r['n'] for r in con.execute("SELECT state,COUNT(*) n FROM work_items GROUP BY state").fetchall()}
            events={r['state']:r['n'] for r in con.execute("SELECT state,COUNT(*) n FROM factory_events GROUP BY state").fetchall()}
        return {
            "work": work,
            "events": events,
            "workers": self.list_workers(),
            "throughput": self.throughput_summary(),
            "execution_cost": self.execution_cost_summary(),
        }
