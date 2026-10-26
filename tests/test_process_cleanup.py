from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from nextagent_bench.util import command


class OwnedProcessTimeoutTests(unittest.TestCase):
    def test_timeout_closes_child_and_leaves_unrelated_process_running(self):
        child = ("import socket,time,json,os,sys;from pathlib import Path;"
                 "s=socket.socket();s.bind(('127.0.0.1',0));s.listen();"
                 "Path(sys.argv[1]).write_text(json.dumps({'pid':os.getpid(),'port':s.getsockname()[1]}));"
                 "time.sleep(10)")
        parent = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]]);time.sleep(30)"
        sibling = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(60)"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for use_log in (False, True):
                with self.subTest(log=use_log), tempfile.TemporaryDirectory() as temporary:
                    marker = Path(temporary) / "child.json"
                    started = time.monotonic()
                    try:
                        with self.assertRaises(subprocess.TimeoutExpired):
                            command([sys.executable, "-c", parent, child, str(marker)], timeout=2,
                                    log=Path(temporary) / "command.log" if use_log else None)
                        self.assertLess(time.monotonic() - started, 6)
                        info = json.loads(marker.read_text())
                        with self.assertRaises(OSError):
                            with socket.create_connection(("127.0.0.1", info["port"]), timeout=0.5):
                                pass
                        self.assertIsNone(sibling.poll())
                    finally:
                        if marker.exists():
                            pid = json.loads(marker.read_text())["pid"]
                            if os.name == "nt":
                                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                                               capture_output=True, timeout=10, check=False)
                            else:
                                try:
                                    os.kill(pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
        finally:
            sibling.terminate()
            sibling.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
