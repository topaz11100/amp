# Implementation Explanation

This document summarizes how the codebase implements the pipeline required by `docs/Theory.md` and how each module aligns with the theory-driven design.

## Color Simulation (`src/color_sim.py`)
- Implements the fixed sequence from Theory.md §0.2 and §4: BGR→RGB normalization → sRGB→linear (power-law gamma 2.2) → domain shrink (Eq.(2)) → RGB→LMS (Eq.(4)) → Viénot deutan matrix (Eq.(5)) → LMS→RGB (inverse of Eq.(4)) → linear→sRGB → BGR.
- `VienotDeutanParams` stores all fixed numerical constants from Viénot et al. (1999) and the derived inverse matrix. `DogPostParams` isolates HSV postprocessing parameters labeled as visualization-only per Theory.md §9A.
- `simulate_animal_color` keeps algorithm selection outside the UI: cat mode returns the pure Viénot simulation (§2.2), while dog mode applies additional HSV postprocessing to enforce 2-hue behavior and cyan desaturation (§6, §9A).

## Dog Postprocessing
- `dog_postprocess_hsv` follows Theory.md §6/§9A by: (A) reducing saturation around the cyan band to approximate the neutral point shift, (B) compressing hue toward blue/yellow attractors to recreate the two-hue phenomenon, and (C) applying a global saturation scale to tame artifacts. Parameters are passed explicitly as a dataclass to keep provenance clear (§9.3).

## Focus Blur (`src/focus_blur.py`)
- Implements the click-based defocus model from Theory.md §7. The blur map uses the smoothstep transition between radii `r0` and `r1`, raises it by `p`, scales by `sigma_max`, and blends between a precomputed Gaussian blur stack (`levels`). This preserves the spatially varying sigma(x, y) structure demanded by the theory.

## Streamlit UI (`src/app.py`)
- Follows the interface in Theory.md §8.4: upload, animal selection, research-mode toggle for dog HSV parameters, image click to set focus, and download. Algorithm selection is delegated to `simulate_animal_color`, keeping UI logic separate from pipeline logic.
- Resizing is kept aspect-preserving and optional through `max_side` selection to balance fidelity and performance without altering the core transformations.

## Utilities (`src/utils.py`)
- Provides thin, explicit helpers for decoding uploads, resizing by maximum side, and encoding PNG downloads. These utilities avoid hidden state and keep the main modules focused on theory-critical logic.

## Parameter Provenance
- Numerical constants for LMS matrices, domain shrink, and gamma follow Theory.md §9.1. The inverse LMS matrix is computed programmatically per §9.2. Dog HSV parameters are the recommended visualization defaults from §9A and remain user-tunable via research mode.

## Future Work
- Any further changes must continue to mirror `docs/Theory.md`. If new phenomena or algorithms are required but absent from the theory, they should be added to Theory.md before implementation, as mandated by the project rules.
