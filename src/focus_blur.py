# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
"""
Click-based defocus blur implementation following Theory.md §7.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class FocusBlurParams:
    """Visualization parameters for spatially varying defocus (Theory.md §7)."""

    r0: float
    r1: float
    sigma_max: float
    p: float
    levels: int


def apply_focus_blur_bgr(bgr_u8: np.ndarray, x0: int, y0: int, p: FocusBlurParams) -> np.ndarray:
    """Apply spatially varying Gaussian blur using click-defined focus (Theory.md §7).

    Args:
        bgr_u8: Input BGR image.
        x0, y0: Focus center coordinates (pixel space of current image).
        p: Blur control parameters.
    """

    H, W = bgr_u8.shape[:2]

    # Precompute blur levels (Gaussian sigma stack)
    sigma_levels = np.linspace(0.0, p.sigma_max, p.levels, dtype=np.float32)

    stack = []
    for s in sigma_levels:
        if s <= 1e-6:
            stack.append(bgr_u8.astype(np.float32))
        else:
            stack.append(
                cv2.GaussianBlur(
                    bgr_u8, (0, 0), sigmaX=float(s), sigmaY=float(s)
                ).astype(np.float32)
            )
    stack = np.stack(stack, axis=0)

    # Distance from focus point (Eq. in Theory.md §7)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - x0) ** 2 + (yy - y0) ** 2).astype(np.float32)

    # Smoothstep transition for blur ramp
    t = (d - p.r0) / max(1e-6, (p.r1 - p.r0))
    t = np.clip(t, 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)

    sigma = p.sigma_max * np.power(t, p.p)

    idx1 = np.searchsorted(sigma_levels, sigma, side="right")
    idx1 = np.clip(idx1, 1, len(sigma_levels) - 1)
    idx0 = idx1 - 1

    s0 = sigma_levels[idx0]
    s1 = sigma_levels[idx1]
    alpha = (sigma - s0) / np.maximum(1e-6, (s1 - s0))

    out = stack[0].copy()
    for k in range(len(sigma_levels) - 1):
        mask = idx0 == k
        if not np.any(mask):
            continue
        a = alpha[mask][:, None]
        out[mask] = (1.0 - a) * stack[k][mask] + a * stack[k + 1][mask]

    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    img = rng.integers(0, 256, size=(240, 320, 3), dtype=np.uint8)
    params = FocusBlurParams(r0=40.0, r1=180.0, sigma_max=18.0, p=2.0, levels=10)
    for (x0, y0) in [(0, 0), (160, 120), (319, 239)]:
        out = apply_focus_blur_bgr(img, x0, y0, params)
        assert out.shape == img.shape and out.dtype == np.uint8
