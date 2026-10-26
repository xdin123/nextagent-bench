import { createLocalFileRoll, createLocalFileRollMaintenance, } from '@nextagent/agent-local-file-roll';
const FILE_NAME = 'nextagent-plugin-diagnostic.ndjson';
const MAX_FILE_SIZE_MIB = 30;
const RETENTION_DAYS = 3;
const MAX_ARCHIVE_FILES = 10;
const BUFFER_CAPACITY_BYTES = 8 * 1024 * 1024;
const MAX_RECORD_BYTES = 4 * 1024 * 1024;
const MAX_DROPPED_COUNT = 2_147_483_647;
const SAFE_IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/u;
const MAX_COORDINATE_LENGTH = 512;
export class DeveloperDiagnosticArtifactWriter {
    now;
    logDirectory;
    createHandle;
    createMaintenance;
    maintenanceHandlePromise;
    handlePromise;
    availability;
    droppedCount = 0;
    lastFailureCode;
    isClosed = false;
    closePromise;
    constructor(options, dependencies = {
        createHandle: createLocalFileRoll,
        createMaintenance: createLocalFileRollMaintenance,
    }) {
        this.now = options.now ?? (() => new Date());
        this.createHandle = dependencies.createHandle;
        this.createMaintenance = dependencies.createMaintenance;
        this.availability = 'AVAILABLE';
        this.logDirectory = options.logDirectory;
    }
    start() {
        if (this.isClosed || this.handlePromise !== undefined) {
            return Promise.resolve();
        }
        this.maintenanceHandlePromise ??= Promise.resolve()
            .then(() => this.createMaintenance(developerDiagnosticArtifactFilePolicy(this.logDirectory)))
            .then((handle) => {
            handle.setMaintenanceEventListener((event) => {
                if (event.outcome === 'failed') {
                    this.recordFailure('OUTPUT_UNAVAILABLE', false);
                }
            });
            return handle;
        })
            .catch(() => {
            this.recordFailure('OUTPUT_UNAVAILABLE', false);
            return undefined;
        });
        return this.maintenanceHandlePromise.then(() => undefined);
    }
    async emit(input) {
        if (this.isClosed) {
            return this.drop('OUTPUT_UNAVAILABLE');
        }
        const serialized = serializeRecord(input, this.now);
        if (serialized.status === 'DROPPED') {
            return this.drop(serialized.reasonCode);
        }
        const handle = await this.ensureHandle();
        if (handle === undefined || this.isClosed) {
            return this.drop('OUTPUT_UNAVAILABLE');
        }
        let appendResult;
        try {
            appendResult = handle.appendLine(serialized.line);
        }
        catch {
            return this.drop('OUTPUT_UNAVAILABLE');
        }
        if (appendResult.status === 'dropped') {
            return this.drop(mapAppendFailure(appendResult));
        }
        this.availability = 'AVAILABLE';
        return { status: 'ACCEPTED' };
    }
    status() {
        return {
            availability: this.availability,
            droppedCount: this.droppedCount,
            ...(this.lastFailureCode === undefined ? {} : { lastFailureCode: this.lastFailureCode }),
        };
    }
    async flush(timeoutMs) {
        const handlePromise = this.handlePromise;
        if (handlePromise === undefined) {
            return;
        }
        const handle = await handlePromise;
        await handle?.flush(timeoutMs);
    }
    close(timeoutMs = 5_000) {
        this.isClosed = true;
        this.closePromise ??= this.closeHandle(timeoutMs);
        return this.closePromise;
    }
    ensureHandle() {
        this.handlePromise ??= Promise.resolve()
            .then(async () => {
            await this.stopMaintenanceHandle();
            return this.isClosed ? undefined : this.createHandle(developerDiagnosticArtifactFilePolicy(this.logDirectory));
        })
            .then((handle) => {
            handle?.setMaintenanceEventListener((event) => {
                if (event.outcome === 'failed') {
                    this.recordFailure('OUTPUT_UNAVAILABLE', false);
                }
            });
            return handle;
        })
            .catch(() => {
            this.recordFailure('OUTPUT_UNAVAILABLE', false);
            return undefined;
        });
        return this.handlePromise;
    }
    async closeHandle(timeoutMs) {
        const closeResults = await Promise.allSettled([
            this.stopMaintenanceHandle(timeoutMs),
            this.handlePromise?.then((handle) => handle?.close(timeoutMs)) ?? Promise.resolve(),
        ]);
        if (closeResults.some((result) => result.status === 'rejected')) {
            this.recordFailure('OUTPUT_UNAVAILABLE', false);
            return;
        }
        this.recordFailure('OUTPUT_UNAVAILABLE', false);
    }
    async stopMaintenanceHandle(timeoutMs = 5_000) {
        const maintenanceHandle = await this.maintenanceHandlePromise;
        await maintenanceHandle?.close(timeoutMs);
    }
    drop(reasonCode) {
        this.recordFailure(reasonCode);
        return { status: 'DROPPED', reasonCode };
    }
    recordFailure(reasonCode, incrementDroppedCount = true) {
        this.availability = 'DEGRADED';
        if (incrementDroppedCount) {
            this.droppedCount = Math.min(MAX_DROPPED_COUNT, this.droppedCount + 1);
        }
        this.lastFailureCode = reasonCode;
    }
}
export function createDeveloperDiagnosticArtifactWriter(options) {
    return new DeveloperDiagnosticArtifactWriter(options);
}
export function createDeveloperDiagnosticArtifactWriterForTesting(options, createHandle, createMaintenance = createLocalFileRollMaintenance) {
    return new DeveloperDiagnosticArtifactWriter(options, { createHandle, createMaintenance });
}
export function developerDiagnosticArtifactFilePolicy(logDirectory) {
    return {
        directory: logDirectory,
        fileName: FILE_NAME,
        naming: 'date-sequence',
        maxFileSizeMiB: MAX_FILE_SIZE_MIB,
        retentionDays: RETENTION_DAYS,
        maxArchiveFiles: MAX_ARCHIVE_FILES,
        bufferCapacityBytes: BUFFER_CAPACITY_BYTES,
    };
}
function serializeRecord(input, now) {
    try {
        if (!SAFE_IDENTIFIER.test(input.pluginId) || !SAFE_IDENTIFIER.test(input.artifactType)) {
            return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
        }
        for (const coordinate of [
            input.sessionId,
            input.requestId,
            input.runId,
            input.agentId,
            input.agentVersion,
            input.agentAssemblyRef,
            input.hookInvocationId,
        ]) {
            if (coordinate !== undefined && (typeof coordinate !== 'string' || coordinate.length === 0 || coordinate.length > MAX_COORDINATE_LENGTH)) {
                return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
            }
        }
        if (!isJsonValue(input.payload)) {
            return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
        }
    }
    catch {
        return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
    }
    let line;
    try {
        line = `${JSON.stringify({
            schemaVersion: 1,
            recordedAt: now().toISOString(),
            pluginId: input.pluginId,
            artifactType: input.artifactType,
            ...optionalCoordinates(input),
            payload: input.payload,
        })}\n`;
    }
    catch {
        return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
    }
    return Buffer.byteLength(line, 'utf8') > MAX_RECORD_BYTES ? { status: 'DROPPED', reasonCode: 'RECORD_TOO_LARGE' } : { status: 'ACCEPTED', line };
}
function optionalCoordinates(input) {
    return Object.fromEntries(Object.entries({
        sessionId: input.sessionId,
        requestId: input.requestId,
        runId: input.runId,
        agentId: input.agentId,
        agentVersion: input.agentVersion,
        agentAssemblyRef: input.agentAssemblyRef,
        hookInvocationId: input.hookInvocationId,
    }).filter((entry) => entry[1] !== undefined));
}
function isJsonValue(value, seen = new WeakSet()) {
    if (value === null || typeof value === 'string' || typeof value === 'boolean') {
        return true;
    }
    if (typeof value === 'number') {
        return Number.isFinite(value);
    }
    if (typeof value !== 'object') {
        return false;
    }
    if (seen.has(value)) {
        return false;
    }
    seen.add(value);
    const valid = Array.isArray(value)
        ? value.every((item) => isJsonValue(item, seen))
        : Object.getPrototypeOf(value) === Object.prototype && Object.values(value).every((item) => isJsonValue(item, seen));
    seen.delete(value);
    return valid;
}
function mapAppendFailure(result) {
    return result.reason === 'buffer_full' ? 'QUEUE_OVERLOADED' : 'OUTPUT_UNAVAILABLE';
}
//# sourceMappingURL=developer-diagnostic-artifact-writer.js.map