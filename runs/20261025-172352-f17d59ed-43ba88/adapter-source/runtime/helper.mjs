import * as fs from 'node:fs/promises';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';

const HOME = '/opt/na-eval/home';
const RUN = '/opt/na-eval/run';
const action = process.argv[2];
let raw = '';
for await (const chunk of process.stdin) raw += chunk;
const input = JSON.parse(raw || '{}');

async function exists(name) {
  try { await fs.lstat(name); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; }
}

function safeRoot(root) {
  if (!root.startsWith('/') || root.includes('/../') || root.endsWith('/..') ||
      ['/', '/usr', '/etc', '/bin', '/sbin', '/dev', '/proc', '/sys', '/opt', '/home', '/var'].includes(root) ||
      ['/usr/', '/etc/', '/bin/', '/sbin/', '/dev/', '/proc/', '/sys/'].some(prefix => root.startsWith(prefix)) ||
      root.startsWith('/opt/nextagent') || root.startsWith('/opt/na-eval')) {
    throw new Error(`Unsafe task root: ${root}`);
  }
}

async function relocate(source, target) {
  safeRoot(source);
  await fs.mkdir(path.dirname(target), { recursive: true });
  if (await exists(source)) {
    const real = await fs.realpath(source);
    if (real === target) return;
    if (target.startsWith(real + '/') || real.startsWith(target + '/')) throw new Error('Overlapping roots');
    const entries = await fs.readdir(source);
    await fs.mkdir(target, { recursive: true });
    for (const name of entries) {
      const from = path.join(source, name), to = path.join(target, name);
      if (await exists(to)) throw new Error(`Path collision: ${to}`);
      try { await fs.rename(from, to); }
      catch (e) {
        if (e.code !== 'EXDEV') throw e;
        await fs.cp(from, to, { recursive: true, dereference: false });
        await fs.rm(from, { recursive: true, force: true });
      }
    }
    await fs.rm(source, { recursive: true, force: true });
  } else {
    await fs.mkdir(target, { recursive: true });
  }
  await fs.symlink(target, source);
  if (await fs.realpath(source) !== await fs.realpath(target)) throw new Error(`Bridge failed: ${source}`);
}

