# Research asset provenance

Created 2026-09-20 as new research models, subsequently branded with official
MOBILTECH wordmarks on the carton, can and mug at the user's request. No
ReplicaCity geometry, textures, materials, source packages or physics were edited or copied.

The v1.1 logo and mass update is documented in [MASS_AND_BRANDING.md](MASS_AND_BRANDING.md).
It used the original website SVGs, not image generation. Peer Qwen completed the
reviewed update in one MCP call with zero errors (7,994 peer tokens).

## Two-machine authoring

- Authoring: native local Blender 5.2.2, connected through Blender MCP.
- Worker: the existing peer Qwen endpoint, model `qwen3.6-35b`.
- Supervisor: reviewed geometry helpers, export/physics code, visual inspection,
  and isolated local Isaac Sim validation. Existing model/simulation services
  were not reconfigured.
- Qwen's initial unrestricted code draft was rejected before execution because
  it proposed deleting existing objects and had API/geometry problems.
- Qwen subsequently executed all five reviewed asset-building calls through
  MCP. It then repeated those calls; the overwrite guard rejected the repeats
  before creating scenes. The worker job therefore did not have a clean final
  status, even though its five initial exports were verified successfully.
- Supervisor refinements corrected phone bottom clearance, tube frames,
  visible camera lenses, can lid details, and small-object contact settings.

Detailed worker logs and rejected drafts remain in the original workspace;
they are not distributed in this repository.
Reported peer usage: draft 8,578 tokens; MCP authoring run 33,409 tokens.
This is peer usage, not an estimate of frontier-token savings.

## Visual provenance

Catalog images are Cycles renders of the delivered Blender meshes. They are
not AI-generated product concept images. Geometry is procedural, with authored
PBR parameters and mesh-based package printing. The objects are plausible
designs, not dimensionally verified scans of commercial products.

The image-generation skill supplied the beech base-color image only:

- Original project copy: `resources/beech_basecolor.png`.
- Referenced asset copy: `wood_block_001/textures/wood_basecolor.png`.
- Base-color map uses sRGB; numeric roughness/metallic parameters are linear.
- No measured BRDF, normal, height or roughness maps are provided.
- Grain is a small sanded side-grain sample; end grain is not separately modeled.

Final image-generation prompt:

> Use case: photorealistic-natural. Asset type: PBR base-color texture for a realistically scaled beechwood robot-grasping block. Generate ONE square, edge-to-edge, orthographic flat texture of clean natural light European beech wood side grain. Fine straight grain runs horizontally, with subtle medullary flecks, narrow gently undulating grain lines and warm pale honey/tan tonal variation. This represents a small 12 cm wide patch of sanded solid wood, not flooring planks. Neutral diffuse albedo appearance, uniform shadow-free illumination, no specular highlights or directional shading. Seamless-looking edges, restrained contrast, crisp natural pores. No object perspective, no boards or joins, no knots, no cracks, no frame, no text, no watermark. The entire image must be only wood surface; suitable for UV mapping onto a small 6 by 4 by 3 cm block.

## Physical provenance and limits

Masses now use published comparable-object values or documented density/package
calculations. They are not measured specimen data. Friction and restitution are
still design estimates. Printed net weight excludes packaging and is not calibration evidence. Inertia and
center of mass are integrated from uniformly dense collision proxies, including
additive overlap of compound parts. Real packaging, food distribution, a phone's
battery and camera assembly can have different mass distributions.

All objects are rigid: there is no carton crushing, ceramic fracture, food or
liquid dynamics, electronic behavior, or material compliance. Small printed
details, speaker openings and surface relief do not get independent collision
geometry. The mug's opening and handle opening do remain open for contact.

The first default-settings contact test passed 13/15 drops. Fixing the contact
sensor setup and using 16/4 solver iterations passed 14/15, with slight phone
resting jitter. Raising solver iterations to 32/8 did not resolve it and was
reverted. The delivered Isaac profile uses 16 position / 4 velocity iterations
and 1 mm contact offset, 0 rest offset; the final test and demo use a smaller
1/480-second physics timestep. Final results, including any
failures, are in `validation/isaac_physics_validation.json`; earlier evidence is
preserved in the original workspace, outside this repository.

Original v1 outcome: 14/15 drops pass. The tilted phone drop failed only the angular
speed threshold (0.110886 rad/s versus 0.100); all contact, translation, linear
speed and penetration checks pass. This known issue is deliberately retained
in the original report rather than hidden by loosening the pass threshold. That
historical result has been superseded by the post-mass-update v1.1 regression
in `validation/isaac_physics_validation.json`.

No formal SimReady certification, robot-grasp success, calibrated friction,
sim-to-real transfer, or production suitability is claimed.
