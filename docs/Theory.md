# 0. 한 줄 요약

입력 JPG/PNG(sRGB)을 받아서 (1) **개/고양이 이색형(dichromat) 색각**을 근사 시뮬레이션하고, (2) 사용자가 클릭한 지점을 **초점 중심**으로 두어 주변으로 갈수록 흐려지는 **공간가변(defocus) 블러**를 적용해 “동물 시점” 이미지를 출력한다.

---

# 1. 목표와 범위

## 1.1 목표(학부 과제 수준)

* 입력: 일반 사진 파일(png/jpg/jpeg)
* 출력:

  * **Dog mode**: 개 시점 색 변환 + (선택) 클릭 초점 블러
  * **Cat mode**: 고양이 시점 색 변환 + (선택) 클릭 초점 블러
* UI: Streamlit에서

  * 동물 선택(dog/cat)
  * 색 변환 옵션(가뭇 안정화, 강도)
  * 이미지 위 클릭으로 초점 지정
  * 초점 반경/블러 최대치 등 파라미터 슬라이더

## 1.2 핵심 아이디어

* 개/고양이는 **원추세포 종류가 2개**인 이색형(dichromat)으로 알려져 있으며(개: (Vision in dogs, 1995), 고양이: (Neutral point testing of color vision in the domestic cat, 2016)), 따라서 색 정보가 3차원(RGB/삼원색)에서 2차원(2-cone)으로 줄어든다.
* RGB→(근사)원추공간(LMS)→RGB로 색을 옮기는 틀을 쓰고, 이색형에서 **미정(undetermined)인 성분을 규칙으로 선택**해 시뮬레이션한다는 관점이 정식으로 제시되어 있다 (Brettel et al., 1997).
* 단일 이미지에는 거리(depth)가 없으므로 물리적으로 정확한 초점(DoF/defocus)을 복원할 수 없다. 대신 사용자의 클릭을 **초점면의 대리 변수(proxy)**로 두고, 렌즈 블러가 PSF(점확산함수)로 모델링된다는 사실(예: disc PSF, thin-lens 모델)을 배경으로 (Zhu & Milanfar, 2013), (Bae & Durand, 2007)에서 소개되는 방식과 일관되게 “공간가변 blur map”을 정의해 근사 적용한다.

---

# 2. 사용 논문과 “이 프로젝트에서 가져오는 것”

* (Vision in dogs, 1995):

  * 개가 이색형이라는 근거, 원추 피크(≈429–435nm, 555nm)와 중성점(neutral point) ≈475–485nm, 그리고 인간 deuteranopia와 유사하다는 서술을 **설계 근거**로 사용.
  * 개의 조절력(accommodation) 범위 2–3 diopters 및 diopter 정의(=1/f[m])를 **초점 제한**에 대한 배경 근거로 사용.
* (Neutral point testing of color vision in the domestic cat, 2016):

  * 고양이 이색형(dichromatic) 가능성, photopic receptor(≈560nm, 추가로 ≈460nm), 중성점이 인간 deuteranope와 유사하다는 서술을 **고양이 색 변환 근거**로 사용.
* (Brettel et al., 1997, Computerized simulation of color appearance for dichromats):

  * LMS(원추) 공간에서 색자극을 정의하고, dichromat에서 결손 성분이 **생리적으로 미정**임을 인정한 뒤, “어떤 규칙으로 그 성분을 선택할지”를 설계하는 것이 시뮬레이션의 핵심이라는 관점을 **색 변환 이론의 뼈대**로 사용.
* (Viénot et al., 1999):

  * 구현을 빠르고 안정적으로 만들기 위해, (Brettel 1997)의 아이디어를 기반으로 한 **선형 행렬 근사(예: deutan)**를 사용.
  * 감마 2.2 선형화, RGB→LMS 변환 행렬 수치, deutan LMS 변환 행렬 수치를 그대로 구현.
* (Image calibration and analysis toolbox…, 2017) / (QCPA…, 2018) / (Receptor noise…, 1998):

  * “카메라/조명/디스플레이 보정 없이는 RGB→cone-catch가 기기 의존적”이라는 한계를 **보고서의 가정/한계**로 명시.
* (Zhu & Milanfar, 2013) 및 (Bae & Durand, 2007):

  * defocus blur가 PSF로 모델링되며(예: disc/gaussian 근사), blur map(공간적으로 변하는 blur scale)을 다루는 관점이 표준적이라는 점을 **초점(블러) 설계의 배경 근거**로 사용.

---

# 3. 전체 처리 파이프라인(시스템 관점)

