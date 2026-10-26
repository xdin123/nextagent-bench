from __future__ import annotations

import concurrent.futures
import json
import tempfile
import threading
import unittest
from pathlib import Path

from nextagent_bench.concurrency import read_concurrency, set_concurrency, dispatch_tasks, pending_tasks
from nextagent_bench.util import write_json
from nextagent_bench.model_proxy import Credential, SharedBudget


class RuntimeConcurrencyTests(unittest.TestCase):
    def test_explicit_retry_adds_only_selected_tasks_and_preserves_original_results(self):
        from nextagent_bench.concurrency import request_task_retries
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'run_id': 'test-run', 'tasks': ['passed', 'network', 'other', 'pending']})
            for task, outcome in [('passed', 'PASSED'), ('network', 'EXECUTION_FAILED'), ('other', 'ENVIRONMENT_ERROR')]:
                write_json(root / f'tasks/{task}/attempt-001/result.json', {'status': 'FINISHED', 'outcome': outcome, 'score': 0})
            original = (root / 'tasks/network/attempt-001/result.json').read_bytes()
            manifest = (root / 'manifest.json').read_bytes()
            request_task_retries(root, ['network'], 'User authorized verified network failure retest')
            self.assertEqual(pending_tasks(root, ['passed', 'network', 'other', 'pending'], False), ['network', 'pending'])
            self.assertEqual((root / 'tasks/network/attempt-001/result.json').read_bytes(), original)
            self.assertEqual((root / 'manifest.json').read_bytes(), manifest)

    def test_retry_request_survives_resume_and_stops_after_one_completed_attempt(self):
        from nextagent_bench.concurrency import request_task_retries
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'run_id': 'test-run', 'tasks': ['network']})
            write_json(root / 'tasks/network/attempt-001/result.json', {'status': 'FINISHED', 'outcome': 'EXECUTION_FAILED'})
            request_task_retries(root, ['network'], 'User authorized network retest')
            self.assertEqual(pending_tasks(root, ['network'], False), ['network'])
            write_json(root / 'tasks/network/attempt-002/result.json', {'status': 'FINISHED', 'outcome': 'TASK_FAILED'})
            self.assertEqual(pending_tasks(root, ['network'], False), [])

    def test_interrupted_retry_can_resume_but_finished_environment_error_is_not_repeated(self):
        from nextagent_bench.concurrency import request_task_retries
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'run_id': 'test-run', 'tasks': ['network']})
            write_json(root / 'tasks/network/attempt-001/result.json', {'status': 'FINISHED', 'outcome': 'ENVIRONMENT_ERROR'})
            request_task_retries(root, ['network'], 'User authorized network retest')
            write_json(root / 'tasks/network/attempt-002/result.json', {'status': 'FINISHED', 'outcome': 'INTERRUPTED'})
            self.assertEqual(pending_tasks(root, ['network'], False), ['network'])
            write_json(root / 'tasks/network/attempt-003/result.json', {'status': 'FINISHED', 'outcome': 'ENVIRONMENT_ERROR'})
            self.assertEqual(pending_tasks(root, ['network'], False), [])

    def test_retry_selection_rejects_unknown_task_and_active_runner(self):
        from nextagent_bench.concurrency import request_task_retries
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'run_id': 'test-run', 'tasks': ['known']})
            with self.assertRaises(ValueError):
                request_task_retries(root, ['unknown'], 'network')
            self.assertFalse((root / 'task-retries.json').exists())
            (root / 'runner.lock').write_text('123')
            with self.assertRaises(ValueError):
                request_task_retries(root, ['known'], 'network')

    def test_duplicate_retry_registration_is_idempotent_until_attempt_finishes(self):
        from nextagent_bench.concurrency import request_task_retries
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'run_id': 'test-run', 'tasks': ['network']})
            write_json(root / 'tasks/network/attempt-001/result.json', {'status': 'FINISHED', 'outcome': 'EXECUTION_FAILED'})
            request_task_retries(root, ['network'], 'network recovered')
            original = (root / 'task-retries.json').read_bytes()
            request_task_retries(root, ['network'], 'network recovered')
            self.assertEqual((root / 'task-retries.json').read_bytes(), original)

    def test_operator_control_does_not_modify_frozen_manifest_or_result(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_json(root / 'manifest.json', {'jobs': 1})
            manifest = (root / 'manifest.json').read_bytes()
            set_concurrency(root, 2, 'User requested 2, then observe')
            self.assertEqual(read_concurrency(root, 1), 2)
            self.assertEqual((root / 'manifest.json').read_bytes(), manifest)
            with self.assertRaises(ValueError):
                set_concurrency(root, 0, 'invalid')

    def test_incremental_selection_skips_all_completed_results(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, outcome in [('passed', 'PASSED'), ('failed', 'TASK_FAILED'), ('error', 'ENVIRONMENT_ERROR'), ('interrupted', 'INTERRUPTED')]:
                write_json(root / f'tasks/{name}/attempt-001/result.json', {'status': 'FINISHED', 'outcome': outcome})
            tasks = ['passed', 'failed', 'error', 'interrupted', 'pending']
            self.assertEqual(pending_tasks(root, tasks, False), ['interrupted', 'pending'])
            self.assertEqual(pending_tasks(root, tasks, True), ['error', 'interrupted', 'pending'])

    def test_live_increase_starts_pending_work_without_cancelling_active_work(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            set_concurrency(root, 1, 'initial')
            release = threading.Event()
            first, second = threading.Event(), threading.Event()
            def worker(task, limit):
                (first if task == 'first' else second).set()
                if not release.wait(3):
                    raise TimeoutError('Test did not release workers')
            with concurrent.futures.ThreadPoolExecutor() as outer:
                running = outer.submit(dispatch_tasks, root, ['first', 'second'], 1, worker, lambda n: None)
                try:
                    self.assertTrue(first.wait(1))
                    self.assertFalse(second.is_set())
                    set_concurrency(root, 2, 'raise live')
                    self.assertTrue(second.wait(2))
                finally:
                    release.set()
                running.result(timeout=3)

    def test_budget_live_update_preserves_inflight_requests_and_caps_new_admission(self):
        pool = SharedBudget([Credential('a', 'fixture')], {'max_concurrency': 1, 'min_interval_seconds': 0})
        import time
        first = pool.acquire(1, time.monotonic()+2)
        pool.set_concurrency(2)
        second = pool.acquire(1, time.monotonic()+2)
        pool.set_concurrency(1)
        self.assertEqual(pool.snapshot()['active'], 2)
        pool.release(first, 200)
        pool.release(second, 200)
        self.assertEqual(pool.snapshot()['quota']['max_concurrency'], 1)

    def test_drain_finishes_active_task_without_starting_pending_task(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            started, release = threading.Event(), threading.Event()
            calls = []
            def worker(task, limit):
                calls.append(task)
                started.set()
                if not release.wait(3):
                    raise TimeoutError('Test did not release active task')
            with concurrent.futures.ThreadPoolExecutor() as outer:
                running = outer.submit(dispatch_tasks, root, ['first','pending'], 1, worker, lambda n: None)
                self.assertTrue(started.wait(1))
                (root/'DRAIN').write_text('Drain after current task')
                release.set()
                running.result(timeout=3)
            self.assertEqual(calls,['first'])

    def test_recorded_runtime_upgrade_preserves_result_and_validates_frozen_profile(self):
        import shutil
        from nextagent_bench.runner import create_run, check_resume
        from nextagent_bench.settings import load_settings
        from nextagent_bench.results import resume_identity
        from nextagent_bench.util import adapter_sha, read_json
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            run = create_run(Path(folder), load_settings(project), {'sha256':'a'}, {'sha256':'b'}, ['task'], 1)
            manifest = read_json(run/'manifest.json')
            manifest['adapter_sha'] = 'old-runtime'
            manifest['resume_identity'] = resume_identity(manifest)
            write_json(run/'manifest.json', manifest)
            with self.assertRaisesRegex(ValueError, 'without a recorded'):
                check_resume(run)
            current = adapter_sha()
            source = run/'adapter-upgrades'/current/'source'
            source.mkdir(parents=True)
            for path in (project/'nextagent_bench').rglob('*'):
                if path.is_file() and path.suffix in {'.py','.mjs'}:
                    target = source/path.relative_to(project/'nextagent_bench')
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(path,target)
            write_json(run/'adapter-upgrade.json', {'from_sha':'old-runtime','to_sha':current,'profile_sha':manifest['profile_sha'],
                       'source':str(source.relative_to(run))})
            self.assertEqual(check_resume(run)['runtime_adapter_sha'],current)
            config = read_json(run/'config/agent.yaml')
            config['runtimeSettings']['guardrailEnabled'] = True
            write_json(run/'config/agent.yaml',config)
            with self.assertRaisesRegex(ValueError,'configuration'):
                check_resume(run)


if __name__ == '__main__':
    unittest.main()
