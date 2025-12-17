# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
from __future__ import annotations

"""
Click-based defocus blur implementation following Theory.md §7.
"""

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

    # Precompute blur levels (Gaussian sigma list) without materializing a (levels,H,W,3) stack
    sigma_levels = np.linspace(0.0, p.sigma_max, p.levels, dtype=np.float32)

    # Distance from focus point using 1D grids to avoid large int64 meshes
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]

    dy = yy - float(y0)
    dy *= dy
    dx = xx - float(x0)
    dx *= dx

    d = dy + dx  # broadcasting (H, W)
    np.sqrt(d, out=d)

    # Smoothstep transition for blur ramp (in-place where possible)
    t = d  # reuse allocated distance array
    np.subtract(t, p.r0, out=t)
    np.divide(t, max(1e-6, (p.r1 - p.r0)), out=t)
    np.clip(t, 0.0, 1.0, out=t)
    t_orig = t.copy()
    np.multiply(t, t, out=t)  # t^2
    np.subtract(3.0, 2.0 * t_orig, out=t_orig)
    np.multiply(t, t_orig, out=t)  # t = t^2 * (3 - 2*t)

    np.power(t, p.p, out=t)
    np.multiply(t, p.sigma_max, out=t)
    sigma = t  # alias for readability

    idx1 = np.searchsorted(sigma_levels, sigma, side="right").astype(np.int16)
    np.clip(idx1, 1, len(sigma_levels) - 1, out=idx1)
    idx0 = (idx1 - 1).astype(np.int16)

    s0 = sigma_levels[idx0]
    s1 = sigma_levels[idx1]
    np.subtract(sigma, s0, out=sigma)  # reuse sigma for numerator
    np.subtract(s1, s0, out=s1)
    np.maximum(s1, 1e-6, out=s1)
    np.divide(sigma, s1, out=sigma)
    alpha = sigma  # alpha shares the same buffer as sigma

    # Streaming composition: keep only previous/current blur levels in memory
    base_f = bgr_u8.astype(np.float32)
    blur_prev = base_f if sigma_levels[0] <= 1e-6 else cv2.GaussianBlur(
        bgr_u8, (0, 0), sigmaX=float(sigma_levels[0]), sigmaY=float(sigma_levels[0])
    ).astype(np.float32)

    out = np.empty_like(base_f)
    for k in range(len(sigma_levels) - 1):
        sigma_k1 = sigma_levels[k + 1]
        blur_curr = (
            base_f
            if sigma_k1 <= 1e-6
            else cv2.GaussianBlur(
                bgr_u8, (0, 0), sigmaX=float(sigma_k1), sigmaY=float(sigma_k1)
            ).astype(np.float32)
        )

        mask = idx0 == k
        if np.any(mask):
            a = alpha[mask][:, None]
            out[mask] = (1.0 - a) * blur_prev[mask] + a * blur_curr[mask]
        blur_prev = blur_curr

    return np.clip(out, 0, 255).astype(np.uint8)


def _reference_apply_focus_blur_bgr(
    bgr_u8: np.ndarray, x0: int, y0: int, p: FocusBlurParams
) -> np.ndarray:
    """Reference implementation using a full blur stack.

    This is intentionally limited to small images for regression testing and is
    not imported elsewhere.
    """

    H, W = bgr_u8.shape[:2]
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

    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    d = np.sqrt((xx - x0) ** 2 + (yy - y0) ** 2).astype(np.float32)

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
    img = rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)
    params = FocusBlurParams(r0=10.0, r1=50.0, sigma_max=12.0, p=2.0, levels=6)
    for (x0, y0) in [(0, 0), (32, 32), (63, 63)]:
        out_stream = apply_focus_blur_bgr(img, x0, y0, params)
        out_ref = _reference_apply_focus_blur_bgr(img, x0, y0, params)
        assert out_stream.shape == img.shape and out_stream.dtype == np.uint8
        assert np.allclose(out_stream, out_ref, atol=1), "streaming blur diverged"
