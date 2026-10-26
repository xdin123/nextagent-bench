from __future__ import annotations

import json
import posixpath
import re
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from .util import adapter_sha, command, digest, file_sha, fs_path, now, read_json, tree_manifest, write_json
from .docker import build_image

RUNTIME_DIRS = ('logs', 'run', 'workspaces', 'data', '__pycache__')


def inspect_archive(source: Path) -> dict:
    metadata, candidates, count, size = {}, [], 0, 0
    with tarfile.open(source) as archive:
        for member in archive:
            name = posixpath.normpath(member.name.replace('\\', '/'))
            if name.startswith(('/', '../')) or name == '..' or ':' in name.split('/')[0]:
                raise ValueError('Unsafe archive member: ' + name)
            if member.issym() or member.islnk():
                target = member.linkname.replace('\\', '/')
                normalized = posixpath.normpath(posixpath.join(posixpath.dirname(name), target) if member.issym() else target)
                if target.startswith('/') or normalized.startswith('../') or normalized == '..':
                    raise ValueError('Archive link escapes deployment: ' + name)
            if member.isfile():
                count += 1
                size += member.size
                if name.endswith('candidate-manifest.json') or (name.endswith('package.json') and
                    (len(PurePosixPath(name).parts) <= 3 or any(name.endswith('node_modules/' + item + '/package.json')
                        for item in ('ai', '@ai-sdk/openai-compatible', '@ai-sdk/provider', '@ai-sdk/provider-utils')))):
                    data = json.loads(archive.extractfile(member).read())
                    metadata[name] = data
                    if name.endswith('candidate-manifest.json'):
                        candidates.append(name)
    if len(candidates) != 1:
        raise ValueError('Archive must contain exactly one candidate-manifest.json')
    candidate_name = candidates[0]
    prefix = posixpath.dirname(candidate_name)
    prefix = prefix + '/' if prefix else ''
    candidate = metadata[candidate_name]
    if candidate.get('platform') != 'linux' or candidate.get('arch') != 'x64':
        raise ValueError('Expected a Linux x64 release bundle')
    if not re.fullmatch(r'v?\d+\.\d+\.\d+', candidate.get('nodeVersion', 'v22.22.0')):
        raise ValueError('Invalid Node version in candidate manifest')
    package = metadata.get(prefix + 'package.json', {})
    if '@nextagent/agent-app' not in package.get('dependencies', {}):
        raise ValueError('Not a NextAgent deployment bundle')
    sdk = {}
    for name in ('ai', '@ai-sdk/openai-compatible', '@ai-sdk/provider', '@ai-sdk/provider-utils'):
        item = metadata.get(prefix + 'node_modules/' + name + '/package.json')
        if item:
            sdk[name] = item.get('version')
    return {'candidate': candidate, 'strip_components': len(PurePosixPath(prefix).parts),
            'sdk_versions': sdk, 'archive_files': count, 'uncompressed_bytes': size}


def import_framework(project: Path, source: Path) -> dict:
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    parent = project / 'artifacts'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='import-', dir=parent) as temporary:
        stage = Path(temporary) / 'ready'
        stage.mkdir()
        bundle = stage / 'bundle.tar.gz'
        if source.is_dir():
            if not (source / 'candidate-manifest.json').is_file():
                raise ValueError('Deployment directory has no candidate-manifest.json')
            # BSD tar's exclusion matching also applies to nested data/ paths.
            # Enumerate only permitted top-level entries; keep package data intact.
            entries = sorted(child.name for child in source.iterdir() if child.name not in RUNTIME_DIRS)
            command(['tar', '-czf', str(bundle), '-C', str(source), '--'] + entries, timeout=1800)
        else:
            shutil.copyfile(source, bundle)
        identity = file_sha(bundle)
        target = parent / identity
        if (target / 'manifest.json').exists():
            return read_json(target / 'manifest.json')
        details = inspect_archive(bundle)
        manifest = {'sha256': identity, 'source': str(source), 'source_kind': 'directory-snapshot' if source.is_dir() else 'archive',
                    'imported_at': now(), 'deployment_sha': identity, 'excluded_runtime_directories': list(RUNTIME_DIRS),
                    'product_patches_applied': [], **details}
        write_json(stage / 'manifest.json', manifest)
        stage.rename(target)
    return manifest


def import_dataset(project: Path, source: Path) -> dict:
    project, source = fs_path(project), fs_path(source.resolve())
    if not (source / 'tasks').is_dir():
        if source.name == 'tasks':
            source = source.parent
        else:
            raise ValueError('dataset must contain tasks/')
    files = tree_manifest(source / 'tasks')
    identity = digest(files)
    target = project / 'datasets' / identity
    if (target / 'manifest.json').exists():
        return read_json(target / 'manifest.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dataset-', dir=target.parent) as temporary:
        output = Path(temporary) / 'ready'
        output.mkdir()
        shutil.copytree(source / 'tasks', output / 'tasks', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if digest(tree_manifest(output / 'tasks')) != identity:
            raise ValueError('Dataset source changed while importing; retry after the source is stable')
        for name in ('README.md', 'LICENSE', 'registry.json', 'AGENTS.md'):
            if (source / name).is_file():
                shutil.copyfile(source / name, output / name)
        manifest = {'sha256': identity, 'source': str(source), 'imported_at': now(),
                    'tasks': sorted(path.name for path in (output / 'tasks').iterdir() if (path / 'task.md').exists()),
                    'note': 'Snapshot of existing locally adapted dataset; original verifier/oracle preserved byte-for-byte.'}
        write_json(output / 'files.json', files)
        write_json(output / 'manifest.json', manifest)
        output.rename(target)
    return manifest


def framework_image(project: Path, artifact: dict, log: Path) -> str:
    source = project / 'artifacts' / artifact['sha256'] / 'bundle.tar.gz'
    if file_sha(source) != artifact['sha256']:
        raise ValueError('Frozen framework archive changed; import a new artifact')
    identity = digest({'deployment': artifact['sha256'], 'adapter': adapter_sha()})
    image = 'nextagent-bench/framework:' + identity[:20]
    if command(['docker', 'image', 'inspect', image], check=False).returncode == 0:
        return image
    context = project / 'cache' / 'framework' / identity
    context.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, context / 'bundle.tar.gz')
    shutil.copytree(Path(__file__).parent / 'runtime', context / 'runtime', dirs_exist_ok=True)
    version = artifact['candidate'].get('nodeVersion', 'v22.22.0').removeprefix('v')
    strip = int(artifact['strip_components'])
    cleanup = ' '.join('/opt/nextagent/' + name for name in RUNTIME_DIRS)
    (context / 'Dockerfile').write_text(
        f'FROM node:{version}-bookworm-slim AS unpack\nCOPY bundle.tar.gz /tmp/bundle.tar.gz\n'
        f'RUN mkdir -p /opt/nextagent && tar -xzf /tmp/bundle.tar.gz -C /opt/nextagent --strip-components={strip} && rm -rf {cleanup}\n'
        'FROM scratch\nCOPY --from=unpack /opt/nextagent/ /opt/nextagent/\nCOPY runtime/ /opt/na-eval/runtime/\n', encoding='utf-8')
    build_image(image, context, 1200, log)
    return image
