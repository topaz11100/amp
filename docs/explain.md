# Implementation Explanation

이 문서는 `docs/Theory.md`에 제시된 이론 파이프라인이 실제 코드에서 어떻게 구현되어 있는지를 **처음 보는 사람도 따라올 수 있을 정도로 상세하게** 설명한다. 파이프라인 단계 번호와 섹션 번호는 `Theory.md`를 그대로 따른다.

## 전체 개요: Theory.md §0.2 파이프라인 고정 순서

코드는 `Theory.md §0.2`의 순서를 변형 없이 지킨다.

1. **sRGB 8-bit 입력** (`utils.decode_upload`) → **BGR uint8** 로드
2. **sRGB→linear 감마 제거** (`color_sim.srgb_to_linear_pow`, §4.1)
3. **domain shrink** (`color_sim._apply_domain_shrink`, Eq.(2), §4.5)
4. **RGB→LMS 변환** (`color_sim.simulate_vienot_deutan`, Eq.(4), §4.3)
5. **Viénot deutan 변환** (`color_sim.simulate_vienot_deutan`, Eq.(5), §4.4)
6. **LMS→RGB 역변환** (Eq.(4) 역행렬, §4.3)
7. **linear→sRGB 감마 복원** (`color_sim.linear_to_srgb_pow`, §4.1)
8. **(dog 전용) HSV 현상 강제** (`color_sim.dog_postprocess_hsv`, §6, §9A)
9. **(선택) 클릭 기반 초점/심도 블러** (`focus_blur.apply_focus_blur_bgr`, §7)
10. **표시·다운로드** (`app.py` + `utils.bgr_to_png_bytes`, §8)

모든 모듈이 이 순서를 전제로 작성되었으며, 감마 처리나 행렬 적용 순서를 바꾸지 않는다.

## 1. Color Simulation (`src/color_sim.py`)

### 1.1 데이터 흐름과 변환 순서 (Theory.md §4)

`simulate_vienot_deutan` 함수가 **BGR→RGB 정규화 → 감마 제거 → domain shrink → RGB→LMS → Viénot deutan → LMS→RGB → 감마 복원 → BGR** 흐름을 그대로 실행한다. 각 단계는 다음 이론 항목과 매핑된다.

- **감마 제거/복원 (§4.1)**: `srgb_to_linear_pow`와 `linear_to_srgb_pow`가 $R_s^\gamma$ 형태의 파워 감마(γ=2.2, Theory §9.1)를 적용한다. 선형 공간에서만 행렬 연산을 수행하기 위해 독립 함수로 분리했다.
- **domain shrink (Eq.(2), §4.5)**: `_apply_domain_shrink`가 $k\cdot x + b$를 선형 공간에서 적용하여 감마 후범위(Color clipping)를 줄인다. 계수(k=0.957237, b=0.0213814)는 Theory §9.1 수치를 그대로 사용한다.
- **RGB→LMS/역변환 (Eq.(4), §4.3)**: `M_rgb2lms` 행렬로 변환 후, 역행렬을 런타임에 `np.linalg.inv`로 계산하여 `M_lms2rgb`로 사용한다(Theory §9.2 “역행렬은 계산으로 얻는다” 원칙 반영).
- **Viénot deutan 변환 (Eq.(5), §4.4)**: `M_deutan_lms`를 `cv2.transform`에 적용해 M-원추 결손을 근사한다. 고양이(cat)도 이 동일한 deutan 변환을 사용한다(Theory §2.2, §5 근거).

### 1.2 매개변수 관리 (Theory.md §8.2, §9, §9A)

- `VienotDeutanParams`는 감마, domain shrink 계수, Viénot 행렬 상수(Theory §9.1)와 역행렬(§9.2)을 한 곳에 묶는다. 알고리즘 상수와 UI 파라미터가 섞이지 않도록 분리했다.
- `DogPostParams`는 **현상 강제용 HSV 파라미터**만 담는다. 이는 생리 상수가 아닌 “시각화 파라미터”이며 Theory §6, §9A(특히 §9A.4.2의 기본값)에서 정한 값을 기본으로 넣는다.
- `ColorSimParams`는 위 두 세트를 한 번에 전달하기 위한 래퍼다. `default_color_params`가 Theory에 명시된 기본값을 생성하며, UI에서 연구 모드일 때만 `DogPostParams`가 교체된다.

### 1.3 Dog HSV 후처리 (Theory.md §6, §9A)

`dog_postprocess_hsv`는 Viénot 결과를 받아 **(A) 청록대역 채도 감소 → (B) 2-hue 압축 → (C) 전체 채도 스케일**을 실행한다. Theory의 “현상 강제” 단계가 코드로 어떻게 내려오는지 각 항목별로 설명한다.