1. 파일 로드(png/jpg) → `BGR uint8`
2. (선택) 사용자 클릭 좌표 획득: `(x0, y0)`
3. 색 변환(동물 모드별):

   * `BGR uint8` → `RGB float32 [0,1]` → 감마 제거 → RGB→LMS → (dichromat 변환) → LMS→RGB → 감마 복원 → `BGR uint8`
4. (선택) 클릭 기반 초점 블러:

   * `blur map σ(x,y)` 생성 → 다중 블러 스택 생성 → σ에 따라 픽셀별 합성
5. 결과 출력(화면 표시 + 다운로드)

---

# 4. 색 변환(개/고양이) 이론 + 구현 스펙

## 4.1 설계 선택(학부 과제용)

* **핵심 가정**: 입력 이미지는 “표준 sRGB”라고 가정하고, RGB를 ‘근사 cone-space’로 옮길 때 표준 행렬을 사용한다.

  * 이는 엄밀한 물리 모델이 아니라 **시각화 목적의 근사**이며, 보정 필요성은 별도 문헌에서 경고된다는 점을 보고서에 명시한다 (Image calibration and analysis toolbox…, 2017).
* **시뮬레이터 선택**: 개/고양이 모두 “deutan(=M-cone 결손) 계열”을 기본으로 사용.

  * 고양이는 중성점이 인간 deuteranope와 유사하다는 근거가 있어 방어가 쉽다 (Neutral point testing…, 2016).
  * 개는 인간 deuteranopia와 유사하나 중성점이 약 480nm로 다르다 (Vision in dogs, 1995). 따라서 개 모드는 “deutan 시뮬레이션을 기본으로 하되, 선택적으로 추가 후처리(채도/청색 bias)를 두는” 형태로 설계한다(후처리는 휴리스틱으로 표기).

## 4.2 수식(논문 기반) — Viénot(1999) 선형 근사

### 4.2.1 감마 선형화

* 입력 `RGB_u8`를 `RGB_01 = RGB_u8 / 255`로 정규화한 후,
* 선형화(감마 제거):

  * `R = (R01)^{2.2}`, `G = (G01)^{2.2}`, `B = (B01)^{2.2}` (Viénot et al., 1999)

### 4.2.2 RGB → LMS

* [L,M,S]^T = M_RGB2LMS · [R,G,B]^T (Viénot et al., 1999)

`M_RGB2LMS`:

* [[17.8824, 43.5161, 4.11935],
  [3.45565, 27.1554, 3.86714],
  [0.0299566, 0.184309, 1.46709]] (Viénot et al., 1999)

### 4.2.3 dichromat(deutan) 변환(LMS 공간)

* deutan에서는 `M` 성분을 `L,S`의 선형결합으로 대체한다 (Viénot et al., 1999; 아이디어의 상위 근거는 Brettel et al., 1997).

[L_d, M_d, S_d]^T = M_DEUTAN_LMS · [L, M, S]^T

`M_DEUTAN_LMS`:

* [[1, 0, 0],
  [0.494207, 0, 1.24827],
  [0, 0, 1]] (Viénot et al., 1999)

### 4.2.4 LMS → RGB

* [R_d, G_d, B_d]^T = M_LMS2RGB · [L_d, M_d, S_d]^T
* `M_LMS2RGB = inv(M_RGB2LMS)` (역행렬은 구현에서 `np.linalg.inv`로 계산; 숫자를 하드코딩해도 됨)

### 4.2.5 감마 복원

* `RGB01_out = clip(RGB_lin_out, 0, 1)^(1/2.2)` (Viénot et al., 1999의 감마 가정과 일관)

### 4.2.6 (선택) 가뭇 안정화(입력 도메인 수축)

* 클리핑을 줄이기 위해 입력 선형 RGB를 affine하게 안쪽으로 수축:

  * `RGB_lin = 0.957237 * RGB_lin + 0.0213814` (Viénot et al., 1999)

## 4.3 색 변환 의사코드(구현 직결)

### 4.3.1 함수 시그니처

* `simulate_color(bgr_u8, mode: {'dog','cat'}, use_domain_shrink: bool, dog_extra_tune: dict) -> bgr_u8`

### 4.3.2 의사코드

```text
function simulate_color(bgr_u8, mode, use_domain_shrink, dog_extra_tune):
    rgb_u8 = BGR2RGB(bgr_u8)
    rgb01  = rgb_u8 / 255

    # gamma remove (Viénot 1999)
    rgb_lin = pow(rgb01, 2.2)

    if use_domain_shrink:
        rgb_lin = 0.957237 * rgb_lin + 0.0213814   # (Viénot 1999)

    # RGB -> LMS (Viénot 1999)
    lms = M_RGB2LMS * rgb_lin

    # Deutan dichromat simulation (Viénot 1999; principle in Brettel 1997)
    lms_d = M_DEUTAN_LMS * lms

    # LMS -> RGB
    rgb_d_lin = M_LMS2RGB * lms_d

    # Optional: dog-only heuristic tuning
    if mode == 'dog':
        rgb_d_lin = apply_dog_heuristic(rgb_d_lin, dog_extra_tune)
        # NOTE: heuristic; justify by neutral point shift & limited red-green discrimination (Vision in dogs 1995)

    rgb_d = pow(clip(rgb_d_lin, 0, 1), 1/2.2)

    out_bgr_u8 = RGB2BGR(round(rgb_d * 255))
    return out_bgr_u8
```

