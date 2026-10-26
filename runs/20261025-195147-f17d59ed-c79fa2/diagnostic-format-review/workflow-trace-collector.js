const WORKFLOW_NODE_TRACE_ARTIFACT_TYPE = 'workflow-node-trace';
const WORKFLOW_BOUNDARY_TRACE_ARTIFACT_TYPE = 'workflow-boundary-trace';
export class WorkflowTraceCollector {
    sink;
    coordinates;
    pending = new Map();
    constructor(sink, coordinates) {
        this.sink = sink;
        this.coordinates = coordinates;
    }
    async emitEvent(event) {
        try {
            const traceKey = event.nodeExecutionId ?? `${event.executionId}:${event.nodeId}`;
            if (event.eventType === 'NODE_STARTED') {
                const input = extractSafeValue(event.input);
                this.pending.set(traceKey, {
                    startedAt: event.startedAt,
                    nodeId: event.nodeId,
                    nodeType: event.nodeType,
                    executionId: event.executionId,
                    input,
                });
                // Emit a trace record at node start so the viewer can show
                // the node beginning with its input before boundary calls
                // and the terminal record appear.
                await this.sink.emit({
                    artifactType: WORKFLOW_NODE_TRACE_ARTIFACT_TYPE,
                    ...optionalCoordinate('sessionId', this.coordinates.sessionId),
                    ...optionalCoordinate('requestId', this.coordinates.requestId),
                    ...optionalCoordinate('runId', this.coordinates.runId),
                    ...optionalCoordinate('agentId', this.coordinates.agentId),
                    ...optionalCoordinate('agentVersion', this.coordinates.agentVersion),
                    payload: {
                        executionId: event.executionId,
                        nodeId: event.nodeId,
                        nodeType: event.nodeType,
                        nodeExecutionId: event.nodeExecutionId,
                        durationMs: 0,
                        status: 'NODE_STARTED',
                        input,
                    },
                });
                return;
            }
            if (event.eventType === 'NODE_COMPLETED' ||
                event.eventType === 'NODE_FAILED' ||
                event.eventType === 'NODE_SKIPPED' ||
                event.eventType === 'NODE_WAITING') {
                const pending = this.pending.get(traceKey);
                if (pending === undefined) {
                    return;
                }
                this.pending.delete(traceKey);
                const completedAt = event.completedAt ?? event.startedAt;
                const durationMs = Math.max(0, completedAt.getTime() - pending.startedAt.getTime());
                const output = extractSafeValue(event.output);
                await this.sink.emit({
                    artifactType: WORKFLOW_NODE_TRACE_ARTIFACT_TYPE,
                    ...optionalCoordinate('sessionId', this.coordinates.sessionId),
                    ...optionalCoordinate('requestId', this.coordinates.requestId),
                    ...optionalCoordinate('runId', this.coordinates.runId),
                    ...optionalCoordinate('agentId', this.coordinates.agentId),
                    ...optionalCoordinate('agentVersion', this.coordinates.agentVersion),
                    payload: {
                        executionId: pending.executionId,
                        nodeId: pending.nodeId,
                        nodeType: pending.nodeType,
                        nodeExecutionId: event.nodeExecutionId,
                        durationMs,
                        status: event.eventType,
                        input: pending.input,
                        output,
                        ...(event.safeError === undefined ? {} : { safeError: event.safeError }),
                    },
                });
            }
        }
        catch {
            // Observe-only: must not affect workflow execution.
        }
    }
}
export function createTimingWrappedService(original, sink, coordinates, boundaryType, methodNames) {
    const wrapped = Object.create(original);
    for (const methodName of methodNames) {
        const fn = original[methodName];
        if (typeof fn !== 'function') {
            continue;
        }
        wrapped[methodName] = function (...args) {
            return trackBoundaryCall(() => fn.apply(original, args), sink, coordinates, boundaryType);
        };
    }
    return Object.freeze(wrapped);
}
async function trackBoundaryCall(operation, sink, coordinates, boundaryType) {
    const startedAt = Date.now();
    try {
        const result = await operation();
        await emitBoundaryTrace(sink, coordinates, boundaryType, startedAt, 'SUCCEEDED');
        return result;
    }
    catch (error) {
        await emitBoundaryTrace(sink, coordinates, boundaryType, startedAt, 'FAILED');
        throw error;
    }
}
async function emitBoundaryTrace(sink, coordinates, boundaryType, startedAt, status) {
    try {
        const durationMs = Math.max(0, Date.now() - startedAt);
        await sink.emit({
            artifactType: WORKFLOW_BOUNDARY_TRACE_ARTIFACT_TYPE,
            ...optionalCoordinate('sessionId', coordinates.sessionId),
            ...optionalCoordinate('requestId', coordinates.requestId),
            ...optionalCoordinate('runId', coordinates.runId),
            ...optionalCoordinate('agentId', coordinates.agentId),
            ...optionalCoordinate('agentVersion', coordinates.agentVersion),
            payload: {
                recordedAt: new Date(startedAt).toISOString(),
                boundaryType,
                durationMs,
                status,
            },
        });
    }
    catch {
        // Observe-only: must not affect workflow execution.
    }
}
function extractSafeValue(value) {
    if (value === undefined)
        return undefined;
    if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
        return value;
    }
    return { value: value };
}
function optionalCoordinate(key, value) {
    return value === undefined ? {} : { [key]: value };
}
export function createWorkflowTraceCoordinates() {
    return {};
}
//# sourceMappingURL=workflow-trace-collector.js.map