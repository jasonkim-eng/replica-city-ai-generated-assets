"""Read-only verification of the packaged research assets; not a physics rerun."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, default=Path('assets/grasp_set_v1'))
    parser.add_argument('--usd', action='store_true', help='Also resolve USD dependencies; requires pxr')
    args = parser.parse_args()
    base = args.assets.resolve()
    collection = json.loads((base / 'collection.json').read_text())
    manifest = json.loads((base / 'manifest.json').read_text())
    report = json.loads((base / 'validation/isaac_physics_validation.json').read_text())
    failures = []
    for key in ('guide', 'validation_manifest', 'provenance', 'mass_and_branding_sources',
                'isaac_scene', 'blender_showcase', 'preview'):
        if not (base / collection[key]).is_file():
            failures.append('Missing collection file: ' + collection[key])
    for asset in collection['assets']:
        for key in ('usd', 'isaac_usd', 'blend'):
            if not (base / asset[key]).is_file():
                failures.append('Missing asset file: ' + asset[key])
    for evidence in (manifest['usd_sha256'], report['source_usd_sha256']):
        for relative, expected in evidence.items():
            path = base / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                failures.append('USD evidence hash mismatch: ' + relative)
    entrypoints = [base / asset[key] for asset in collection['assets'] for key in ('usd', 'isaac_usd')]
    entrypoints.append(base / collection['isaac_scene'])
    if args.usd:
        from pxr import Usd, UsdUtils
        for path in entrypoints:
            stage = Usd.Stage.Open(str(path))
            if not stage or not stage.GetDefaultPrim():
                failures.append('Cannot open default prim: ' + str(path.relative_to(base)))
            layers, assets, unresolved = UsdUtils.ComputeAllDependencies(str(path))
            dependencies = [Path(str(p)) for p in assets]
            dependencies += [Path(layer.realPath) for layer in layers if layer.realPath]
            if unresolved or any(not p.is_file() or not p.resolve().is_relative_to(base) for p in dependencies):
                failures.append('Unresolved or external dependency: ' + str(path.relative_to(base)))
    print(json.dumps({
        'release': collection['release_version'], 'assets': len(collection['assets']),
        'usd_files_hash_checked': len(manifest['usd_sha256']),
        'entrypoints_dependency_checked': len(entrypoints) if args.usd else 0,
        'recorded_drop_trials_passed': sum(trial['passed'] for trial in report['trials']),
        'recorded_drop_trials_total': len(report['trials']),
        'note': 'Existing simulation evidence only; physics was not rerun.',
        'failures': failures, 'package_integrity_passed': not failures,
    }, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
