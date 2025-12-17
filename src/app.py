# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
"""
Streamlit entry point implementing UI specified in Theory.md §8.
"""
from __future__ import annotations

import numpy as np
import cv2
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from color_sim import ColorSimParams, DogPostParams, default_color_params, simulate_animal_color
from focus_blur import FocusBlurParams, apply_focus_blur_bgr
from utils import bgr_to_png_bytes, decode_upload, resize_by_max_side


st.title("개/고양이 시점 이미지 변환")

uploaded = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
if uploaded is None:
    st.stop()

bgr = None
try:
    bgr = decode_upload(uploaded)
except ValueError as e:
    st.error(str(e))
    st.stop()

if bgr is None:
    st.error("이미지를 불러오지 못했습니다.")
    st.stop()
H0, W0 = bgr.shape[:2]

max_side = st.select_slider("처리 해상도(긴 변)", options=[960, 1280, 1920, 2560], value=1280)
bgr = resize_by_max_side(bgr, max_side)

animal = st.selectbox("동물", ["dog", "cat"])
research_mode = st.checkbox("연구용 모드(파라미터 조절)", value=False)

params: ColorSimParams = default_color_params()

if research_mode and animal == "dog":
    st.subheader("Dog 후처리 파라미터(시각화 파라미터)")
    params.dog_post = DogPostParams(
        cyan_h0=st.slider("cyan_h0(H)", 0.0, 179.0, float(params.dog_post.cyan_h0)),
        cyan_sigma=st.slider("cyan_sigma", 1.0, 30.0, float(params.dog_post.cyan_sigma)),
        cyan_desat=st.slider("cyan_desat", 0.0, 1.0, float(params.dog_post.cyan_desat)),
        blue_h=st.slider("blue_h(H)", 0.0, 179.0, float(params.dog_post.blue_h)),
        yellow_h=st.slider("yellow_h(H)", 0.0, 179.0, float(params.dog_post.yellow_h)),
        blue_cutoff=st.slider("blue_cutoff(H)", 0.0, 179.0, float(params.dog_post.blue_cutoff)),
        blue_compress=st.slider("blue_compress", 0.0, 1.0, float(params.dog_post.blue_compress)),
        yellow_compress=st.slider("yellow_compress", 0.0, 1.0, float(params.dog_post.yellow_compress)),
        sat_global=st.slider("sat_global", 0.0, 1.0, float(params.dog_post.sat_global)),
    )

# 3) 색 변환 수행 (Theory.md §0.2, 단계 고정)
with st.spinner("색 변환(선형화→LMS→동물 시점) 계산 중…"):
    out = simulate_animal_color(bgr, animal, params)

# 4) 클릭 기반 초점/심도 (Theory.md §7)
rgb_disp = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
display_width = min(720, rgb_disp.shape[1])  # Fix: lock render width to avoid coordinate mismatch
st.caption("👇 이미지에서 초점을 맞출 위치를 클릭하세요")
coords = streamlit_image_coordinates(rgb_disp, key="img", width=display_width)

st.subheader("초점/심도(클릭 기반)")
H, W = out.shape[:2]
r0 = st.slider("초점 반경 r0", 0, min(H, W) // 2, int(0.15 * min(H, W)))
r1 = st.slider("블러 최대 도달 반경 (r1)", r0 + 1, int(np.hypot(H, W)), int(0.6 * np.hypot(H, W)))
sigma_max = st.slider("최대 blur sigma", 0.0, 30.0, 16.0)
pow_p = st.slider("blur falloff p", 1.0, 4.0, 2.0)
levels = st.slider("blur levels", 6, 20, 12)

if coords is not None:
    # streamlit-image-coordinates reports click in display space; map back to processed image space
    orig_w = float(coords.get("original_width", W)) or float(W)
    orig_h = float(coords.get("original_height", H)) or float(H)
    disp_w = float(coords.get("displayed_width", coords.get("width", display_width))) or float(display_width)
    disp_h = float(coords.get("displayed_height", coords.get("height", display_width * H / W))) or (display_width * H / W)
    scale_x = orig_w / disp_w
    scale_y = orig_h / disp_h
    x0 = int(np.clip(round(coords["x"] * scale_x), 0, W - 1))
    y0 = int(np.clip(round(coords["y"] * scale_y), 0, H - 1))
    blur_p = FocusBlurParams(
        r0=float(r0),
        r1=float(r1),
        sigma_max=float(sigma_max),
        p=float(pow_p),
        levels=int(levels),
    )
    with st.spinner("초점/심도 블러 합성 중… (다중 sigma 가우시안)"):
        out = apply_focus_blur_bgr(out, x0, y0, blur_p)

st.subheader("🖼️ Simulation Result")
st.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

png_bytes = bgr_to_png_bytes(out)
st.download_button("결과 다운로드 (PNG)", png_bytes, file_name="animal_view.png", mime="image/png")
