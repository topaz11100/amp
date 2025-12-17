# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
"""
Color transformation pipeline implementing Viénot deutan simulation and dog-specific
HSV postprocessing as specified in docs/Theory.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np


@dataclass
class VienotDeutanParams:
    """Fixed parameters drawn from Viénot et al. (1999) and Theory.md §4, §9."""

    gamma: float
    # Eq.(2) domain shrink coefficients (Theory.md §4.5)
    domain_shrink_k: float
    domain_shrink_b: float
    # Eq.(4) RGB→LMS matrix
    M_rgb2lms: np.ndarray
    # Eq.(5) deutan LMS matrix
    M_deutan_lms: np.ndarray
    # inv(Eq.(4)) LMS→RGB matrix (computed, not hard-coded)
    M_lms2rgb: np.ndarray


@dataclass
class DogPostParams:
    """Visualization parameters for dog HSV postprocessing (Theory.md §6, §9A)."""

    cyan_h0: float
    cyan_sigma: float
    cyan_desat: float

    blue_h: float
    yellow_h: float
    blue_cutoff: float

    blue_compress: float
    yellow_compress: float

    sat_global: float


@dataclass
class ColorSimParams:
    """Bundle of color simulation parameters for reuse in the pipeline."""

    vienot: VienotDeutanParams
    dog_post: DogPostParams


def srgb_to_linear_pow(rgb01: np.ndarray, gamma: float) -> np.ndarray:
    """Apply power-law decoding from sRGB to linear RGB (Theory.md §4.1).

    Args:
        rgb01: RGB image in [0,1].
        gamma: Gamma exponent (2.2 per Theory.md §9.1).

    Returns:
        Linear RGB array in [0,1].
    """

    return np.power(np.clip(rgb01, 0.0, 1.0), gamma, dtype=np.float32)


def linear_to_srgb_pow(lin01: np.ndarray, gamma: float) -> np.ndarray:
    """Apply power-law encoding from linear RGB to sRGB (Theory.md §4.1)."""

    return np.power(np.clip(lin01, 0.0, 1.0), 1.0 / gamma, dtype=np.float32)


def _apply_domain_shrink(rgb_lin: np.ndarray, k: float, b: float) -> np.ndarray:
    """Affine shrink in linear RGB to stabilize gamut (Theory.md §4.5, Eq.(2))."""

    return k * rgb_lin + b


def _bgr_to_rgb01(bgr_u8: np.ndarray) -> np.ndarray:
    """Convert uint8 BGR to float32 RGB in [0,1] without altering content."""

    rgb = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2RGB).astype(np.float32)
    return rgb / 255.0


def _rgb01_to_bgr(rgb01: np.ndarray) -> np.ndarray:
    """Convert float RGB [0,1] to uint8 BGR with rounding."""

    rgb_u8 = np.clip(rgb01 * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8)
    return cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)


def simulate_vienot_deutan(bgr_u8: np.ndarray, p: VienotDeutanParams) -> np.ndarray:
    """Viénot deutan simulation pipeline (Theory.md §4.1–§4.4).

    Processing order is fixed: BGR→RGB→sRGB→linear→domain shrink→RGB→LMS→deutan→
    RGB→linear→sRGB→BGR.
    """

    # BGR -> RGB [0,1]
    rgb01 = _bgr_to_rgb01(bgr_u8)

    # sRGB -> linear (gamma removal)
    rgb_lin = srgb_to_linear_pow(rgb01, p.gamma)

    # domain shrink (Eq.(2)) in linear space
    rgb_lin = _apply_domain_shrink(rgb_lin, p.domain_shrink_k, p.domain_shrink_b)

    # RGB -> LMS (Eq.(4))
    lms = cv2.transform(rgb_lin, p.M_rgb2lms)

    # deutan transformation (Eq.(5))
    lms_d = cv2.transform(lms, p.M_deutan_lms)

    # LMS -> RGB (inverse of Eq.(4))
    rgb_d_lin = cv2.transform(lms_d, p.M_lms2rgb)

    # linear -> sRGB (gamma restoration)
    rgb_d = linear_to_srgb_pow(rgb_d_lin, p.gamma)

    # RGB -> BGR uint8
    return _rgb01_to_bgr(rgb_d)


def dog_postprocess_hsv(bgr_u8: np.ndarray, p: DogPostParams) -> np.ndarray:
    """Dog-specific HSV postprocessing enforcing perceptual constraints (Theory.md §6, §9A)."""

    hsv = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # (A) Cyan/blue-green desaturation toward neutral (neutral band near 480nm proxy)
    dh = np.minimum(np.abs(H - p.cyan_h0), 180.0 - np.abs(H - p.cyan_h0))
    w = np.exp(-(dh * dh) / (2.0 * p.cyan_sigma * p.cyan_sigma))
    S = S * (1.0 - p.cyan_desat * w)

    # (B) Two-hue compression toward blue and yellow attractors (linear interpolation)
    is_blue = H >= p.blue_cutoff
    H2 = H.copy()
    H2[is_blue] = (1.0 - p.blue_compress) * H[is_blue] + p.blue_compress * p.blue_h
    H2[~is_blue] = (1.0 - p.yellow_compress) * H[~is_blue] + p.yellow_compress * p.yellow_h

    # (C) Global saturation scaling to suppress artifacts
    S2 = np.clip(S * p.sat_global, 0.0, 255.0)

    hsv2 = np.stack([np.clip(H2, 0.0, 179.0), S2, V], axis=-1).astype(np.uint8)
    return cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)


def simulate_animal_color(bgr_u8: np.ndarray, animal: str, p: ColorSimParams) -> np.ndarray:
    """Run color simulation for the specified animal mode.

    Args:
        bgr_u8: Input image in BGR uint8.
        animal: "cat" or "dog".
        p: Color simulation parameters.
    """

    base = simulate_vienot_deutan(bgr_u8, p.vienot)

    if animal == "cat":
        # Cat uses only the Viénot deutan simulation (Theory.md §2.2, §5).
        return base

    if animal == "dog":
        # Dog adds HSV postprocessing enforcing perceptual phenomena (Theory.md §6, §9A).
        return dog_postprocess_hsv(base, p.dog_post)

    raise ValueError("animal must be 'cat' or 'dog'")


def default_color_params() -> ColorSimParams:
    """Return default parameters based on Theory.md §8.2, §9."""

    # Viénot et al. (1999) constants (Theory.md §9.1)
    M_rgb2lms = np.array([
        [17.8824, 43.5161, 4.11935],
        [3.45565, 27.1554, 3.86714],
        [0.0299566, 0.184309, 1.46709],
    ], dtype=np.float32)

    M_deutan = np.array([
        [1.0, 0.0, 0.0],
        [0.494207, 0.0, 1.24827],
        [0.0, 0.0, 1.0],
    ], dtype=np.float32)

    # Derived from theory principle: inverse of Eq.(4)
    M_lms2rgb = np.linalg.inv(M_rgb2lms).astype(np.float32)

    vienot = VienotDeutanParams(
        gamma=2.2,
        domain_shrink_k=0.957237,
        domain_shrink_b=0.0213814,
        M_rgb2lms=M_rgb2lms,
        M_deutan_lms=M_deutan,
        M_lms2rgb=M_lms2rgb,
    )

    # Visualization parameters (not physiological constants) per Theory.md §9A
    dog_post = DogPostParams(
        cyan_h0=90.0,
        cyan_sigma=12.0,
        cyan_desat=0.70,
        blue_h=120.0,
        yellow_h=30.0,
        blue_cutoff=95.0,
        blue_compress=0.70,
        yellow_compress=0.55,
        sat_global=0.90,
    )

    return ColorSimParams(vienot=vienot, dog_post=dog_post)
