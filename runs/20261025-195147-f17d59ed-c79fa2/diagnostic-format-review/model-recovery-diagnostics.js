/* eslint @typescript-eslint/no-use-before-define: ['error', { functions: false }] */
import { AsyncLocalStorage } from 'node:async_hooks';
import { randomUUID } from 'node:crypto';
import { getLogger } from './logger.js';
import { boundedModelDiagnosticSnapshot } from './model-diagnostic-snapshot.js';
const context = new AsyncLocalStorage();
const logger = getLogger({ component: 'agent-model', source: 'recovery-diagnostics' });
let sink;
let pending = 0;
let dropped = 0;
const pendingWrites = new Set();
const coordinateKeys = ['sessionId', 'requestId', 'runId', 'agentId', 'agentVersion', 'agentAssemblyRef'];
const numberKeys = new Set([
    'attemptNo',
    'nextAttemptNo',
    'maxAttempts',
    'attempts',
    'retryCount',
    'waitMs',
    'remainingMs',
    'durationMs',
    'budgetMs',
    'oldMaxOutputTokens',
    'maxOutputTokens',
    'continuationNo',
    'inputBytesBefore',
    'inputBytesAfter',
    'contentLength',
    'reasoningLength',
    'retainedContentLength',
    'httpStatus',
]);
const tokenKeys = new Set([
    'action',
    'status',
    'outcome',
    'kind',
    'providerCode',
    'frameworkCode',
    'reasonCode',
    'providerKind',
    'finishReason',
    'origin',
    'terminal',
    'purpose',
    'format',
    'language',
    'mode',
    'channel',
    'stepId',
    'invocationId',
    'parentInvocationId',
    'modelId',
    'phase',
    'sdkErrorType',
    'operation',
    'location',
]);
const booleanKeys = new Set(['delivered', 'safeToReplay', 'remoteTerminated', 'repaired', 'recoveryHandled']);
/** Independent of plugin hooks; binding lifetime belongs to the existing host diagnostic writer. */
export function bindModelDiagnosticSink(next) {
    const previous = sink;
    sink = next;
    return () => {
        if (sink === next)
            sink = previous;
    };
}
export async function flushModelDiagnostics() {
    let timer;
    try {
        await Promise.race([
            Promise.all([...pendingWrites]),
            new Promise((resolve) => {
                timer = setTimeout(resolve, 2500);
            }),
        ]);
    }
    finally {
        clearTimeout(timer);
    }
}
export function withModelDiagnosticScope(request, providerKind, operation) {
    const previous = context.getStore();
    const input = record(request);
    const stepId = record(input.invocationScope).operationId ?? previous?.stepId;
    const modelId = input.modelId ?? previous?.modelId;
    return context.run({
        coordinates: { ...previous?.coordinates, ...coordinates(request) },
        invocationId: randomUUID(),
        ...(typeof stepId === 'string' ? { stepId } : {}),
        ...(typeof modelId === 'string' ? { modelId } : {}),
        ...(previous === undefined ? {} : { parentInvocationId: previous.invocationId }),
        ...(providerKind === undefined ? {} : { providerKind }),
    }, operation);
}
export function withModelDiagnosticAttempt(attemptNo, operation) {
    const current = context.getStore();
    return current === undefined ? operation() : context.run({ ...current, attemptNo }, operation);
}
/** Shared allowlist used again at the operational writer; no bodies or arbitrary exception strings. */
export function projectModelRecoveryFields(value) {
    const output = {};
    for (const [key, field] of Object.entries(record(value))) {
        if (allowedField(key, field))
            output[key] = field;
    }
    return output;
}
/** Logging is observational: never await I/O on the model path and never change its result. */
export function emitModelDiagnostic(request, event, fields, snapshots) {
    try {
        const current = context.getStore();
        const input = record(request);
        const scope = record(input.invocationScope);
        const ids = { ...current?.coordinates, ...coordinates(request) };
        const details = projectModelRecoveryFields({
            ...current,
            ...fields,
            ...projectModelRecoveryFields({ stepId: scope.operationId, modelId: input.modelId }),
        });
        logger.info({ event, ...ids, modelRecovery: details });
        if (sink === undefined)
            return;
        if (pending >= 16) {
            noteDrop();
            return;
        }
        const payload = {
            version: 1,
            event,
            stage: 'MODEL_RECOVERY',
            ...details,
            ...(snapshots === undefined ? {} : { snapshots: boundedModelDiagnosticSnapshot(snapshots) }),
        };
        sendDiagnostic(sink, { pluginId: 'framework-model-recovery', artifactType: 'model-recovery', ...ids, payload });
    }
    catch {
        noteDrop();
    }
}
/** A local operation's result and thrown failure are logged without swallowing exceptions. */
export async function observeModelAction(request, fields, operation) {
    const started = performance.now();
    emitModelDiagnostic(request, 'model.recovery.action', { ...fields, status: 'STARTED' });
    try {
        const result = await operation();
        emitModelDiagnostic(request, 'model.recovery.action', {
            ...fields,
            status: record(result).safeError === undefined ? 'SUCCEEDED' : 'FAILED',
            durationMs: performance.now() - started,
        });
        return result;
    }
    catch (error) {
        const details = record(record(error).safeDetails);
        emitModelDiagnostic(request, 'model.recovery.action', {
            ...fields,
            status: 'FAILED',
            durationMs: performance.now() - started,
            frameworkCode: typeof record(error).code === 'string' ? String(record(error).code) : 'UNCLASSIFIED',
            operation: typeof details.operation === 'string' ? details.operation : undefined,
            location: typeof details.location === 'string' ? details.location : undefined,
        });
        throw error;
    }
}
export function modelRequestSnapshot(request) {
    const input = record(request);
    return select(input, [
        'messages',
        'tools',
        'toolChoice',
        'maxOutputTokens',
        'temperature',
        'topP',
        'topK',
        'thinking',
        'responseHandling',
        'timeoutMs',
        'maxRetries',
    ]);
}
export function modelResultSnapshot(result) {
    return select(record(result), [
        'content',
        'reasoning',
        'toolCalls',
        'finishReason',
        'usage',
        'safeError',
        'failureFacts',
        'responseEvidence',
        'recovery',
    ]);
}
function record(value) {
    return value !== null && typeof value === 'object' ? value : {};
}
function coordinates(request) {
    const source = record(record(request).invocationScope ?? request);
    const output = {};
    for (const key of coordinateKeys) {
        const value = source[key];
        if (typeof value === 'string' && /^[A-Za-z0-9_.:@/-]{1,256}$/u.test(value))
            output[key] = value;
    }
    return output;
}
function allowedField(key, field) {
    if (typeof field === 'number')
        return numberKeys.has(key) && Number.isFinite(field) && field >= 0;
    if (typeof field === 'string')
        return tokenKeys.has(key) && /^[A-Za-z0-9_.:-]{1,128}$/u.test(field);
    return typeof field === 'boolean' && booleanKeys.has(key);
}
function noteDrop() {
    dropped += 1;
    if (dropped === 1 || dropped % 100 === 0)
        logger.warn({ event: 'model.diagnostic.dropped', droppedCount: dropped });
}
function sendDiagnostic(target, input) {
    pending += 1;
    const task = Promise.resolve()
        .then(() => target(input))
        .then((result) => {
        if (result.status !== 'ACCEPTED')
            noteDrop();
    }, () => noteDrop())
        .finally(() => {
        pending -= 1;
        pendingWrites.delete(task);
    });
    pendingWrites.add(task);
}
function select(input, keys) {
    return Object.fromEntries(keys.filter((key) => input[key] !== undefined).map((key) => [key, input[key]]));
}
//# sourceMappingURL=model-recovery-diagnostics.js.map