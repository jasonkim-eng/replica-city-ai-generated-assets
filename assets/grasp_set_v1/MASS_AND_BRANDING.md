# MOBILTECH branding and reference-based masses

Updated 2026-09-20 at the user's request. Values below are entered in each asset's
`physics.usda` as `physics:mass` in kilograms. Both the portable and Isaac
entrypoints compose that layer. Center of mass and diagonal inertia were
recomputed consistently with the new mass using the existing collision proxies.

## Official logo

The artwork comes directly from the current [MOBILTECH official website](https://www.mobiltech.io/):
its original inline blue header wordmark (`#0069C8`) and light footer wordmark
(`#DDDDDD`). They are saved unchanged, with source URLs and SHA-256 checksums, in
`resources/mobiltech/`. No replacement font or AI-drawn approximation was used.

- Carton: blue wordmark on the upper cream label.
- Can: blue wordmark on the upper cream band, following the cylinder.
- Mug: light wordmark on the teal glaze, following the tapered body.

The vector outlines were converted to thin print meshes and included in both
the Blender source and USD visual geometry. They introduce no logo-texture or
font dependency and no additional collision shapes. MOBILTECH artwork remains
MOBILTECH's branding; these are user-requested research mockups, not a claim
that the company manufactures or endorses these food products.

## Mass values and basis

| Asset | USD mass | State | Basis |
|---|---:|---|---|
| Wood block | 0.05184 kg | Solid European beech | Nominal volume × wood density |
| Food carton | 0.165 kg | Filled and sealed | 150 g contents + estimated 15 g package |
| Food can | 0.349 kg | Filled and sealed | Comparable YCB tomato soup can total mass |
| Ceramic mug | 0.295 kg | Empty | Comparable 80 mm × 93 mm ceramic mug |
| Cell phone | 0.187 kg | Battery included, no case | Comparable compact smartphone |

### Wood block

The 60 × 40 × 30 mm block has nominal volume 0.000072 m³. Using approximately
720 kg/m³ gives **51.84 g**; small bevel volume is neglected. Density is based on
the supplier's European beech figure at approximately 15% moisture content.
Actual moisture and wood stock will change the mass. [Halswell Timber](https://www.halswelltimber.co.nz/timber-species/beech-european/)

### Food carton

Use **165 g gross**, keeping the printed **150 g net contents**. A real
150 g oat-based snack package is the contents-mass reference, not an exact
geometry match. [Nairn's product page](https://nairns.com/our-range/flatbreads/rosemary-sea-salt-flatbreads)

The modeled box surface area is 0.032 m². At an assumed 350 g/m² board weight,
the bare six faces weigh 11.2 g; folds, glue and liner bring the adopted package
allowance to 15 g. This is our engineering estimate, not a published package
weight. The board manufacturer's range includes 350 g/m².
[Holmen Incada Exel data](https://www.holmen.com/en/board-and-paper/products/paperboard/incada/incada-exel/)

### Food can

Use **349 g gross**, matching the tomato soup can listed in the YCB research
dataset. This is a close analogue for the modeled Ø65 × 100 mm can, not a
measurement of this synthetic mesh. [YCB dataset paper, Table 1](https://journals.sagepub.com/doi/10.1177/0278364917700714)

The visual label now says **NET WT 305 g**, corresponding to the rounded mass
of 10.75 oz contents. It does not say 349 g because that includes the container.
[Campbell's 10.75 oz product](https://www.campbellsfoodservice.com/product/campbells-condensed-tomato-soup-10-75-oz-can-12-pack/)

### Empty ceramic mug

Use **295 g** from the supplier-listed Cambridge ceramic mug, Ø80 mm × 93 mm
high, close to the modeled Ø80 mm × 95 mm body. The reference is unit mass,
not the shipping/carton weight. No liquid is included.
[Cambridge mug specifications](https://www.mugstore.co.uk/cambridge-mug-19309)

### Cell phone

Use **187 g**, the published Pixel 8 device mass, as a realistic baseline for
the similarly sized generic phone. It remains unbranded and is not a Pixel
geometry replica. [Google hardware specifications](https://support.google.com/pixelphone/answer/7158570?hl=en)

## Remaining uncertainty

These are traceable representative values, **not calibrated specimen masses**.
Friction and restitution remain unmeasured estimates. The inertia model still
assumes uniform density over collision proxies; packaging, battery placement,
food distribution and ceramic wall variation are not measured. The printed
branding has negligible mass and is not a separate rigid body.

The physics regression is recorded in `validation/isaac_physics_validation.json`.
It passes 13/15 drops. The three branded assets pass all 9/9; the wood block also
passes 3/3. The phone passes 1/3 and retains its known small resting-jitter issue
(angular speeds 0.124 and 0.143 rad/s in two poses, above the 0.100 rad/s limit).
Robot-grasp success and formal SimReady certification remain untested.

## Reproducibility and preservation

- Mass reference inputs are included in `validation/mass_references.json`.
- Original source SVGs and source URLs/checksums are in `resources/mobiltech/`.
- Editable branded geometry is included in each `authoring.blend`.
- The peer Qwen update completed in one successful MCP call with zero tool
  errors and 7,994 peer tokens. Full logs and pre-update backups remain in the
  original workspace, outside this repository.
- No ReplicaCity originals or running model/simulation services were modified.
