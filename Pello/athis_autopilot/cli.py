import argparse
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import sys
from .supervisor import Supervisor


def main():
    project = Path(__file__).resolve().parent.parent
    cli = argparse.ArgumentParser(prog='pello', description='Pello — desarrollo incremental y automatización de negocio')
    cli.add_argument('--root', type=Path, help='Runtime, state, evidence location')
    sub = cli.add_subparsers(dest='command', required=True)
    start = sub.add_parser('start', help='New autonomous job from a product specification')
    start.add_argument('--spec', type=Path, required=True)
    start.add_argument('--suite', type=Path, required=True, help='Owner-authored independent acceptance suite')
    start.add_argument('--mode', choices=['mock', 'codex'], default='mock')
    demo = sub.add_parser('demo', help='Offline red -> green demonstration using deterministic mock')
    resume = sub.add_parser('resume', help='Resume an existing job from SQLite')
    resume.add_argument('job_id')
    status = sub.add_parser('status', help='Inspect persistent job state')
    status.add_argument('job_id')
    doctor = sub.add_parser('doctor', help='Check prerequisites; does not run model turns')
    doctor.add_argument('--check-auth', action='store_true', help='Read SDK account status without showing credentials')
    login = sub.add_parser('login', help='Authenticate official Codex SDK using ChatGPT')
    login.add_argument('--device', action='store_true', help='Use device-code flow')
    supervised = sub.add_parser('supervised', help='One AI supervisor/executor cycle; at most three SDK turns')
    source = supervised.add_mutually_exclusive_group(required=True)
    source.add_argument('--spec', type=Path, help='Small Markdown product specification')
    source.add_argument('--resume', metavar='PROJECT_ID', help='Continue stored work without repeating completed turns')
    source.add_argument('--status', metavar='PROJECT_ID', help='Read the stored report without model calls')
    supervised.add_argument('--suite', type=Path, help='Independent test directory with manifest.json')
    supervised.add_argument('--project-id', help='Optional unique project identifier')
    supervised.add_argument('--model', default='gpt-6-luna', help='Must be present in the authenticated SDK catalog')
    supervised.add_argument('--effort', choices=['low', 'medium'], default='low')
    supervised.add_argument('--timeout', type=int, default=180, help='Seconds per model turn; no automatic retries')
    pipeline = sub.add_parser('pipeline', help='Pello: plan global e incrementos dependientes verificados')
    pipeline_source = pipeline.add_mutually_exclusive_group(required=True)
    pipeline_source.add_argument('--spec', type=Path)
    pipeline_source.add_argument('--resume', metavar='PROJECT_ID')
    pipeline_source.add_argument('--status', metavar='PROJECT_ID')
    pipeline.add_argument('--suite', type=Path)
    pipeline.add_argument('--manifest', type=Path, help='Contrato de incrementos y herramientas sin secretos')
    pipeline.add_argument('--policy', type=Path, help='Límites y selección de modelos en JSON')
    pipeline.add_argument('--project-id')
    pipeline.add_argument('--timeout', type=int, default=180)
    pipeline.add_argument('--stop-after', type=int, help='Pausa después de N checkpoints de este proceso')
    pilot = sub.add_parser('n8n-pilot', help='QA aislado de Phase 3B por SDK y MCP oficial')
    pilot_source = pilot.add_mutually_exclusive_group(required=True)
    pilot_source.add_argument('--new', action='store_true')
    pilot_source.add_argument('--resume', metavar='PROJECT_ID')
    pilot_source.add_argument('--publish-only', metavar='PROJECT_ID')
    pilot_source.add_argument('--status', metavar='PROJECT_ID')
    pilot_source.add_argument('--stop', metavar='PROJECT_ID')
    pilot_source.add_argument('--reconcile-create', metavar='PROJECT_ID')
    pilot.add_argument('--project-id')
    pilot.add_argument('--timeout', type=int, default=240)
    pilot.add_argument('--stop-after', type=int)
    pilot.add_argument('--authorize-closeout', type=Path,help='Explicit human closeout grant JSON; records without resetting usage')
    pilot.add_argument('--publication-review-round',type=int,choices=[1,2],default=1,help='Round2 only repairs the recorded stage-contract mismatch')
    planning = sub.add_parser('plan-spec', help='Interpret a natural-language product specification and persist its traceable requirements')
    planning_action = planning.add_mutually_exclusive_group(required=True)
    planning_action.add_argument('--create', action='store_true', help='Create a bounded project without invoking a model')
    planning_action.add_argument('--understand', action='store_true', help='Extract structured requirements via the existing SDK Planner')
    planning_action.add_argument('--planner-input', action='store_true', help='Inspect validated accepted requirements without model inference')
    planning_action.add_argument('--review-analysis', action='store_true', help='Independently review a saved analysis')
    planning_action.add_argument('--reprocess-analysis', action='store_true', help='Create an append-only normalized analysis revision from the saved Planner response')
    planning_action.add_argument('--review-increment', metavar='INCREMENT_ID', help='Independent read-only engineering review after objective tests pass')
    planning_action.add_argument('--status', action='store_true', help='Read durable state without invoking a model')
    planning_action.add_argument('--revalidate', action='store_true', help='Create a new immutable version after source changes')
    planning.add_argument('--spec', type=Path, help='Markdown product specification')
    planning.add_argument('--project-id', required=True)
    planning.add_argument('--max-turns', type=int, default=12, help='Project SDK model-turn limit (1-12)')
    planning.add_argument('--duration-minutes', type=int, default=60, help='Project deadline (1-360 minutes)')
    planning.add_argument('--evidence', type=Path, help='Structured engineering review evidence JSON')
    planning.add_argument('--reason', help='Bounded correction rationale required with --reprocess-analysis')
    args = cli.parse_args()
    if args.root is None:
        config_path = project / 'config' / 'pello.json'
        config = json.loads(config_path.read_text(encoding='utf-8-sig')) if config_path.exists() else {}
        args.root = project / config.get('runtime_root', 'runtime')
    if args.command == 'login':
        try:
            from openai_codex import Codex
        except ImportError:
            print('Install SDK first: python -m pip install -r requirements-codex.txt')
            return 2
        with Codex() as codex:
            handle = codex.login_chatgpt_device_code() if args.device else codex.login_chatgpt()
            if args.device:
                print('Open:', handle.verification_url, 'Code:', handle.user_code, flush=True)
            else:
                print('Open:', handle.auth_url, flush=True)
            print('Finish login in your browser. This terminal waits for the SDK confirmation.', flush=True)
            success = bool(handle.wait().success)
            print('Authenticated:', success)
        return 0 if success else 2
    if args.command == 'doctor':
        checks = {
            'python': sys.version.split()[0], 'os': platform.platform(),
            'python_executable': sys.executable,
            'virtual_environment': sys.prefix != sys.base_prefix,
            'git_installed': shutil.which('git') is not None,
            'codex_python_sdk_installed': importlib.util.find_spec('openai_codex') is not None,
            'runtime_root': str(args.root.resolve()),
            'chatgpt_codex_login_verified': None,
            'notes': 'SDK availability is NOT proof of an authenticated, usable Codex account.'
        }
        auth_code = 0
        if args.check_auth and checks['codex_python_sdk_installed']:
            from .installation import check_auth
            auth = check_auth()
            checks['authentication'] = auth
            checks['chatgpt_codex_login_verified'] = auth.get('authenticated', False)
            auth_code = 0 if auth.get('authenticated') else 2
        print(json.dumps(checks, indent=2, ensure_ascii=False))
        return auth_code or (0 if checks['git_installed'] and checks['codex_python_sdk_installed'] else 2)
    if args.command == 'n8n-pilot':
        from .n8n_pipeline import N8nPipeline
        from .engines import CodexBlocked
        try:
            if args.stop_after is not None and args.stop_after < 1:
                cli.error('--stop-after debe ser positivo')
            core = N8nPipeline(args.root, timeout=args.timeout)
            project_id = core.create_qa_project(project_id=args.project_id) if args.new else (
                args.resume or args.publish_only or args.status or args.stop or args.reconcile_create)
            print('PROJECT_ID:', project_id, flush=True)
            if args.authorize_closeout:
                core.journal.authorize_closeout(project_id,json.loads(args.authorize_closeout.read_text(encoding='utf-8')))
            if args.stop:
                (core.folder(project_id)/'STOP').write_text('Emergency STOP requested by operator\n',encoding='utf-8')
            if args.reconcile_create:
                core.journal.reconcile_create(project_id,'create')
                print(json.dumps({'project_id':project_id,'workflow_id':core.journal.resource(project_id)['workflow_id']},indent=2))
                return 0
            result = (core.pipeline_report(project_id) if args.status else core.publish_increment(project_id,review_round=args.publication_review_round) if args.publish_only
                      else core.run_pipeline(project_id,stop_after=args.stop_after))
            print(json.dumps({key:result[key] for key in ('project_id','stage','passed','verified_increments',
                'planned_increments','workflow_id','external_integration','blocker','report_path')},indent=2,ensure_ascii=False))
            return 0 if result['passed'] or (result['stage']=='PAUSED' and result['integrity']) else 2
        except (ValueError,CodexBlocked) as exc:
            print('PELLO N8N ERROR:',exc)
            return 2
        finally:
            if 'core' in locals() and hasattr(core.backend,'close'): core.backend.close()
    if args.command == 'plan-spec':
        from .product_planning import ProductPlanningCore
        from .engines import CodexBlocked, EngineError
        try:
            planning_root = args.root / 'phase3c'
            core = ProductPlanningCore(planning_root)
            if args.create:
                if args.spec is None:
                    cli.error('--create requiere --spec')
                result = {'project_id': core.create_project(args.spec, project_id=args.project_id,
                    max_turns=args.max_turns, duration_minutes=args.duration_minutes), 'status': 'NEW'}
            else:
                if args.spec is not None and not args.revalidate:
                    cli.error('--spec solo aplica con --create o --revalidate')
                if args.understand:
                    result = core.understand(args.project_id)
                elif args.planner_input:
                    result = core.planner_input(args.project_id)
                elif args.review_analysis:
                    result = core.review_analysis(args.project_id)
                elif args.reprocess_analysis:
                    if not args.reason:
                        cli.error('--reprocess-analysis requiere --reason')
                    result = core.reprocess_analysis(args.project_id, reason=args.reason)
                elif args.review_increment:
                    if args.evidence is None:
                        cli.error('--review-increment requiere --evidence')
                    result = core.review_engineering_increment(args.project_id, args.review_increment,
                        evidence=json.loads(args.evidence.read_text(encoding='utf-8-sig')))
                elif args.revalidate:
                    result = {'project_id': args.project_id, 'version': core.revalidate(args.project_id, args.spec), 'status': 'NEW'}
                else:
                    result = core.status(args.project_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        except (ValueError, CodexBlocked, EngineError) as exc:
            print('PELLO PLAN-SPEC ERROR:', exc)
            return 2
        finally:
            if 'core' in locals() and hasattr(core.backend, 'close'): core.backend.close()
    if args.command == 'pipeline':
        from .pipeline import IncrementalPipeline
        from .pipeline_contracts import PipelinePolicy
        try:
            if args.stop_after is not None and args.stop_after < 1:
                cli.error('--stop-after debe ser positivo')
            core = IncrementalPipeline(args.root, timeout=args.timeout)
            if args.spec:
                if args.suite is None or args.manifest is None:
                    cli.error('--spec requiere --suite y --manifest')
                policy = PipelinePolicy.model_validate_json(args.policy.read_text(encoding='utf-8-sig')) if args.policy else PipelinePolicy()
                project_id = core.create_pipeline(args.spec, args.suite, args.manifest, policy=policy, project_id=args.project_id)
            else:
                if args.policy:
                    cli.error('La política queda fijada al crear el proyecto')
                project_id = args.resume or args.status
            print('PROJECT_ID:', project_id, flush=True)
            result = core.pipeline_report(project_id) if args.status else core.run_pipeline(project_id, stop_after=args.stop_after)
            print(json.dumps({key: result[key] for key in ('project_id', 'stage', 'evidence_class', 'passed',
                'verified_increments', 'planned_increments', 'acceptance_criteria_verified', 'acceptance_criteria_total',
                'blocker', 'usage_latest_total_per_thread', 'report_path')}, indent=2, ensure_ascii=False))
            return 0 if result['passed'] or (result['stage'] == 'PAUSED' and result['integrity']) else 2
        except ValueError as exc:
            print('PELLO PIPELINE ERROR:', exc)
            return 2
    if args.command == 'supervised':
        from .supervised import SupervisedCycle
        try:
            cycle = SupervisedCycle(args.root, timeout=args.timeout)
            if args.spec:
                if args.suite is None:
                    cli.error('--suite is required with --spec')
                project_id = cycle.create_supervised(args.spec, args.suite, model=args.model,
                                                      effort=args.effort, project_id=args.project_id)
            else:
                project_id = args.resume or args.status
            print('PROJECT_ID:', project_id, flush=True)
            result = cycle.supervised_report(project_id) if args.status else cycle.run_supervised(project_id)
            print(json.dumps({key: result[key] for key in (
                'project_id', 'task_id', 'stage', 'evidence_class', 'sdk_turns_reserved',
                'supervisor_decision', 'verification', 'blocker', 'report_path', 'evidence_directory')},
                indent=2, ensure_ascii=False))
            return 0 if result['passed'] else 2
        except ValueError as exc:
            print('SUPERVISED ERROR:', exc)
            return 2
    supervisor = Supervisor(args.root)
    if args.command == 'status':
        print(json.dumps(supervisor.job(args.job_id), indent=2, ensure_ascii=False))
        return 0
    if args.command == 'resume':
        job_id = args.job_id
    elif args.command == 'demo':
        job_id = supervisor.create(project / 'examples/clinica/spec.json',
                                   project / 'examples/clinica/acceptance', 'mock')
    elif args.command == 'start':
        job_id = supervisor.create(args.spec, args.suite, args.mode)
    print('JOB_ID:', job_id, flush=True)
    job = supervisor.run(job_id)
    print('STATUS:', job['state'])
    print('TURNS:', job['turns'], '| FIXES:', job['fixes'], '| LAST_TESTS:', job['last_tests'])
    print('REPORT:', (supervisor.root / 'jobs' / job_id / 'report.md'))
    return 0 if job['state'] == 'LISTO_PARA_REVISION' else 2


if __name__ == '__main__':
    raise SystemExit(main())
