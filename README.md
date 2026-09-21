# Replica City AI Generated Assets

Version **1.1.0** · collection ID `replica_city_ai_generated_assets`

Five realistically scaled research objects for robotic manipulation, with
editable Blender sources, OpenUSD/PBR visuals, collision geometry, mass and
inertia estimates, Isaac Sim profiles, and validation evidence.

![Rendered collection](assets/grasp_set_v1/preview.png)

| Object | Mass | State |
|---|---:|---|
| Wood block | 51.84 g | Solid beech |
| Food carton | 165 g | Filled and sealed |
| Food can | 349 g | Filled and sealed |
| Ceramic mug | 295 g | Empty |
| Cell phone | 187 g | Battery included, no case |

The carton, can and mug carry MOBILTECH wordmarks. All masses are reference-based
estimates, not measurements of physical specimens.

## Use

1. Clone or download this repository, keeping its directory structure intact.
2. In Isaac Sim, open `assets/grasp_set_v1/grasp_set_isaac.usda` and press Play.
3. For your own scene, reference an individual `<asset_id>_isaac.usda` file.
   Keep scale at 1; each asset already has one root rigid body.
4. For other USD tools, use `<asset_id>.usda`. For Blender, open
   `assets/grasp_set_v1/showcase.blend` for the whole set. Individual
   `authoring.blend` files are scene libraries: use File > Append, browse to
   the file's Scene section, append its research scene, and select that scene.

The full [asset guide](assets/grasp_set_v1/README.md) documents units, entrypoints,
collision conventions and reproduction commands. The machine-readable catalog
is [collection.json](assets/grasp_set_v1/collection.json).

## Validation and limitations

Authored in Blender 5.2.2; physics evidence was collected in Isaac Sim 6.0.0.1.
Static USD and relocation checks pass for all five assets. The recorded physics
test passes **13/15** drops at 480 Hz: wood, carton, can and mug pass 3/3 each;
the phone passes 1/3 and needs resting-contact tuning. Its other two poses exceed
the resting angular-speed threshold. This is **not formal SimReady certification**,
and robot-grasp success has not yet been tested.

Run a read-only integrity check from the repository root:

```bash
python3 scripts/verify_asset_release.py
```

Add `--usd` in a Python environment with OpenUSD's `pxr` module to check all
entrypoints and dependencies. This verifies packaging; it does not rerun physics.

See [physics evidence](assets/grasp_set_v1/validation/isaac_physics_validation.json),
[mass and branding sources](assets/grasp_set_v1/MASS_AND_BRANDING.md), and
[authoring provenance](assets/grasp_set_v1/PROVENANCE.md).

## Scope and rights

This collection is distinct from the original ReplicaCity asset library. No
original ReplicaCity geometry, textures or source packages are included.
Builds, machine configuration, credentials and private worker logs are excluded.

No open-source or asset redistribution license has been assigned to this
repository. MOBILTECH branding remains subject to its owner's rights; see
[NOTICE.md](NOTICE.md). Review permissions before public redistribution.
