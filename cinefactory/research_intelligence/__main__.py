"""CLI: python -m cinefactory.research_intelligence observe|dispatch|compare ..."""
import argparse
import json
from pathlib import Path
from .core import observe_video, create_department_tasks, assess_production, _write_json


def main():
    parser = argparse.ArgumentParser(description="CineFactory Research Intelligence")
    commands = parser.add_subparsers(dest="cmd", required=True)
    obs = commands.add_parser("observe", help="Sample authorized local video")
    obs.add_argument("video")
    obs.add_argument("output")
    obs.add_argument("--interval", type=int, default=15)
    obs.add_argument("--max-frames", type=int, default=100)
    task = commands.add_parser("dispatch", help="Prepare reviewable Claude Code department tasks")
    task.add_argument("observation")
    task.add_argument("output")
    task.add_argument("--niche", required=True)
    task.add_argument("--reference-id", required=True)
    task.add_argument("--approved", action="store_true")
    task.add_argument("--all-departments", action="store_true", help="Override focused department routing")
    cmp = commands.add_parser("compare", help="Compare measured owned/reference videos")
    cmp.add_argument("reference")
    cmp.add_argument("produced")
    cmp.add_argument("output")
    cmp.add_argument("--analytics")
    cmp.add_argument('--studio-report', help='Validated owner-authorized Studio CSV import JSON')
    cmp.add_argument('--owned-video-id', help='Exact 11-character video ID from owner report')
    run = commands.add_parser('run-claude', help='Manually execute a pre-approved department task, bounded budget')
    run.add_argument('task')
    run.add_argument('output')
    run.add_argument('--max-budget-usd', type=float, default=0.50)
    review = commands.add_parser('review', help='Validate structured department findings')
    review.add_argument('task')
    review.add_argument('findings')
    review.add_argument('output')
    learning = commands.add_parser('learn', help='Propose controlled improvement experiments')
    learning.add_argument('feedback')
    learning.add_argument('reviews', nargs='+')
    learning.add_argument('--output', required=True)
    qc = commands.add_parser('qc', help='Validate measured production video technical quality')
    qc.add_argument('observation')
    qc.add_argument('output')
    qc.add_argument('--min-width', type=int, default=1920)
    qc.add_argument('--min-height', type=int, default=1080)
    qc.add_argument('--expected-duration', type=float)
    smart = commands.add_parser('smart-observe', help='Bounded opening/visual-change/full-video sampling')
    smart.add_argument('video')
    smart.add_argument('output')
    smart.add_argument('--max-frames', type=int, default=24)
    triage = commands.add_parser('triage', help='Score niche evidence before spending model budget')
    triage.add_argument('candidates')
    triage.add_argument('output')
    triage.add_argument('--max-deep', type=int, default=3)
    studio = commands.add_parser('studio-import', help='No-key YouTube Studio CSV import, authorized channel only')
    studio.add_argument('csv_file')
    studio.add_argument('output')
    studio.add_argument('--start', required=True)
    studio.add_argument('--end', required=True)
    studio.add_argument('--channel-id', required=True)
    retention = commands.add_parser('retention', help='Analyze measured audience-retention points')
    retention.add_argument('points_json')
    retention.add_argument('output')
    retention.add_argument('--min-drop-points', type=float, default=8)
    retention.add_argument('--observation', help='Owned video observation; link nearby sampled frames')
    ledger = commands.add_parser('council-evidence', help='Freeze a shared, hash-verified evidence registry')
    ledger.add_argument('sources_json')
    ledger.add_argument('output')
    council_round = commands.add_parser('council-round', help='Prepare per-department shared-issue Claude tasks')
    council_round.add_argument('issue_json')
    council_round.add_argument('evidence_json')
    council_round.add_argument('observation_json')
    council_round.add_argument('output_dir')
    council_round.add_argument('--niche', required=True)
    council_round.add_argument('--round', choices=['initial', 'rebuttal'], default='initial')
    council_round.add_argument('--previous-opinions')
    council_round.add_argument('--approved', action='store_true')
    ci = commands.add_parser('council-import', help='Validate one structured Claude opinion against shared evidence')
    ci.add_argument('task_json')
    ci.add_argument('claude_result_json')
    ci.add_argument('evidence_json')
    ci.add_argument('output')
    cd = commands.add_parser('council-decide', help='Deterministic arbitration of same-issue opinions')
    cd.add_argument('issue_json')
    cd.add_argument('evidence_json')
    cd.add_argument('opinions_json')
    cd.add_argument('output')
    cc = commands.add_parser('council-challenge', help='Generate peer-to-peer disagreement questions')
    cc.add_argument('decision_json')
    cc.add_argument('output')
    cl = commands.add_parser('council-learn', help='Require council, owned video outcomes and QC')
    cl.add_argument('decision_json')
    cl.add_argument('feedback_json')
    cl.add_argument('quality_json')
    cl.add_argument('evidence_json')
    cl.add_argument('output')
    cm = commands.add_parser('council-case', help='Write ONE authoritative versioned decision and next action')
    cm.add_argument('issue_json')
    cm.add_argument('evidence_json')
    cm.add_argument('opinions_json')
    cm.add_argument('output_dir')
    cm.add_argument('--feedback-json')
    cm.add_argument('--quality-json')
    bridge = commands.add_parser('bridge-import', help='Read Company Youtube niche radar snapshots without modifying scanner')
    bridge.add_argument('--company-root', required=True)
    bridge.add_argument('--channels', required=True)
    bridge.add_argument('--videos', required=True)
    bridge.add_argument('--output', required=True)
    bridge.add_argument('--niche', required=True)
    bridge.add_argument('--format-key', required=True)
    bridge.add_argument('--review-json')
    bridge.add_argument('--portfolio-json')
    bridge.add_argument('--as-of')
    bridge.add_argument('--max-age-hours', type=int, default=48)
    activation = commands.add_parser('pod-activate', help='Create a reviewed niche pod, without scheduling tasks')
    activation.add_argument('--company-root', required=True)
    activation.add_argument('--bridge', required=True)
    activation.add_argument('--gate', required=True)
    activation.add_argument('--owner-event', required=True)
    activation.add_argument('--output-root', required=True)
    activation.add_argument('--as-of')
    pod_watch = commands.add_parser('pod-watch', help='Read-only competitor/fresh-video analysis of approved niche snapshots')
    pod_watch.add_argument('--pod', required=True)
    pod_watch.add_argument('--current-bridge', required=True)
    pod_watch.add_argument('--previous-bridge')
    pod_watch.add_argument('--output', required=True)
    pod_watch.add_argument('--as-of')
    shot_timeline = commands.add_parser('shot-timeline', help='Measure real shot boundaries on locally authorized footage')
    shot_timeline.add_argument('video')
    shot_timeline.add_argument('output')
    shot_timeline.add_argument('--permission', required=True, choices=['OWNED','LICENSED','SOURCE_OWNER_PERMISSION'])
    shot_timeline.add_argument('--max-seconds', type=int, default=180)
    shot_timeline.add_argument('--fps', type=int, default=3)
    pod_batch = commands.add_parser('pod-dispatch', help='Produce source-verified niche watches and per-video research work orders')
    pod_batch.add_argument('--pods-root', required=True)
    pod_batch.add_argument('--bridges-root', required=True)
    pod_batch.add_argument('--output-root', required=True)
    pod_batch.add_argument('--as-of')
    pod_batch.add_argument('--max-pods', type=int, default=50)
    pod_batch.add_argument('--authorized-media-manifest')
    pod_batch.add_argument('--max-media-videos', type=int, default=3)
    media_mechanics = commands.add_parser('media-mechanics', help='Study cuts and audio silences in explicitly authorized local footage')
    media_mechanics.add_argument('video')
    media_mechanics.add_argument('output_dir')
    media_mechanics.add_argument('--permission', required=True, choices=['OWNED','LICENSED','SOURCE_OWNER_PERMISSION'])
    media_mechanics.add_argument('--max-seconds', type=int, default=1800)
    media_mechanics.add_argument('--fps', type=int, default=3)
    daily = commands.add_parser('daily-run', help='Run canonical Company scanner once per day with evidence snapshots')
    daily.add_argument('--company-root', required=True)
    daily.add_argument('--state-root', required=True)
    daily.add_argument('--day')
    daily.add_argument('--retry', action='store_true')
    daily.add_argument('--dry-run', action='store_true')
    daily.add_argument('--timeout', type=int, default=5400)
    daily.add_argument('--profile', choices=['standard','light','focused'], default='standard')
    health = commands.add_parser('daily-health', help='Read persisted health and report missed/blocked daily runs')
    health.add_argument('--state-root', required=True)
    health.add_argument('--max-age-hours', type=int, default=36)
    official = commands.add_parser('official-breakout-audit', help='Strict evidence audit for canonical YouTube Data API artifacts')
    official.add_argument('official_json')
    official.add_argument('output_json')
    official.add_argument('--observed-at')
    prescreen = commands.add_parser('public-prescreen', help='Rank public youtubei.js leads for exact-data verification')
    prescreen.add_argument('--company-root', required=True)
    prescreen.add_argument('--run-dir', required=True)
    prescreen.add_argument('--output', required=True)
    prescreen.add_argument('--max-candidates', type=int, default=20)
    prescreen.add_argument('--as-of')
    targeted = commands.add_parser('targeted-verify', help='Quota-limited channels.list/videos.list for shortlisted IDs')
    targeted.add_argument('--prescreen', required=True)
    targeted.add_argument('--output-dir', required=True)
    targeted.add_argument('--max-channels', type=int, default=8)
    targeted.add_argument('--max-requests', type=int, default=4)
    review_prep = commands.add_parser('five-gate-review-prep', help='Create a pending, source-backed human review worklist')
    review_prep.add_argument('--official-artifact', required=True)
    review_prep.add_argument('--breakout-audit', required=True)
    review_prep.add_argument('--output', required=True)
    review_prep.add_argument('--as-of')
    gates = commands.add_parser('five-gate-dossier', help='Unify exact video, evergreen, entry and cost evidence into one council case')
    gates.add_argument('--official-artifact', required=True)
    gates.add_argument('--breakout-audit', required=True)
    gates.add_argument('--review', required=True)
    gates.add_argument('--output-dir', required=True)
    gates.add_argument('--as-of')
    gates.add_argument('--portfolio-json')
    gate_final = commands.add_parser('five-gate-council-finalize', help='Apply real council opinions to existing five-gate case')
    gate_final.add_argument('--case-dir', required=True)
    gate_final.add_argument('--opinions', required=True)
    live_ev = commands.add_parser('evidence-live', help='Run bounded canonical search + catalogs + evidence QA + council packet')
    live_ev.add_argument('--company-root', required=True)
    live_ev.add_argument('--queries-json', required=True)
    live_ev.add_argument('--youtubejs-entry', required=True)
    live_ev.add_argument('--output-dir', required=True)
    live_ev.add_argument('--niche', required=True)
    live_ev.add_argument('--max-channels', type=int, default=6)
    live_ev.add_argument('--max-results', type=int, default=7)
    live_ev.add_argument('--videos-per-channel', type=int, default=12)
    live_ev.add_argument('--timeout', type=int, default=180)
    live_ev.add_argument('--deep-thumbnails', type=int, default=0)
    evidence_plan = commands.add_parser('evidence-plan', help='Balanced source-backed public competitor shortlist')
    evidence_plan.add_argument('--search', required=True)
    evidence_plan.add_argument('--output-dir', required=True)
    evidence_plan.add_argument('--niche', required=True)
    evidence_plan.add_argument('--max-channels', type=int, default=6)
    evidence_plan.add_argument('--as-of')
    evidence_analyze = commands.add_parser('evidence-analyze', help='Join public search + video catalogs into a QA evidence pack')
    evidence_analyze.add_argument('--plan', required=True)
    evidence_analyze.add_argument('--catalog', required=True)
    evidence_analyze.add_argument('--output', required=True)
    evidence_analyze.add_argument('--as-of')
    evidence_council = commands.add_parser('evidence-council', help='Create shared-issue council review for public evidence')
    evidence_council.add_argument('--evidence', required=True)
    evidence_council.add_argument('--output-dir', required=True)
    deep_verify = commands.add_parser('deep-video-verify', help='Verify frozen source, one CineCouncil issue and thumbnail hashes')
    deep_verify.add_argument('--review', required=True)
    deep = commands.add_parser('deep-video-public', help='Prepare real public thumbnails and pending semantic review tasks')
    deep.add_argument('--evidence', required=True)
    deep.add_argument('--output-dir', required=True)
    deep.add_argument('--max-videos', type=int, default=4)
    local = commands.add_parser('deep-video-local', help='Sample licensed local video frames and audio for approved reviewers')
    local.add_argument('--source', required=True)
    local.add_argument('--output-dir', required=True)
    local.add_argument('--niche', required=True)
    local.add_argument('--video-id', required=True)
    local.add_argument('--authorization', required=True, choices=['OWNED','LICENSED','USER_PROVIDED_WITH_PERMISSION'])
    local.add_argument('--max-frames', type=int, default=16)
    measure = commands.add_parser('scene-measure', help='Compute hash-verified objective stats for real local frame samples')
    measure.add_argument('--observation',required=True)
    measure.add_argument('--output',required=True)
    vision = commands.add_parser('vision-local-review', help='Optional loopback VLM; records unknown when not available')
    vision.add_argument('--source',required=True)
    vision.add_argument('--output',required=True)
    vision.add_argument('--role',choices=['visual','packaging','story','editorial','quality'],default='visual')
    vision.add_argument('--model',default='')
    vision.add_argument('--endpoint',default='http://127.0.0.1:1234/v1/chat/completions')
    vision.add_argument('--max-images',type=int,default=3)
    vision.add_argument('--timeout',type=int,default=35)
    vision.add_argument('--execute',action='store_true')
    vision_qa = commands.add_parser('vision-quality-packet',help='Hold model assertions for independent image QA')
    vision_qa.add_argument('--model-review',required=True)
    vision_qa.add_argument('--output',required=True)
    vlm_gate = commands.add_parser('vlm-smoke-audit',help='Check pinned local VLM CPU benchmark without automatically approving deployment')
    vlm_gate.add_argument('--report',required=True)
    vlm_gate.add_argument('--output',required=True)
    args = parser.parse_args()
    if args.cmd == 'vlm-smoke-audit':
        from .vlm_benchmark_gate import audit_vlm_cpu_benchmark
        result=audit_vlm_cpu_benchmark(args.report,args.output)
    elif args.cmd == 'scene-measure':
        from .scene_measurement import measure_sampled_frames
        result=measure_sampled_frames(args.observation,args.output)
    elif args.cmd == 'vision-local-review':
        from .local_vision_adapter import review_local_vision
        result=review_local_vision(args.source,args.output,role=args.role,model=args.model,
                                    endpoint=args.endpoint,max_images=args.max_images,
                                    timeout_seconds=args.timeout,execute=args.execute)
    elif args.cmd == 'vision-quality-packet':
        from .vision_quality import quality_review_packet
        result=quality_review_packet(args.model_review,args.output)
    elif args.cmd == 'deep-video-verify':
        from .deep_video_intelligence import verify_deep_video_review
        result = verify_deep_video_review(args.review)
    elif args.cmd == 'deep-video-public':
        from .deep_video_intelligence import prepare_public_video_review
        result = prepare_public_video_review(args.evidence,args.output_dir,max_videos=args.max_videos)
    elif args.cmd == 'deep-video-local':
        from .deep_video_intelligence import observe_authorized_footage
        result = observe_authorized_footage(args.source,args.output_dir,niche=args.niche,
                                             video_id=args.video_id,authorization=args.authorization,
                                             max_frames=args.max_frames)
    elif args.cmd == 'evidence-live':
        from .evidence_research import run_live_evidence_research
        result = run_live_evidence_research(args.company_root,args.queries_json,
                                            args.youtubejs_entry,args.output_dir,
                                            niche=args.niche,max_channels=args.max_channels,
                                            max_results_per_query=args.max_results,
                                            videos_per_channel=args.videos_per_channel,
                                            timeout_seconds=args.timeout,
                                            deep_thumbnail_budget=args.deep_thumbnails)
    elif args.cmd == 'evidence-plan':
        from .evidence_research import plan_research_channels
        result = plan_research_channels(args.search, args.output_dir, niche=args.niche,
                                        max_channels=args.max_channels, as_of=args.as_of)
    elif args.cmd == 'evidence-analyze':
        from .evidence_research import analyze_research_evidence
        result = analyze_research_evidence(args.plan,args.catalog,args.output,as_of=args.as_of)
    elif args.cmd == 'evidence-council':
        from .evidence_research import prepare_evidence_council
        result = prepare_evidence_council(args.evidence,args.output_dir)
    elif args.cmd == 'five-gate-review-prep':
        from .five_gate_dossier import prepare_five_gate_review
        result = prepare_five_gate_review(args.official_artifact, args.breakout_audit,
                                          args.output, as_of=args.as_of)
    elif args.cmd == 'five-gate-dossier':
        from .five_gate_dossier import build_five_gate_dossier
        custom = json.loads(Path(args.portfolio_json).read_text(encoding='utf-8')) if args.portfolio_json else None
        result = build_five_gate_dossier(args.official_artifact, args.breakout_audit,
                                         args.review, args.output_dir, as_of=args.as_of, portfolio=custom)
    elif args.cmd == 'five-gate-council-finalize':
        from .five_gate_dossier import finalize_five_gate_council
        result = finalize_five_gate_council(args.case_dir, args.opinions)
    elif args.cmd == 'public-prescreen':
        from .public_prescreen import prescreen_company_public
        result = prescreen_company_public(
            args.company_root, args.run_dir, args.output,
            max_candidates=args.max_candidates, as_of=args.as_of)
    elif args.cmd == 'targeted-verify':
        from .targeted_official import verify_targeted_queue
        result = verify_targeted_queue(
            args.prescreen, args.output_dir, max_channels=args.max_channels,
            max_requests=args.max_requests)
    elif args.cmd == 'official-breakout-audit':
        from .breakout_proof import audit_official_artifact
        result = audit_official_artifact(args.official_json, args.output_json, observed_at=args.observed_at)
    elif args.cmd == 'shot-timeline':
        from .shot_timeline import inspect_shot_timeline
        result = inspect_shot_timeline(args.video, args.output, permission=args.permission,
                                       max_scan_seconds=args.max_seconds, fps=args.fps)
    elif args.cmd == 'pod-dispatch':
        from .pod_dispatch import dispatch_pods_once
        result = dispatch_pods_once(args.pods_root, args.bridges_root, args.output_root,
                                    as_of=args.as_of, max_pods=args.max_pods,
                                    authorized_media_manifest=args.authorized_media_manifest,
                                    max_media_videos=args.max_media_videos)
    elif args.cmd == 'media-mechanics':
        from .media_mechanics import prepare_media_mechanics
        result=prepare_media_mechanics(args.video,args.output_dir,
                                       permission=args.permission,max_scan_seconds=args.max_seconds,
                                       fps=args.fps)
    elif args.cmd == 'daily-run':
        from .daily_research import execute_daily
        budget = ['--queries-per-market','2','--max-queries-per-window','3',
                  '--max-results-per-query','20','--quota-budget','1000',
                  '--max-catalog-channels','35','--dynamic-root-limit','2',
                  '--dynamic-suffix-limit','2','--lane-b-subclusters-per-market','1',
                  '--lane-b-max-results','10','--max-youtubejs-about-channels','35',
                  '--lane-b-catalog-videos','20','--recursive-parent-limit','5',
                  '--recursive-children-per-parent','2','--recursive-batch-size','10',
                  '--recursive-max-catalog-channels','30'] if args.profile == 'light' else None
        if args.profile == 'focused':
            # Partial public source discovery remains nonqualifying without official proof.
            # Omit costly recursive expansion while preserving independent channel lane.
            budget = ['--queries-per-market','1','--max-queries-per-window','2',
                      '--max-results-per-query','8','--quota-budget','500',
                      '--max-catalog-channels','12','--dynamic-root-limit','1',
                      '--dynamic-suffix-limit','1','--lane-b-subclusters-per-market','1',
                      '--lane-b-max-results','4','--max-youtubejs-about-channels','12',
                      '--lane-b-catalog-videos','12','--skip-recursive-expansion']
        result = execute_daily(args.company_root, args.state_root, day=args.day,
                               retry=args.retry, dry_run=args.dry_run, max_seconds=args.timeout,
                               runner_extra=budget)
    elif args.cmd == 'daily-health':
        from .daily_research import daily_health
        result = daily_health(args.state_root, max_age_hours=args.max_age_hours)
    elif args.cmd == 'pod-watch':
        from .pod_watch import watch_niche
        previous = json.loads(Path(args.previous_bridge).read_text(encoding='utf-8')) if args.previous_bridge else None
        result = watch_niche(
            json.loads(Path(args.pod).read_text(encoding='utf-8')),
            json.loads(Path(args.current_bridge).read_text(encoding='utf-8')),
            args.output, previous=previous, as_of=args.as_of)
    elif args.cmd == 'bridge-import':
        from .market_bridge import import_company_snapshot
        review_packet = json.loads(Path(args.review_json).read_text(encoding='utf-8')) if args.review_json else None
        portfolio = json.loads(Path(args.portfolio_json).read_text(encoding='utf-8')) if args.portfolio_json else None
        result = import_company_snapshot(
            args.company_root, args.channels, args.videos, args.output,
            niche=args.niche, format_key=args.format_key, review=review_packet,
            existing_niches=portfolio, as_of=args.as_of, max_snapshot_age_hours=args.max_age_hours)
    elif args.cmd == 'pod-activate':
        from .niche_pod import activate_research_pod
        result = activate_research_pod(
            args.company_root, args.bridge, args.gate, args.owner_event,
            args.output_root, as_of=args.as_of)
    elif args.cmd == 'council-case':
        from .case_controller import consolidate_case
        feedback = json.loads(Path(args.feedback_json).read_text(encoding='utf-8')) if args.feedback_json else None
        quality = json.loads(Path(args.quality_json).read_text(encoding='utf-8')) if args.quality_json else None
        result = consolidate_case(json.loads(Path(args.issue_json).read_text(encoding='utf-8')),
                                  json.loads(Path(args.evidence_json).read_text(encoding='utf-8')),
                                  json.loads(Path(args.opinions_json).read_text(encoding='utf-8')),
                                  args.output_dir, feedback=feedback, technical_qc=quality)
    elif args.cmd == 'council-evidence':
        from .council import collect_evidence
        result = collect_evidence(json.loads(Path(args.sources_json).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'council-round':
        from .workflow import create_round_tasks
        previous = json.loads(Path(args.previous_opinions).read_text(encoding='utf-8')) if args.previous_opinions else None
        result = create_round_tasks(json.loads(Path(args.issue_json).read_text(encoding='utf-8')),
                                    json.loads(Path(args.evidence_json).read_text(encoding='utf-8')),
                                    args.observation_json, args.output_dir, niche=args.niche,
                                    round=args.round, previous_opinions=previous, approved=args.approved)
    elif args.cmd == 'council-import':
        from .workflow import parse_claude_opinion
        result = parse_claude_opinion(json.loads(Path(args.task_json).read_text(encoding='utf-8')),
                                     json.loads(Path(args.claude_result_json).read_text(encoding='utf-8')),
                                     json.loads(Path(args.evidence_json).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'council-decide':
        from .council import run_council
        result = run_council(json.loads(Path(args.issue_json).read_text(encoding='utf-8')),
                             json.loads(Path(args.evidence_json).read_text(encoding='utf-8')),
                             json.loads(Path(args.opinions_json).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'council-challenge':
        from .council import create_challenge_packets
        result = create_challenge_packets(json.loads(Path(args.decision_json).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'council-learn':
        from .council_learning import build_joint_experiment
        result = build_joint_experiment(json.loads(Path(args.decision_json).read_text(encoding='utf-8')),
                                        json.loads(Path(args.feedback_json).read_text(encoding='utf-8')),
                                        json.loads(Path(args.quality_json).read_text(encoding='utf-8')),
                                        json.loads(Path(args.evidence_json).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'studio-import':
        from .analytics_adapter import import_studio_csv
        result = import_studio_csv(args.csv_file, args.output, period_start=args.start, period_end=args.end, channel_id=args.channel_id)
    elif args.cmd == 'retention':
        from .analytics_adapter import retention_drop_candidates
        points = json.loads(Path(args.points_json).read_text(encoding='utf-8'))
        if args.observation:
            from .analytics_adapter import map_retention_to_frames
            result = map_retention_to_frames(json.loads(Path(args.observation).read_text(encoding='utf-8')), points, min_drop_percentage_points=args.min_drop_points)
        else:
            candidates = retention_drop_candidates(points, min_drop_percentage_points=args.min_drop_points)
            result = {'schema': 'cine.research.retention_review.v1', 'drop_candidates': candidates}
        _write_json(Path(args.output), result)
    elif args.cmd == 'smart-observe':
        from .smart import observe_smart
        result = observe_smart(args.video, args.output, max_frames=args.max_frames)
    elif args.cmd == 'triage':
        from .triage import triage_to_file
        result = triage_to_file(json.loads(Path(args.candidates).read_text(encoding='utf-8')), args.output, max_deep_reviews=args.max_deep)
    elif args.cmd == 'qc':
        from .technical_qc import evaluate_video_quality
        result = evaluate_video_quality(json.loads(Path(args.observation).read_text(encoding='utf-8')), args.output, min_width=args.min_width, min_height=args.min_height, expected_duration_seconds=args.expected_duration)
    elif args.cmd == 'review':
        from .learning import ingest_department_result
        result = ingest_department_result(json.loads(Path(args.task).read_text(encoding='utf-8')), json.loads(Path(args.findings).read_text(encoding='utf-8')), args.output)
    elif args.cmd == 'learn':
        from .learning import propose_learning
        result = propose_learning(json.loads(Path(args.feedback).read_text(encoding='utf-8')), [json.loads(Path(p).read_text(encoding='utf-8')) for p in args.reviews], args.output)
    elif args.cmd == 'run-claude':
        from .claude_bridge import run_approved_task
        result = run_approved_task(args.task, args.output, max_budget_usd=args.max_budget_usd)
    elif args.cmd == "observe":
        result = observe_video(args.video, args.output, interval_seconds=args.interval, max_frames=args.max_frames)
    elif args.cmd == "dispatch":
        from .triage import select_departments
        departments = None if args.all_departments else select_departments(args.niche)
        result = create_department_tasks(json.loads(Path(args.observation).read_text(encoding="utf-8")), args.output, niche=args.niche, reference_id=args.reference_id, approved=args.approved, departments=departments)
    else:
        reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
        produced = json.loads(Path(args.produced).read_text(encoding="utf-8"))
        if args.analytics and args.studio_report:
            parser.error('Use either --analytics or --studio-report, not both')
        studio_link = None
        if args.studio_report:
            from .analytics_adapter import select_owned_video
            if not args.owned_video_id:
                parser.error('--studio-report requires --owned-video-id')
            studio_link = select_owned_video(json.loads(Path(args.studio_report).read_text(encoding='utf-8')), args.owned_video_id)
            analytics = studio_link['metrics']
        else:
            analytics = json.loads(Path(args.analytics).read_text(encoding='utf-8')) if args.analytics else None
        result = assess_production(reference, produced, analytics)
        if studio_link:
            result['owned_video_id'] = studio_link['video_id']
            result['owned_analytics_provenance'] = studio_link['source']
        _write_json(Path(args.output), result)
    if args.cmd == 'daily-run':
        print(json.dumps({"schema": result["schema"], "state": result["state"],
                          "day": result["day"], "report": result["canonical_run_dir"]}, ensure_ascii=False))
        if result["state"] not in ("COMPLETE", "DRY_RUN"):
            raise SystemExit(2)
    elif args.cmd == 'pod-dispatch':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "pod_count":result["pods_discovered"],
                          "watches_created":result["watch_reports_created"]},ensure_ascii=False))
        if result["state"] in ("BLOCKED","PARTIAL_BLOCKED"):
            raise SystemExit(2)
    elif args.cmd == 'media-mechanics':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "segment_count":result["segment_count"],
                          "production_permission":False},ensure_ascii=False))
    elif args.cmd == 'shot-timeline':
        print(json.dumps({"schema":result["schema"],"state":result["report_state"],
                          "observed_seconds":result["observed_duration_s"],
                          "segments":result["segment_count"],
                          "semantic_video_analysis_completed":False},ensure_ascii=False))
    elif args.cmd == 'daily-health':
        print(json.dumps(result, ensure_ascii=False))
        if result["status"] != "HEALTHY":
            raise SystemExit(3)
    elif args.cmd == 'vlm-smoke-audit':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "controlled_accuracy":result["controlled_accuracy"],
                          "model_deploy_approved":result["model_deploy_approved"]},ensure_ascii=False))
    elif args.cmd in ('scene-measure','vision-local-review','vision-quality-packet'):
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "production_permission":result["production_permission"]},ensure_ascii=False))
        if args.cmd == 'vision-local-review' and args.execute and not result["inference_completed"]:
            raise SystemExit(2)
    elif args.cmd == 'deep-video-verify':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "verified_thumbnails":result["verified_thumbnails"],
                          "council_issue_id":result["council_issue_id"]},ensure_ascii=False))
    elif args.cmd == 'deep-video-public':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "selected_count":result["selected_count"],
                          "thumbnails_observed":result["thumbnails_observed"]},ensure_ascii=False))
    elif args.cmd == 'deep-video-local':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "frames_observed":result["frames_observed"],
                          "audio_measured":result["audio_measured"]},ensure_ascii=False))
    elif args.cmd == 'evidence-live':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "counts":result.get("counts",{}),
                          "output_dir":args.output_dir},ensure_ascii=False))
        if result["state"]!="REVIEW_PACKET_CREATED":
            raise SystemExit(2)
    elif args.cmd == 'evidence-plan':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "selected_channels":len(result["selected"])},ensure_ascii=False))
    elif args.cmd == 'evidence-analyze':
        print(json.dumps({"schema":result["schema"],"state":result["state"],
                          "counts":result["counts"]},ensure_ascii=False))
    elif args.cmd == 'evidence-council':
        print(json.dumps({"schema":result["schema"],"state":result["state"]},ensure_ascii=False))
    elif args.cmd == 'five-gate-review-prep':
        print(json.dumps({'schema':result['schema'],'state':result['state'],
                          'counts':result['counts']},ensure_ascii=False))
    elif args.cmd in ('five-gate-dossier', 'five-gate-council-finalize'):
        print(json.dumps({"schema":result["schema"], "state":result["state"],
                          "case_id":result["case_id"],
                          "production_permission":result["production_permission"]}, ensure_ascii=False))
    else:
        print(json.dumps({"schema": result["schema"], "status": "ok"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
