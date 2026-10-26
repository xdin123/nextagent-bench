from __future__ import annotations

import concurrent.futures
import json
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nextagent_bench.model_proxy import Credential, SharedBudget, make_handler


QUOTA = {"max_concurrency": 1, "min_interval_seconds": 0, "max_wait_seconds": 3, "max_attempts": 3,
         "requests_per_minute": None, "tokens_per_minute": None, "upstream_idle_timeout_seconds": 2}


class SharedQuotaTests(unittest.TestCase):
    def test_two_keys_share_one_slot_and_one_cooldown(self):
        pool = SharedBudget([Credential("a", "secret-a"), Credential("b", "secret-b")], QUOTA)
        first = pool.acquire(1, time.monotonic() + 3)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            second = executor.submit(pool.acquire, 1, time.monotonic() + 3)
            time.sleep(0.03)
            self.assertFalse(second.done())
            pool.release(first, 429, cooldown=0.08)
            self.assertGreater(pool.snapshot()["cooldown_remaining_seconds"], 0)
            key = second.result(timeout=2)
        self.assertEqual(pool.snapshot()["active"], 1)
        self.assertEqual(key.name, "b")
        pool.release(key, 200)
        self.assertNotIn("secret-", json.dumps(pool.snapshot()))
        self.assertNotIn("secret-a", repr(first))


class ProxyContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.calls, self.events = [], []
        self.event_received = threading.Event()
        outer = self
        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass
            def do_POST(self):
                body = self.rfile.read(int(self.headers['Content-Length']))
                outer.calls.append({"body": body, "authorization": self.headers['Authorization'], "path": self.path})
                number = len(outer.calls)
                if outer.mode == 'rate' and number == 1:
                    self.send_response(429)
                    self.send_header('Retry-After', '0.02')
                    self.end_headers()
                    self.wfile.write(b'{"error":{"code":"rate_limit"}}')
                elif outer.mode == 'auth' and number == 1:
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b'{"error":{"message":"secret-a"}}')
                elif outer.mode == 'broken':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Transfer-Encoding', 'chunked')
                    self.end_headers()
                    data = b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n'
                    self.wfile.write(f'{len(data):x}\r\n'.encode() + data + b'\r\n')
                    self.wfile.flush()
                    self.connection.shutdown(socket.SHUT_WR)
                elif outer.mode == 'reset-before-response':
                    self.close_connection = True
                    self.connection.shutdown(socket.SHUT_RDWR)
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.end_headers()
                    self.wfile.write(outer.stream)
        self.mode = 'normal'
        self.stream = b'data: {"choices":[{"delta":{"content":"ok","reasoning_content":"hidden reasoning"}}]}\n\ndata: [DONE]\n\n'
        self.upstream = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        self.pool = SharedBudget([Credential('a', 'secret-a'), Credential('b', 'secret-b')], dict(QUOTA))
        def record_event(value):
            self.events.append(value)
            self.event_received.set()
        self.proxy = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(self.pool, 'http://127.0.0.1:' + str(self.upstream.server_port) + '/v1',
                     'local-token', emit=record_event, evidence_root=Path(self.temporary.name), control_token='operator-token'))
        for server in [self.upstream, self.proxy]:
            threading.Thread(target=server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.proxy.shutdown()
        self.upstream.shutdown()
        self.proxy.server_close()
        self.upstream.server_close()
        self.temporary.cleanup()

    def request(self):
        body = b'{"model":"fixture","messages":[{"role":"system","content":"schema guidance"}],"stream":true}'
        request = urllib.request.Request('http://127.0.0.1:' + str(self.proxy.server_port) + '/tasks/fixture/attempts/1/v1/chat/completions',
            data=body, headers={'Authorization':'Bearer local-token','Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=5) as response:
            return body, response.read()

    def test_429_cools_shared_pool_and_preserves_stream_bytes_and_request(self):
        self.mode = 'rate'
        body, response = self.request()
        self.assertEqual(response, self.stream)
        self.assertEqual([call['authorization'] for call in self.calls], ['Bearer secret-a', 'Bearer secret-b'])
        self.assertTrue(all(call['body'] == body and call['path'] == '/v1/chat/completions' for call in self.calls))
        self.assertEqual(self.pool.statuses[429], 1)
        self.assertNotIn('secret-', '\n'.join(self.events))

    def test_invalid_key_is_quarantined_without_exposing_it(self):
        self.mode = 'auth'
        self.request()
        self.assertTrue(self.pool.credentials[0].disabled)
        self.assertEqual(len(self.calls), 2)
        self.assertNotIn('secret-a', '\n'.join(self.events))

    def test_started_stream_is_never_retried(self):
        self.mode = 'broken'
        _, response = self.request()
        self.assertIn(b'partial', response)
        self.assertEqual(len(self.calls), 1)

    def test_upstream_reset_before_response_returns_502_without_waiting_for_client_timeout(self):
        self.mode = 'reset-before-response'
        with self.assertRaises(urllib.error.HTTPError) as raised:
            self.request()
        self.assertEqual(raised.exception.code, 502)
        self.assertEqual(json.loads(raised.exception.read())['error']['code'], 'EVAL_UPSTREAM_CONNECTION_RESET')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(self.event_received.wait(timeout=1), 'Gateway must emit the terminal transport event')
        self.assertEqual(json.loads(self.events[-1])['error_kind'], 'UPSTREAM_CONNECTION_RESET')
        self.assertEqual(self.pool.snapshot()['active'], 0)

    def test_evidence_has_actual_messages_and_omits_reasoning_and_auth(self):
        self.request()
        request_file = next(Path(self.temporary.name).rglob('request.json'))
        self.assertEqual(json.loads(request_file.read_text())['messages'][0]['content'], 'schema guidance')
        response_file = next(Path(self.temporary.name).rglob('response-01.jsonl'))
        content = response_file.read_text()
        self.assertNotIn('hidden reasoning', content)
        self.assertNotIn('reasoning_content', content)
        self.assertNotIn('secret-a', ''.join(p.read_text() for p in Path(self.temporary.name).rglob('*.json')))

    def test_agent_token_cannot_change_shared_concurrency(self):
        request = urllib.request.Request('http://127.0.0.1:' + str(self.proxy.server_port) + '/control/concurrency',
            data=b'{"jobs":4}', headers={'Authorization':'Bearer local-token','Content-Type':'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request, timeout=2)
        self.assertEqual(raised.exception.code, 401)
        self.assertEqual(self.pool.snapshot()['quota']['max_concurrency'], 1)

    def test_operator_can_adjust_limit_without_recreating_pool_or_losing_counters(self):
        self.request()
        request = urllib.request.Request('http://127.0.0.1:' + str(self.proxy.server_port) + '/control/concurrency',
            data=b'{"jobs":2}', headers={'Authorization':'Bearer operator-token','Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=2) as response:
            metrics = json.loads(response.read())
        self.assertEqual(metrics['quota']['max_concurrency'], 2)
        self.assertEqual(sum(item['requests'] for item in metrics['credentials']), 1)


if __name__ == '__main__':
    unittest.main()