async function run() {
  if (action === 'prepare') {
    await fs.mkdir(RUN, { recursive: true });
    await fs.mkdir(HOME + '/skills', { recursive: true });
    await fs.mkdir(HOME + '/agents/' + input.agentId, { recursive: true });
    await fs.mkdir(RUN + '/config', { recursive: true });
    await fs.mkdir('/opt/nextagent', { recursive: true });
    // Import-only ESM package exports resolve from the deployment directory.
    await fs.copyFile('/opt/na-eval/runtime/start.mjs', '/opt/nextagent/.bench-start.mjs');
    return { home: HOME };
  }
  if (action === 'status') {
    if (!(await exists(RUN + '/app.pid'))) return { running: false };
    const pid = Number(await fs.readFile(RUN + '/app.pid', 'utf8'));
    try {
      const stat = await fs.readFile('/proc/' + pid + '/stat', 'utf8');
      return { running: stat.slice(stat.lastIndexOf(')') + 2).split(' ')[0] !== 'Z' };
    } catch (e) { if (e.code === 'ENOENT') return { running: false }; throw e; }
  }
  if (action === 'skill-discovery') {
    const registered = new Set(), diagnostics = [];
    const directory = HOME + '/logs';
    for (const file of await fs.readdir(directory)) {
      if (!/\.(jsonl|ndjson)(\.gz)?$/.test(file)) continue;
      const bytes = await fs.readFile(path.join(directory, file));
      const content = (file.endsWith('.gz') ? gunzipSync(bytes) : bytes).toString('utf8');
      for (const line of content.split('\n')) {
        let entry;
        try { entry = JSON.parse(line); } catch { continue; }
        if (entry.providerId !== 'local-skills-system' || !String(entry.event).startsWith('skill.discovery.')) continue;
        if (entry.event === 'skill.discovery.registered') registered.add(entry.skillId);
        diagnostics.push({ event: entry.event, skillId: entry.skillId, reason: entry.reason, diagnosticReasonCodes: entry.diagnosticReasonCodes });
      }
    }
    return { registered: [...registered].sort(), diagnostics, source: 'system-local structured startup discovery diagnostics' };
  }
  if (action === 'rpc') {
    const response = await fetch('http://127.0.0.1:31872' + input.path, {
      method: input.method, headers: { 'Content-Type': 'application/json' },
      body: input.body === undefined || input.body === null ? undefined : JSON.stringify(input.body),
      signal: AbortSignal.timeout(20000),
    });
    const text = await response.text();
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${text.slice(0, 600)}`);
    return text ? JSON.parse(text) : {};
  }
  if (action === 'bridge') {
    const execution = HOME + '/workspaces/execution';
    const candidates = [];
    for (const entry of await fs.readdir(execution, { withFileTypes: true })) {
      const workspace = path.join(execution, entry.name, 'workspace');
      if (entry.isDirectory() && await exists(workspace)) candidates.push(workspace);
    }
    if (candidates.length !== 1) throw new Error(`Expected one fresh execution workspace, found ${candidates.length}`);
    const workspace = candidates[0], scope = path.dirname(workspace);
    // Relocate the main root before its children; overlapping extra roots are
    // rejected by the host planner. The application lives outside these roots.
    const mappings = input.mappings.filter(x => x.relocate);
    for (const mapping of mappings) {
      const target = mapping.logical === 'temp' ? path.join(scope, 'temp') :
        path.join(workspace, mapping.logical.slice('workspace'.length));
      await relocate(mapping.physical, target);
    }
    const skills = RUN + '/agent-facing/skills';
    if (await exists(skills)) {
      await fs.cp(skills, workspace + '/skills', { recursive: true, force: true });
    }
    return { workspace, scope, mappings: await Promise.all(mappings.map(async m => ({ ...m, resolved: await fs.realpath(m.physical) }))) };
  }
  if (action === 'stop') {
    if (input.kind && !['app', 'verifier'].includes(input.kind)) throw new Error('Invalid managed process kind');
    const pidFile = RUN + '/' + (input.kind || 'app') + '.pid';
    if (!(await exists(pidFile))) return { stopped: true, alreadyStopped: true };
    const pid = Number(await fs.readFile(pidFile, 'utf8'));
    if (!Number.isInteger(pid) || pid <= 1) throw new Error('Invalid application pid');
    const parents = new Map();
    for (const entry of await fs.readdir('/proc')) {
      if (!/^\d+$/.test(entry)) continue;
      try {
        const stat = await fs.readFile('/proc/' + entry + '/stat', 'utf8');
        const parent = Number(stat.slice(stat.lastIndexOf(')') + 2).split(' ')[1]);
        parents.set(Number(entry), parent);
      } catch (e) { if (!['ENOENT', 'ESRCH'].includes(e.code)) throw e; }
    }
    const descendants = new Set([pid]);
    for (let previous = 0; previous !== descendants.size;) {
      previous = descendants.size;
      for (const [child, parent] of parents) if (descendants.has(parent)) descendants.add(child);
    }
    const finish = async forced => {
      for (const child of descendants) {
        if (child === process.pid) continue;
        try { process.kill(child, 'SIGKILL'); } catch (e) { if (e.code !== 'ESRCH') throw e; }
      }
      await fs.rm(pidFile, { force: true });
      return { stopped: true, forced };
    };
    try { process.kill(pid, 'SIGTERM'); } catch (e) { if (e.code !== 'ESRCH') throw e; }
    for (let attempt = 0; attempt < 100; attempt++) {
      try { process.kill(pid, 0); } catch (e) { if (e.code === 'ESRCH') return finish(false); throw e; }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    return finish(true);
  }
  if (action === 'read') {
    const result = {};
    for (const name of input.paths || []) {
      result[name] = await exists(name) ? await fs.readFile(name, 'utf8') : null;
    }
    return result;
  }
  throw new Error(`Unknown action: ${action}`);
}

try { console.log(JSON.stringify(await run())); }
catch (error) { console.error(error.stack || String(error)); process.exitCode = 1; }