- **A. 청록 중립대(480nm 근방) 회색화**: `cyan_h0=100`, `cyan_sigma=12`(OpenCV Hue 단위)로 가우시안 가중치를 만들고 `cyan_desat=0.65`만큼 채도를 줄인다. 이는 Theory §6의 “blue-green 회색화” 요구와 §9A.2의 가우시안 형태 설계를 그대로 따른다.
- **B. 2-hue 압축**: Hue를 파란 군(`blue_h=120`)과 노란 군(`yellow_h=30`)으로 원형 보간(`_circular_lerp_hue`)해 끌어당긴다. `blue_cutoff=95` 기준으로 Hue를 둘로 나누며, 압축 정도는 `blue_compress=0.55`, `yellow_compress=0.40`으로 설정했다. 이는 Theory §6의 “blue/yellow 두 군”과 §9A.3의 보간식(§7.2 원형 보간)을 코드화한 부분이다.
- **C. 전체 채도 스케일**: `sat_global=0.85`로 후처리 아티팩트를 완화한다(Theory §9A.3.3). 값은 UI에서 노출되어 연구자는 조정 가능하다.

### 1.4 Cat 모드 처리 (Theory.md §2.2, §5)

`simulate_animal_color`에서 `animal == "cat"`일 경우 Viénot deutan 결과를 그대로 반환한다. Theory에서 고양이는 인간 deuteranope와 거의 동일하다고 정리했으므로(§2.2), HSV 현상 강제 없이 끝낸다.

### 1.5 BGR↔RGB 유틸리티와 자료형 처리

모든 외부 노출은 OpenCV 기본 형식인 **BGR uint8**로 유지한다. `_bgr_to_rgb01`/`_rgb01_to_bgr`가 float32 [0,1] 구간으로 정규화와 역정규화를 담당하여 감마 연산과 행렬 곱이 안전하게 작동하도록 한다.

## 2. Focus Blur (`src/focus_blur.py`)

### 2.1 알고리즘 개요 (Theory.md §7)

`apply_focus_blur_bgr`는 클릭 위치 `(x0, y0)`를 **초점면**으로 간주하고, 거리 기반으로 가우시안 시그마를 부여해 심도를 근사한다. Theory §7의 단계가 다음과 같이 대응된다.

1. **부드러운 전이(Smoothstep)**: 거리 `d`를 이용해 `r0→r1` 사이에서 $t^2(3-2t)$ 형태의 smoothstep을 적용한다(§7.1).
2. **거듭제곱 falloff**: `t^p`(기본 p=2.0)로 가중하여 배경 쪽에서 더 빨리 블러가 증가하도록 한다(§7.1).
3. **sigma 스케일**: `sigma_max`(기본 16)까지 선형 매핑하여 **공간가변 sigma(x,y)**를 얻는다.
4. **다중 sigma 가우시안 블렌딩**: `levels` 개의 사전 블러(또는 원본)를 준비하고, 각 픽셀마다 인접한 두 sigma 레벨을 선형 보간해 최종 값을 만든다(§7.3 “스택 블렌딩” 방식).

### 2.2 메모리 최적화 구현 세부

- **스트리밍 블렌딩**: 전체 블러 스택을 한 번에 메모리에 두지 않고, 이전/현재 블러 두 장만 유지하면서 `idx0/idx1` 마스크를 이용해 출력에 누적한다. 이는 Theory §7.3의 “메모리 폭증 방지” 취지를 그대로 코드로 옮긴 부분이다.
- **벡터화된 거리 계산**: `xx`, `yy` 1D 그리드를 사용해 `(H,W)` 거리 맵을 만든 뒤, 같은 버퍼(`t`, `sigma`)를 여러 단계에서 재사용하여 중간 배열 생성을 줄였다.
- **검증용 참조 구현**: `_reference_apply_focus_blur_bgr`는 작은 이미지에서만 쓰이는 완전 스택 버전이다. `__main__`에서 난수 테스트로 스트리밍 버전과 `atol=1` 오차 범위 내 일치함을 확인한다(회귀 테스트 용도).

## 3. Streamlit UI (`src/app.py`)

### 3.1 UI 흐름과 Theory 매핑 (Theory.md §8)