### 4.3.3 OpenCV API 매핑(색 변환)

* `BGR2RGB`: `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`
* `RGB2BGR`: `cv2.cvtColor(img, cv2.COLOR_RGB2BGR)`
* `M * img` (픽셀별 3×3 선형변환): `cv2.transform(img, M)`
* `clip`: `np.clip`
* `pow`: `np.power`

### 4.3.4 구현용 상수(그대로 복붙)

```python
M_RGB2LMS = np.array([
  [17.8824,   43.5161,   4.11935],
  [ 3.45565,  27.1554,   3.86714],
  [ 0.0299566, 0.184309, 1.46709]
], dtype=np.float32)  # (Viénot et al., 1999)

M_DEUTAN_LMS = np.array([
  [1.0,      0.0,     0.0],
  [0.494207, 0.0,     1.24827],
  [0.0,      0.0,     1.0]
], dtype=np.float32)  # (Viénot et al., 1999)

M_LMS2RGB = np.linalg.inv(M_RGB2LMS).astype(np.float32)  # inverse, computed in code
```

---

# 5. 클릭 기반 초점(Defocus) 근사: 이론 + 구현 스펙

## 5.1 물리 모델을 그대로 못 쓰는 이유(명시)

* 단일 사진은 픽셀별 거리(depth)가 없으므로, thin-lens 모델의 circle of confusion을 픽셀마다 정확히 계산할 수 없다.
* 따라서 과제 구현에서는 사용자의 클릭을 초점면의 대리로 두고, 화면상 거리(이미지 좌표 거리)에 기반해 blur map을 정의한다.
* 단, defocus blur를 PSF로 모델링하고(예: disc/gaussian 근사), 공간적으로 변하는 blur scale(blur map)을 다루는 접근 자체는 표준적인 관점이다 (Zhu & Milanfar, 2013), (Bae & Durand, 2007).

## 5.2 blur map 정의(과제용 휴리스틱)

### 5.2.1 거리 정의

* 클릭 좌표 `p0=(x0,y0)`
* 픽셀 `p=(x,y)`
* 화면상 거리(픽셀 단위):

  * `d(p)=sqrt((x-x0)^2 + (y-y0)^2)`

### 5.2.2 blur 강도 스케줄

* 파라미터:

  * `r0`: 초점 유지 반경(이 안은 선명)
  * `r1`: 최대 블러로 들어가는 반경(이 밖은 거의 최대)
  * `sigma_max`: 최대 가우시안 σ
  * `p`: 증가 곡선 지수(1~4)
* 정규화:

  * `t = clip((d-r0)/(r1-r0), 0, 1)`
* 매끄럽게(smoothstep):

  * `s = t*t*(3-2*t)`
* 최종 σ:

  * `σ(p) = sigma_max * (s^p)`

> 주의: 여기서 σ는 “렌즈 물리량”이 아니라 “가우시안 PSF의 스케일”이라는 공학적 파라미터이며, defocus를 PSF로 근사한다는 배경은 (Zhu & Milanfar, 2013), (Bae & Durand, 2007) 관점과 정렬된다.

## 5.3 공간가변 블러 구현(효율적 방법)

픽셀마다 다른 σ로 `GaussianBlur`를 직접 적용하면 매우 느리다.
따라서 다음 전략을 사용한다.

### 5.3.1 다중 블러 스택(Discrete σ levels)

* `levels = [0, 1, 2, 4, 8, 12, 16, 24]` 같은 몇 개의 σ를 선택
* 각 σ에 대해

  * `blur_k = GaussianBlur(img, sigma=levels[k])`
* 결과: `stack[k]` (N장의 블러 이미지)

### 5.3.2 blur map 기반 픽셀 합성

* 픽셀별 σ(p)를 계산
* σ(p)가 `[levels[i], levels[i+1])`에 속하면

  * `alpha = (σ - levels[i])/(levels[i+1]-levels[i])`
  * `out = (1-alpha)*stack[i] + alpha*stack[i+1]`

## 5.4 초점 블러 의사코드 + OpenCV 매핑

### 5.4.1 의사코드

