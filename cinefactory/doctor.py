from __future__ import annotations

import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

from cinefactory.workflows.safety import WorkflowSafetyValidator


class Doctor:
    def __init__(self, ctx) -> None:
        self.ctx=ctx

    @staticmethod
    def _ram_bytes() -> int | None:
        try:
            pages=os.sysconf('SC_PHYS_PAGES'); size=os.sysconf('SC_PAGE_SIZE')
            return int(pages*size)
        except Exception:
            return None

    @staticmethod
    def _gpu() -> dict:
        exe=shutil.which('nvidia-smi')
        if not exe:
            return {'available':False,'devices':[],'detail':'nvidia-smi not found'}
        proc=subprocess.run([
            exe,'--query-gpu=name,memory.total,driver_version','--format=csv,noheader,nounits'
        ],text=True,capture_output=True,check=False,timeout=10)
        if proc.returncode!=0:
            return {'available':False,'devices':[],'detail':proc.stderr[-1000:]}
        devices=[]
        for line in proc.stdout.splitlines():
            parts=[x.strip() for x in line.split(',')]
            if len(parts)>=3:
                devices.append({'name':parts[0],'vram_mb':int(float(parts[1])),'driver':parts[2]})
        return {'available':bool(devices),'devices':devices,'detail':exe}

    def run(self) -> dict:
        checks=[]
        def add(name, ok, detail): checks.append({'name':name,'ok':bool(ok),'detail':detail})
        for cmd in ('ffmpeg','ffprobe'):
            p=shutil.which(cmd); add(cmd, bool(p), p or 'not found')

        add('gpu', True, self._gpu())
        ram=self._ram_bytes(); add('ram', ram is not None, {'bytes':ram} if ram is not None else 'unavailable')
        disk=shutil.disk_usage(self.ctx.root); add('disk', disk.free > 5*1024**3, {'free_bytes':disk.free,'total_bytes':disk.total})

        comfy=self.ctx.settings.get('comfyui',{}).get('base_url','http://127.0.0.1:8188').rstrip('/')
        try:
            with urllib.request.urlopen(comfy+'/system_stats',timeout=1.5) as r:
                add('comfyui', r.status==200, comfy)
        except Exception as exc:
            add('comfyui', False, f'{comfy} unavailable: {exc}')

        manifests=self.ctx.workflows.list()
        safety=WorkflowSafetyValidator()
        workflow_findings=[]
        by_media={}
        for m in manifests:
            by_media[m.media_type]=by_media.get(m.media_type,0)+1
            try:
                report=safety.review(self.ctx.workflows.read_workflow_json(m.workflow_id,m.version))
                if not report.passed: workflow_findings.extend([f'{m.workflow_id}@{m.version}:{x}' for x in report.findings])
            except Exception as exc:
                workflow_findings.append(f'{m.workflow_id}@{m.version}:READ_ERROR:{exc}')
        add('workflow_registry', not workflow_findings, {'count':len(manifests),'by_media':by_media,'findings':workflow_findings})

        models=list(self.ctx.models.items.values())
        approved=[m for m in models if m.approved_for_production and m.commercial_use_reviewed and m.output_terms_reviewed]
        add('model_registry', True, {'count':len(models),'approved':len(approved)})
        add('database', True, str(self.ctx.db.engine.url))
        add('zero_metered_api', not self.ctx.policy.raw.get('production',{}).get('allow_metered_generation_api',False), self.ctx.policy.raw.get('mode'))

        required={'ffmpeg','ffprobe','database','zero_metered_api','workflow_registry'}
        ok=all(c['ok'] for c in checks if c['name'] in required)
        return {'ok':ok,'production_ready_for_real_ai':ok and any(c['name']=='comfyui' and c['ok'] for c in checks) and len(approved)>0 and len(manifests)>0,'checks':checks}
