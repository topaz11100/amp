# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
"""
Shared utilities for image I/O and resizing consistent with Theory.md pipeline philosophy.
"""
from __future__ import annotations

import cv2
import numpy as np


def decode_upload(file) -> np.ndarray:
    """Decode uploaded file bytes into BGR image (Theory.md §0.2 pipeline step 1)."""

    data = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("업로드한 파일을 읽을 수 없습니다. 파일이 손상되었거나 지원되지 않는 형식일 수 있습니다.")
    return img


def resize_by_max_side(bgr: np.ndarray, max_side: int) -> np.ndarray:
    """Resize keeping aspect ratio so that the longest side matches max_side."""

    h, w = bgr.shape[:2]
    scale = max_side / max(h, w)
    if scale >= 1.0:
        return bgr
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def bgr_to_png_bytes(bgr: np.ndarray) -> bytes:
    """Encode BGR uint8 image as PNG bytes for download."""

    success, buf = cv2.imencode(".png", bgr)
    if not success:
        raise ValueError("PNG encoding failed")
    return buf.tobytes()