```text
function apply_focus_blur(bgr_u8, x0, y0, r0, r1, sigma_max, p, levels):
    stack = []
    for s in levels:
        if s == 0:
            stack.append(bgr_u8)
        else:
            stack.append(GaussianBlur(bgr_u8, sigma=s))

    for each pixel p=(x,y):
        d = sqrt((x-x0)^2 + (y-y0)^2)
        t = clip((d-r0)/(r1-r0), 0, 1)
        s = smoothstep(t) = t*t*(3-2*t)
        sigma = sigma_max * (s^p)

        find i such that levels[i] <= sigma < levels[i+1]
        alpha = (sigma-levels[i])/(levels[i+1]-levels[i])
        out[p] = (1-alpha)*stack[i][p] + alpha*stack[i+1][p]

    return out
```

### 5.4.2 OpenCV API 매핑(초점 블러)

* `GaussianBlur(img, sigma=s)`: `cv2.GaussianBlur(img, ksize=(0,0), sigmaX=s, sigmaY=s)`
* 좌표 격자 생성: `yy,xx=np.mgrid[0:H,0:W]`
* 거리 계산/루트: `np.sqrt`
* 보간/합성: `numpy` 브로드캐스팅

---

# 6. Streamlit UI(클릭 입력) 구현 스펙

## 6.1 클릭 좌표 얻기

Streamlit 기본 `st.image`만으로는 클릭 좌표 이벤트가 부족하므로, 다음 중 하나를 사용한다.

* 권장(단순): `streamlit-image-coordinates`
* 대안(드래그/영역 선택): `streamlit-drawable-canvas`

## 6.2 UI 흐름 의사코드

```text
upload image
select animal: dog/cat
checkbox: domain_shrink
sliders: r0, r1, sigma_max, p
show image; get click (x0,y0)

img1 = simulate_color(bgr, animal, domain_shrink, dog_extra_tune)
if click exists:
    img2 = apply_focus_blur(img1, x0, y0, r0, r1, sigma_max, p)
else:
    img2 = img1

display img2, download
```

## 6.3 파일 로드(OpenCV)

* 업로드 바이트 → `np.frombuffer` → `cv2.imdecode(..., cv2.IMREAD_COLOR)`

---

# 7. 권장 기본 파라미터(학부 과제용)

## 7.1 색 변환

* `use_domain_shrink=True` (Viénot et al., 1999)
* `mode='cat'`: deutan 그대로
* `mode='dog'`: deutan 그대로 + (선택) `dog_extra_tune`(휴리스틱)

  * 예: `sat_scale=0.9`(채도 약간 감소), `blue_yellow_bias=+0.02` 등
  * 근거 표기는 “개가 deuteranopia와 유사하나 neutral point가 480nm로 이동” (Vision in dogs, 1995)로만 하고, 구체 튜닝은 ‘과제용 경험적 파라미터’로 명시

## 7.2 초점 블러

* `r0 = 0.15 * min(H,W)`
* `r1 = 0.60 * hypot(H,W)`
* `sigma_max = 16.0`
* `p = 2.0`
* `levels = [0,1,2,4,8,12,16,24]`

---

# 8. 구현 체크리스트(보고서/디버깅 관점)

## 8.1 색 변환 sanity check

* 회색(중립) 입력은 출력에서도 거의 회색 유지(중립 보존은 dichromat 시뮬레이션의 핵심 컨셉; Brettel 1997)
* R/G 대비가 큰 영역(예: 빨간 꽃/초록 잎)이 deutan에서 비슷하게 보이도록 변화
* 클리핑이 심하면 `use_domain_shrink` 켠다(Viénot 1999)

## 8.2 초점 블러 sanity check

* 클릭 지점 주변은 선명하고, 멀어질수록 부드럽게 흐려짐
* r0/r1 조절이 직관적으로 동작
* 성능: 스택 개수(레벨 수)를 6~10개로 제한

---

# 9. 한계(반드시 문서에 명시)

1. 입력이 일반 jpg/png이므로, 스펙트럼 기반 cone-catch를 직접 계산할 수 없고 표준 변환을 가정한다 (Brettel 1997의 적분 정의 + 보정 필요성: Image calibration toolbox 2017).
2. 단일 이미지에는 거리(depth)가 없으므로, 초점은 사용자 클릭을 이용한 휴리스틱 blur map으로 근사한다 (Zhu 2013, Bae&Durand 2007의 PSF/blur-map 관점에 기대).
3. 개/고양이 전용 cone fundamentals를 엄밀히 적용하지 않고, deutan 근사를 기본으로 사용한다(고양이는 neutral point 근거로 타당, 개는 유사하지만 중성점 차이 존재: Vision in dogs 1995).
