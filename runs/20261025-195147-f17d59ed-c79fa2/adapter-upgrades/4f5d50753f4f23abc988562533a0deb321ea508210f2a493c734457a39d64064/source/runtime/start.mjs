import { createNextAgentAppAsync } from '@nextagent/agent-app';
import { writeFileSync } from 'node:fs';

writeFileSync('/opt/na-eval/run/app.pid', String(process.pid));
const app = await createNextAgentAppAsync({
  deploymentRoot: new URL('file:///opt/nextagent/'),
  configFile: '/opt/nextagent/config/evaluation-system.yaml',
  commandLine: [],
});
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.once(signal, () => app.close().then(() => process.exit(0)).catch(() => process.exit(1)));
}
await app.start();
console.log(JSON.stringify({ event: 'nextagent.bench.started', pid: process.pid }));
