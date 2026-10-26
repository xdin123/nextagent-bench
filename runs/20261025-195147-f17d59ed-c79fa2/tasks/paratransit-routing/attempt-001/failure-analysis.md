# paratransit-routing / attempt 1

Outcome: ENVIRONMENT_ERROR
End-to-end score: None; verifier reward: None
Model: qwen3.8-27b; framework: f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5

## Evidence

- result.json: phase, terminal, budgets, timings and collection status.
- agent-facing/adaptation.json and adaptation.patch: exact path changes; verifier unchanged.
- skill-catalog.json + skill-discovery.json: discoverability; trajectory.jsonl: actual Skill invocation and loading.
- nextagent-home.tar: complete POSIX execution workspace, persistent state and framework logs; nextagent-home/logs/: readable log copy.
- ctrf.json, reward.txt and verifier-stdout.txt: original scoring evidence.

## Finding

docker exited 1: rror(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))) - skipping
#6 38.82 ERROR: Could not find a version that satisfies the requirement ortools==9.11.4210 (from versions: none)
#6 43.85 ERROR: No matching distribution found for ortools==9.11.4210
#6 ERROR: process "/bin/sh -c pip install --no-cache-dir     ortools==9.11.4210     pandas==2.2.3     numpy==1.26.4     pytest==8.3.4     pytest-json-ctrf==0.3.5" did not complete successfully: exit code: 1
------
 > [2/7] RUN pip install --no-cache-dir     ortools==9.11.4210     pandas==2.2.3     numpy==1.26.4     pytest==8.3.4     pytest-json-ctrf==0.3.5:
6.212 WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))': /simple/ortools/
11.73 WARNING: Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))': /simple/ortools/
17.75 WARNING: Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))': /simple/ortools/
24.78 WARNING: Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))': /simple/ortools/
33.79 WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))': /simple/ortools/
38.82 Could not fetch URL https://pypi.org/simple/ortools/: There was a problem confirming the ssl certificate: HTTPSConnectionPool(host='pypi.org', port=443): Max retries exceeded with url: /simple/ortools/ (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))) - skipping
38.82 ERROR: Could not find a version that satisfies the requirement ortools==9.11.4210 (from versions: none)
43.85 ERROR: No matching distribution found for ortools==9.11.4210
------
Dockerfile:5
--------------------
   4 |     
   5 | >>> RUN pip install --no-cache-dir \
   6 | >>>     ortools==9.11.4210 \
   7 | >>>     pandas==2.2.3 \
   8 | >>>     numpy==1.26.4 \
   9 | >>>     pytest==8.3.4 \
  10 | >>>     pytest-json-ctrf==0.3.5
  11 |     
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c pip install --no-cache-dir     ortools==9.11.4210     pandas==2.2.3     numpy==1.26.4     pytest==8.3.4     pytest-json-ctrf==0.3.5" did not complete successfully: exit code: 1

Root cause is not established by this automatic summary. Distinguish task assertions, framework execution, model/provider evidence and harness/environment errors before assigning responsibility.