1. **업로드 (§0.2 단계 1)**: `st.file_uploader` → `utils.decode_upload`로 BGR 이미지를 확보한다.
2. **해상도 선택**: `resize_by_max_side`로 최대 변 길이를 960~2560 중 선택해 성능/품질을 조절하되, 내용 손실 없는 비율 스케일만 수행한다.
3. **동물 선택 & 연구 모드**: `selectbox`/`checkbox`로 dog/cat 선택과 파라미터 노출을 제공한다(Theory §8.4 “UI/파라미터 공개” 요구 충족).
4. **색 변환 실행**: `simulate_animal_color`를 스피너로 감싸 실행한다. 내부에서 위 1~8단계를 수행한다는 설명을 주석으로 명시하여 파이프라인 고정성을 강조했다.
5. **클릭 기반 초점/심도 (§7)**: `streamlit_image_coordinates`로 표시된 이미지 좌표를 받아, `resize_to_fit`가 계산한 `scale_x/scale_y`로 원본 해상도 좌표로 되돌린 뒤 `apply_focus_blur_bgr`를 호출한다. 이는 표시 해상도와 처리 해상도가 달라도 클릭 지점이 정확히 매핑되도록 하기 위한 조치다(Theory §7의 “초점 지점 일관성” 요구 충족).
6. **결과 표시 및 다운로드 (§0.2 단계 10)**: BGR → RGB 변환 후 `st.image`로 보여주고, `bgr_to_png_bytes`로 PNG 바이트를 생성해 `st.download_button`에 연결한다.

### 3.2 연구 모드 파라미터 노출 (Theory.md §8.4, §9A)

연구 모드에서만 HSV 후처리 파라미터 슬라이더를 열어, 논문 기본값과 사용자가 조정한 값이 명확히 구분된다. 이는 Theory의 “논문값 vs 튜닝값 구분, UI로 투명하게 공개” 요구사항을 충족한다.

### 3.3 표시 해상도 관리

`resize_to_fit`가 반환하는 스케일을 사용해 클릭 좌표를 원본으로 역투영하며, 화면 표시용 최대 크기(`DISPLAY_MAX_W/H`)는 성능을 위해 별도로 제한한다. 이는 이론적 알고리즘을 유지하면서도 UI 상호작용을 원활히 하는 순수 프론트엔드 최적화다.

## 4. Utilities (`src/utils.py`)

- **`decode_upload`**: 업로드된 파일을 `cv2.imdecode`로 읽어 BGR uint8을 얻는다. 이는 파이프라인 1단계(입력)와 직결되며 실패 시 명확한 오류 메시지를 던진다.
- **`resize_by_max_side`**: 가장 긴 변을 지정 길이에 맞추는 비율 스케일러로, 색 변환 전의 **내용 보존 리사이즈**만 수행한다(Theory §0.2의 “입력 정규화” 보조).
- **`resize_to_fit`**: 표시용 리사이즈와 함께 **표시↔원본 스케일 팩터**를 반환해 클릭 좌표가 정확히 매핑되도록 한다(Theory §7 UI 요구 충족).
- **`bgr_to_png_bytes`**: 최종 BGR 이미지를 PNG로 인코딩하여 다운로드 버튼에 전달한다. 처리 파이프라인과 독립된 I/O 유틸이지만 최종 단계(§0.2 “출력/다운로드”)를 담당한다.

## 5. 파라미터 출처와 재현성 (Theory.md §9, §9A)

- **Viénot 상수**: `M_rgb2lms`, `M_deutan_lms`, 감마 2.2, domain shrink 계수는 Theory §9.1의 수치를 그대로 코드에 하드코딩한다. `M_lms2rgb`는 Theory §9.2 지침에 따라 실행 시 역행렬을 계산한다.
- **Dog HSV 기본값**: Theory §9A.4.2에서 제안한 시각화 기본값을 `default_color_params`에 그대로 반영한다. UI 슬라이더에서 수정 시에도 `DogPostParams` 내부에만 영향이 있어, Viénot 선형 변환과 분리된 상태가 유지된다.
- **Defocus 파라미터**: Theory §7 권장값을 기본으로 넣고, 연구 모드에서만 사용자가 변경 가능하다. 기본값은 얕은 심도를 강조하는 `r0=0.15·min(H,W)`, `r1=0.6·hypot(H,W)`, `sigma_max=16`, `p=2`, `levels=12` 조합이다.

## 6. 확장 시 유의사항

- 이론 변경이 필요하면 **반드시 `docs/Theory.md`를 먼저 업데이트**하고, 그 후 코드와 본 설명서를 동기화해야 한다(모든 파일 상단 경고 주석과 동일한 정책).
- 새로운 후처리나 파라미터를 추가할 때는 “이론적 변환(행렬)”과 “시각화 후처리(HSV/블러)”가 구분된 현재 구조를 유지해야 한다. 이는 Theory §0.3에서 강조한 분리 원칙을 지키기 위함이다.
