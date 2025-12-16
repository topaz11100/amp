# This file is implemented strictly based on docs/Theory.md
# Do not modify algorithms without updating Theory.md
"""
Streamlit entry point implementing UI specified in Theory.md §8.4.
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

bgr = decode_upload(uploaded)
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
out = simulate_animal_color(bgr, animal, params)

# 4) 클릭 기반 초점/심도 (Theory.md §7)
rgb_disp = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
coords = streamlit_image_coordinates(rgb_disp, key="img")

st.subheader("초점/심도(클릭 기반)")
H, W = out.shape[:2]
r0 = st.slider("초점 반경 r0", 0, min(H, W) // 2, int(0.15 * min(H, W)))
r1 = st.slider("블러 시작 r1", r0 + 1, int(np.hypot(H, W)), int(0.6 * np.hypot(H, W)))
sigma_max = st.slider("최대 blur sigma", 0.0, 30.0, 16.0)
pow_p = st.slider("blur falloff p", 1.0, 4.0, 2.0)
levels = st.slider("blur levels", 6, 20, 12)

if coords is not None:
    x0, y0 = int(coords["x"]), int(coords["y"])
    blur_p = FocusBlurParams(
        r0=float(r0),
        r1=float(r1),
        sigma_max=float(sigma_max),
        p=float(pow_p),
        levels=int(levels),
    )
    out = apply_focus_blur_bgr(out, x0, y0, blur_p)

st.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

png_bytes = bgr_to_png_bytes(out)
st.download_button("결과 다운로드 (PNG)", png_bytes, file_name="animal_view.png", mime="image/png")
