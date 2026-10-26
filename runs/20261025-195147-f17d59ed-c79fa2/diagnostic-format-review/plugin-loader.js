import { readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { Type } from '@sinclair/typebox';
import { Ajv } from 'ajv';
import { isPathInside } from '@nextagent/agent-common';
/* eslint @typescript-eslint/no-use-before-define: ["error", { "functions": false, "variables": true, "classes": true, "typedefs": true }] -- Migrated loader uses hoisted function declarations; variables and classes remain checked. */
import { HOST_EXTERNAL_INVENTORY, noopDeveloperDiagnosticArtifactSink, OPEN_POLICY_INVENTORY, pluginToolProviderType, ROOT_PLUGIN_API_VERSION, SUPPORTED_PLUGIN_API_VERSIONS, } from '@nextagent/agent-plugin-sdk';
const manifestSchema = {
    type: 'object',
    additionalProperties: false,
    required: ['pluginId', 'version', 'main', 'artifactType'],
    properties: {
        pluginId: { type: 'string', minLength: 1, maxLength: 128, pattern: '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$' },
        version: { type: 'string', minLength: 1, maxLength: 128 },
        apiVersion: { type: 'string', minLength: 3, maxLength: 16, pattern: '^\\d+\\.\\d+$' },
        main: { type: 'string', minLength: 1, maxLength: 256 },
        artifactType: { const: 'esm-bundle' },
        hostExternals: {
            type: 'array',
            maxItems: 2,
            items: {
                type: 'object',
                additionalProperties: false,
                required: ['id', 'versionRange'],
                properties: {
                    id: { enum: HOST_EXTERNAL_INVENTORY.map((entry) => entry.id) },
                    versionRange: { type: 'string', minLength: 1, maxLength: 64 },
                },
            },
        },
    },
}, ajv = new Ajv({ allErrors: true }), validateManifest = ajv.compile(manifestSchema), hostExternalsById = new Map(HOST_EXTERNAL_INVENTORY.map((entry) => [entry.id, entry])), openPolicyIds = new Set(OPEN_POLICY_INVENTORY.filter((entry) => entry.status === 'OPEN').map((entry) => entry.policyPointId)), reservedPolicyIds = new Set(OPEN_POLICY_INVENTORY.filter((entry) => entry.status === 'RESERVED').map((entry) => entry.policyPointId));
class PluginLoadError extends Error {
    safeReasonCode;
    safeSummary;
    constructor(safeReasonCode, safeSummary) {
        super(safeSummary);
        this.safeReasonCode = safeReasonCode;
        this.safeSummary = safeSummary;
        this.name = 'PluginLoadError';
    }
}
export function emptyPluginRegistrySnapshot() {
    return Object.freeze({ plugins: [], providers: [], policies: [], hooks: [], diagnostics: [] });
}
export async function loadPluginRegistrySnapshot(entries, configRoot, hostServices) {
    if (entries.length === 0) {
        return emptyPluginRegistrySnapshot();
    }
    if (entries.length > 8) {
        throw new Error('Plugin config declares more than 8 plugins.');
    }
    const diagnostics = [], plugins = [], providers = [], policies = [], hooks = [], pluginIds = new Set(), providerIds = new Set(), policyKeys = new Set(), hookIds = new Set();
    for (const entry of entries) {
        try {
            if (pluginIds.has(entry.pluginId)) {
                throw new Error('Duplicate plugin id.');
            }
            pluginIds.add(entry.pluginId);
            appendLoadedPlugin(await loadOnePluginAsync(entry, configRoot, providerIds, policyKeys, hookIds, hostServices), plugins, providers, policies, hooks);
        }
        catch (error) {
            diagnostics.push(safeDiagnostic('ERROR', 'PLUGIN_LOAD_REJECTED', entry.pluginId, error));
            if (entry.required) {
                throw new Error('Required plugin failed startup validation.');
            }
        }
    }
    return deepFreeze({ plugins, providers, policies, hooks, diagnostics });
}
export function loadPluginRegistrySnapshotSync(entries, configRoot, hostServices) {
    if (entries.length === 0) {
        return emptyPluginRegistrySnapshot();
    }
    if (entries.length > 8) {
        throw new Error('Plugin config declares more than 8 plugins.');
    }
    const diagnostics = [], plugins = [], providers = [], policies = [], hooks = [], pluginIds = new Set(), providerIds = new Set(), policyKeys = new Set(), hookIds = new Set();
    for (const entry of entries) {
        try {
            if (pluginIds.has(entry.pluginId)) {
                throw new Error('Duplicate plugin id.');
            }
            pluginIds.add(entry.pluginId);
            appendLoadedPlugin(loadOnePlugin(entry, configRoot, providerIds, policyKeys, hookIds, hostServices), plugins, providers, policies, hooks);
        }
        catch (error) {
            diagnostics.push(safeDiagnostic('ERROR', 'PLUGIN_LOAD_REJECTED', entry.pluginId, error));
            if (entry.required) {
                throw new Error('Required plugin failed startup validation.');
            }
        }
    }
    return deepFreeze({ plugins, providers, policies, hooks, diagnostics });
}
function appendLoadedPlugin(loaded, plugins, providers, policies, hooks) {
    plugins.push({ pluginId: loaded.plugin.pluginId, version: loaded.plugin.version });
    providers.push(...(loaded.plugin.providers ?? []));
    policies.push(...(loaded.plugin.policies ?? []).map((policy) => ({ pluginId: loaded.plugin.pluginId, policy })));
    hooks.push(...(loaded.plugin.hooks ?? []));
}
function loadPluginBundle(entry, configRoot) {
    const pluginDir = resolve(configRoot, entry.path);
    if (!isPathInside(resolve(configRoot), pluginDir) || !isDirectory(pluginDir)) {
        throw new PluginLoadError('PLUGIN_DIRECTORY_INVALID', 'Plugin directory is outside config root or missing.');
    }
    // eslint-disable-next-line one-var -- The manifest is read only after the trusted plugin directory check.
    const manifest = readManifest(resolve(pluginDir, 'plugin.json'));
    if (manifest.pluginId !== entry.pluginId) {
        throw new PluginLoadError('PLUGIN_ID_MISMATCH', 'Plugin id mismatch.');
    }
    // eslint-disable-next-line one-var -- The main path depends on the validated manifest identity.
    const mainPath = resolve(pluginDir, manifest.main);
    if (!isPathInside(pluginDir, mainPath) || !mainPath.endsWith('.js') || !isFile(mainPath)) {
        throw new PluginLoadError('PLUGIN_MAIN_INVALID', 'Plugin main bundle is invalid.');
    }
    // eslint-disable-next-line one-var -- Source is read only after the main path boundary check.
    const source = readFileSync(mainPath, 'utf8');
    scanBundleImports(source);
    return { manifest, source };
}
function loadOnePlugin(entry, configRoot, providerIds, policyKeys, hookIds, hostServices) {
    const { manifest, source } = loadPluginBundle(entry, configRoot), exported = evaluateBundleDefaultExport(source), plugin = materializePlugin(exported, manifest, hostServices);
    validatePluginShape(plugin, manifest, providerIds, policyKeys, hookIds);
    return { plugin };
}
async function loadOnePluginAsync(entry, configRoot, providerIds, policyKeys, hookIds, hostServices) {
    const { manifest, source } = loadPluginBundle(entry, configRoot), exported = evaluateBundleDefaultExport(source), plugin = await materializePluginAsync(exported, manifest, hostServices);
    validatePluginShape(plugin, manifest, providerIds, policyKeys, hookIds);
    return { plugin };
}
function readManifest(path) {
    let manifest;
    try {
        manifest = JSON.parse(readFileSync(path, 'utf8'));
    }
    catch {
        throw new PluginLoadError('PLUGIN_MANIFEST_INVALID', 'Plugin manifest is invalid.');
    }
    if (!validateManifest(manifest)) {
        throw new PluginLoadError('PLUGIN_MANIFEST_INVALID', 'Plugin manifest is invalid.');
    }
    const typed = manifest;
    if (typed.apiVersion !== undefined && !isSupportedPluginApiVersion(typed.apiVersion)) {
        throw new PluginLoadError('PLUGIN_API_VERSION_UNSUPPORTED', 'Plugin API version is unsupported.');
    }
    return typed;
}
function scanBundleImports(source) {
    const ws = String.raw `(?:\s|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*(?:\r?\n|$))*`, importPattern = new RegExp(String.raw `\bimport${ws}(?:\(${ws}["'][^"']+["']${ws}\)|(?:[^"'\x60;]+from${ws})?["'][^"']+["'])|\bexport${ws}[^"'\x60;]+from${ws}["'][^"']+["']`, 'u');
    if (importPattern.test(source)) {
        throw new PluginLoadError('PLUGIN_BUNDLE_IMPORT_SPECIFIER', 'Plugin bundle contains runtime import specifier.');
    }
}
function evaluateBundleDefaultExport(source) {
    const exports = new Map(), withoutSourceMap = source.replace(/\r?\n\/\/# sourceMappingURL=.*$/u, ''), exportListPattern = /\bexport\s*\{([^}]*)\}\s*;?/gu;
    let moduleBody = withoutSourceMap.replace(exportListPattern, (_statement, exportList) => {
        for (const rawEntry of exportList.split(',')) {
            const entry = rawEntry.trim();
            if (entry.length === 0) {
                continue;
            }
            // eslint-disable-next-line one-var -- The match follows the empty export-entry check.
            const match = /^([A-Za-z_$][\w$]*)(?:\s+as\s+([A-Za-z_$][\w$]*|default))?$/u.exec(entry);
            if (match === null) {
                throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin default export is invalid.');
            }
            // eslint-disable-next-line one-var -- The capture is checked after the pattern matches.
            const localName = match[1];
            if (localName === undefined) {
                throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin default export is invalid.');
            }
            exports.set(match[2] ?? localName, localName);
        }
        return '';
    }), returnExpression = exports.get('default');
    if (returnExpression === undefined) {
        if (!/\bexport\s+default\b/u.test(moduleBody)) {
            throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin default export is invalid.');
        }
        moduleBody = moduleBody.replace(/\bexport\s+default\b/u, 'const __nextagentPluginDefaultExport =');
        returnExpression = '__nextagentPluginDefaultExport';
    }
    if (/\bexport\s+(?:\*|\{|const\b|let\b|var\b|function\b|class\b|default\b)/u.test(moduleBody)) {
        throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin default export is invalid.');
    }
    try {
        // Existing isolated ESM bundle evaluation is guarded by the import scan and closed host registry.
        // eslint-disable-next-line @typescript-eslint/no-implied-eval, @typescript-eslint/no-unsafe-call
        return Function(`"use strict";\n${moduleBody}\n;return ${returnExpression};`)();
    }
    catch {
        throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin default export is invalid.');
    }
}
function materializePlugin(exported, manifest, hostServices) {
    const requiresFactory = (manifest.hostExternals?.length ?? 0) > 0 || manifest.apiVersion === '1.1' || manifest.apiVersion === '1.2';
    if (requiresFactory) {
        if (typeof exported !== 'function') {
            throw new PluginLoadError('PLUGIN_FACTORY_REQUIRED', 'Plugin with host externals must export a factory.');
        }
        for (const external of manifest.hostExternals ?? []) {
            const inventoryEntry = hostExternalsById.get(external.id);
            if (inventoryEntry === undefined) {
                throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_CLOSED', 'Host external is not open.');
            }
            if (!isVersionRangeCompatible(external.versionRange, inventoryEntry.version)) {
                throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_VERSION_INCOMPATIBLE', 'Host external version is incompatible.');
            }
        }
        const plugin = exported(createFactoryHost(manifest, hostServices));
        if (isPromiseLike(plugin)) {
            throw new PluginLoadError('PLUGIN_FACTORY_ASYNC_UNSUPPORTED', 'Plugin factory must materialize synchronously.');
        }
        return plugin;
    }
    if (typeof exported === 'function') {
        throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_DECLARATION_REQUIRED', 'Plugin factory requires hostExternals declaration.');
    }
    if (typeof exported === 'object' &&
        exported !== null &&
        (exported.apiVersion === '1.1' || exported.apiVersion === '1.2')) {
        throw new PluginLoadError('PLUGIN_FACTORY_REQUIRED', 'Plugin API 1.1 or later must use an explicit factory manifest.');
    }
    return exported;
}
async function materializePluginAsync(exported, manifest, hostServices) {
    const requiresFactory = (manifest.hostExternals?.length ?? 0) > 0 || manifest.apiVersion === '1.1' || manifest.apiVersion === '1.2';
    if (!requiresFactory) {
        return materializePlugin(exported, manifest, hostServices);
    }
    if (typeof exported !== 'function') {
        throw new PluginLoadError('PLUGIN_FACTORY_REQUIRED', 'Plugin with host externals must export a factory.');
    }
    for (const external of manifest.hostExternals ?? []) {
        const inventoryEntry = hostExternalsById.get(external.id);
        if (inventoryEntry === undefined) {
            throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_CLOSED', 'Host external is not open.');
        }
        if (!isVersionRangeCompatible(external.versionRange, inventoryEntry.version)) {
            throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_VERSION_INCOMPATIBLE', 'Host external version is incompatible.');
        }
    }
    return await exported(createFactoryHost(manifest, hostServices));
}
function createFactoryHost(manifest, hostServices) {
    const externals = createHostExternalRegistry((manifest.hostExternals ?? []).map((external) => external.id));
    if (manifest.apiVersion !== '1.1' && manifest.apiVersion !== '1.2') {
        return Object.freeze({ externals });
    }
    // eslint-disable-next-line one-var -- The sink is needed only for API versions with developer diagnostics.
    const sink = hostServices?.developerDiagnosticsForPlugin(manifest.pluginId) ?? noopDeveloperDiagnosticArtifactSink, hostV1_1 = {
        externals,
        developerDiagnostics: bindDeveloperDiagnosticSink(sink),
    };
    if (manifest.apiVersion === '1.1') {
        return Object.freeze(hostV1_1);
    }
    if (hostServices?.runtime === undefined) {
        throw new PluginLoadError('PLUGIN_RUNTIME_SERVICES_UNAVAILABLE', 'Plugin runtime services are unavailable.');
    }
    return Object.freeze({ ...hostV1_1, runtime: hostServices.runtime });
}
function bindDeveloperDiagnosticSink(sink) {
    const allowedKeys = new Set([
        'artifactType',
        'sessionId',
        'requestId',
        'runId',
        'agentId',
        'agentVersion',
        'agentAssemblyRef',
        'hookInvocationId',
        'payload',
    ]);
    return Object.freeze({
        async emit(input) {
            try {
                if (input === null || typeof input !== 'object' || Object.keys(input).some((key) => !allowedKeys.has(key))) {
                    return { status: 'DROPPED', reasonCode: 'INVALID_RECORD' };
                }
                return await sink.emit(input);
            }
            catch {
                return { status: 'DROPPED', reasonCode: 'OUTPUT_UNAVAILABLE' };
            }
        },
    });
}
function createHostExternalRegistry(ids) {
    const requested = new Set(ids), registry = Object.freeze({
        ...(requested.has('typebox') ? { typebox: Object.freeze({ Type }) } : {}),
        ...(requested.has('ajv') ? { ajv: Object.freeze({ Ajv }) } : {}),
    });
    return Object.freeze(new Proxy(registry, {
        get(target, property, receiver) {
            if (property === 'typebox' || property === 'ajv') {
                if (!requested.has(property)) {
                    throw new PluginLoadError('PLUGIN_HOST_EXTERNAL_NOT_DECLARED', 'Host external was not declared.');
                }
            }
            return Reflect.get(target, property, receiver);
        },
    }));
}
function validatePluginShape(plugin, manifest, providerIds, policyKeys, hookIds) {
    if (!isObject(plugin) || plugin.pluginId !== manifest.pluginId || plugin.version !== manifest.version) {
        throw new PluginLoadError('PLUGIN_EXPORT_INVALID', 'Plugin export identity is invalid.');
    }
    validatePluginApiVersion(plugin, manifest);
    if ((plugin.providers ?? []).length > 4) {
        throw new PluginLoadError('PLUGIN_PROVIDER_LIMIT_EXCEEDED', 'Plugin declares more than 4 providers.');
    }
    for (const provider of plugin.providers ?? []) {
        const { providerId } = provider.identity;
        if (provider.identity.providerKind !== 'CUSTOM' ||
            provider.identity.providerType !== pluginToolProviderType ||
            !safeId(providerId) ||
            providerIds.has(providerId) ||
            providerId === 'memory-tools') {
            throw new PluginLoadError('PLUGIN_PROVIDER_INVALID', 'Plugin provider identity is invalid.');
        }
        providerIds.add(providerId);
    }
    for (const policy of plugin.policies ?? []) {
        if (!openPolicyIds.has(policy.policyPointId)) {
            if (reservedPolicyIds.has(policy.policyPointId)) {
                throw new PluginLoadError('PLUGIN_POLICY_RESERVED', 'Plugin policy point is reserved.');
            }
            throw new PluginLoadError('PLUGIN_POLICY_CLOSED', 'Plugin policy point is closed.');
        }
        const key = `${policy.policyPointId}\0${policy.policyId}`;
        if (!safeId(policy.policyId) || policyKeys.has(key)) {
            throw new PluginLoadError('PLUGIN_POLICY_INVALID', 'Plugin policy identity is invalid.');
        }
        validateOpenPolicyShape(policy);
        if (policy.configSchema !== undefined &&
            (typeof policy.configSchema !== 'object' || policy.configSchema === null || Array.isArray(policy.configSchema))) {
            throw new PluginLoadError('PLUGIN_POLICY_INVALID', 'Plugin policy config schema is invalid.');
        }
        policyKeys.add(key);
    }
    for (const hook of plugin.hooks ?? []) {
        if (!safeId(hook.hookId) || hookIds.has(hook.hookId)) {
            throw new PluginLoadError('PLUGIN_HOOK_INVALID', 'Plugin hook identity is invalid.');
        }
        hookIds.add(hook.hookId);
    }
}
function validateOpenPolicyShape(policy) {
    if (policy.configure !== undefined && typeof policy.configure !== 'function') {
        throw new PluginLoadError('PLUGIN_POLICY_INVALID', 'Plugin policy executable is invalid.');
    }
    if (policy.policyPointId === 'agentRoutingPolicy' && typeof policy.decide !== 'function') {
        throw new PluginLoadError('PLUGIN_POLICY_INVALID', 'Plugin routing policy executable is invalid.');
    }
    if (policy.policyPointId === 'hostedAgentSelectionPolicy' && typeof policy.resolve !== 'function') {
        throw new PluginLoadError('PLUGIN_POLICY_INVALID', 'Plugin selection policy executable is invalid.');
    }
}
function validatePluginApiVersion(plugin, manifest) {
    const exportedApiVersion = plugin.apiVersion;
    if (exportedApiVersion !== undefined && typeof exportedApiVersion !== 'string') {
        throw new PluginLoadError('PLUGIN_API_VERSION_UNSUPPORTED', 'Plugin API version is unsupported.');
    }
    if (exportedApiVersion !== undefined && !isSupportedPluginApiVersion(exportedApiVersion)) {
        throw new PluginLoadError('PLUGIN_API_VERSION_UNSUPPORTED', 'Plugin API version is unsupported.');
    }
    if (manifest.apiVersion !== undefined && exportedApiVersion !== undefined && manifest.apiVersion !== exportedApiVersion) {
        throw new PluginLoadError('PLUGIN_API_VERSION_MISMATCH', 'Plugin API version does not match manifest.');
    }
    // eslint-disable-next-line one-var -- The effective version is selected after mismatch checks.
    const effectiveApiVersion = manifest.apiVersion ?? exportedApiVersion ?? ROOT_PLUGIN_API_VERSION;
    if (!isSupportedPluginApiVersion(effectiveApiVersion)) {
        throw new PluginLoadError('PLUGIN_API_VERSION_UNSUPPORTED', 'Plugin API version is unsupported.');
    }
}
function safeId(value) {
    return /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/u.test(value);
}
function isVersionRangeCompatible(range, version) {
    const normalized = range.trim();
    if (normalized === '*' || normalized === version) {
        return true;
    }
    if (!normalized.startsWith('^')) {
        return false;
    }
    // eslint-disable-next-line one-var -- Versions are parsed only for a compatible range prefix.
    const lower = parseVersion(normalized.slice(1)), current = parseVersion(version);
    if (lower === undefined || current === undefined || compareVersion(current, lower) < 0) {
        return false;
    }
    if (lower.major > 0) {
        return current.major === lower.major;
    }
    if (lower.minor > 0) {
        return current.major === 0 && current.minor === lower.minor;
    }
    return current.major === 0 && current.minor === 0 && current.patch === lower.patch;
}
function parseVersion(value) {
    const match = /^(\d+)\.(\d+)\.(\d+)$/u.exec(value.trim());
    if (match === null) {
        return undefined;
    }
    return {
        major: Number(match[1]),
        minor: Number(match[2]),
        patch: Number(match[3]),
    };
}
function compareVersion(left, right) {
    return left.major - right.major || left.minor - right.minor || left.patch - right.patch;
}
function isSupportedPluginApiVersion(value) {
    return SUPPORTED_PLUGIN_API_VERSIONS.includes(value);
}
function isObject(value) {
    return value !== null && typeof value === 'object';
}
function isPromiseLike(value) {
    return isObject(value) && typeof value.then === 'function';
}
function safeDiagnostic(severity, reasonCode, pluginId, error) {
    const safeError = error instanceof PluginLoadError ? error : undefined;
    return {
        severity,
        reasonCode: safeError?.safeReasonCode ?? reasonCode,
        pluginId,
        outcome: 'rejected',
        summary: safeError?.safeSummary ?? 'Plugin validation failed.',
    };
}
function isDirectory(path) {
    try {
        return statSync(path).isDirectory();
    }
    catch {
        return false;
    }
}
function isFile(path) {
    try {
        return statSync(path).isFile();
    }
    catch {
        return false;
    }
}
function deepFreeze(snapshot) {
    return Object.freeze({
        plugins: Object.freeze([...snapshot.plugins]),
        providers: Object.freeze([...snapshot.providers]),
        policies: Object.freeze([...snapshot.policies]),
        hooks: Object.freeze([...snapshot.hooks]),
        diagnostics: Object.freeze([...snapshot.diagnostics]),
    });
}
//# sourceMappingURL=plugin-loader.js.map