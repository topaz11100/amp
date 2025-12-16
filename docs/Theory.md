# 심전실 프로젝트 이론 문서(통합본): 인간 이미지를 개/고양이 시각으로 변환하기

본 문서는 다음 두 문서를 **내용을 삭제하지 않고** 하나의 마크다운 파일로 합친 통합본이다.

- 원문 1: `theory_expanded_professor_clean.md`
- 원문 2: `theory_filled_expanded.md`

통합본의 목적은 다음 두 가지를 동시에 만족시키는 것이다.

1) **프로젝트 파이프라인이 한눈에 드러나도록** ‘권장 읽기 순서(통합 정리판)’를 문서 맨 앞에 제공한다.
2) 사용자가 요구한 “내용은 절대로 줄이지 말 것”을 만족하기 위해, 두 원문의 본문을 **부록에 원문 그대로** 모두 포함한다.

작성일(로컬 기준): 2025-12-17

---

## 0. 통합 정리판(권장 읽기 순서)

### 0.1 한 장 요약: 이 프로젝트는 무엇을 재현하는가?

- 입력: 일반 사진(JPEG/PNG 등), 대개 **sRGB 8-bit 3채널**(구현에서는 OpenCV 관례에 따라 `BGR uint8`)
- 출력:
  - (1) **개(dog) 시점 변환 이미지**
  - (2) **고양이(cat) 시점 변환 이미지**
  - (선택) (3) **클릭 기반 초점/심도(Defocus) 효과**가 적용된 이미지
- 재현 목표(핵심):
  - dog: **이색형(dichromat) 기반의 색 붕괴 + ‘2-hue’ 경향 + 480nm 부근 neutral point + blue–green 회색화 경향**
  - cat: **이색형이며 인간 deuteranope와 매우 유사**(neutral point가 505nm라는 보고 포함)

> 주의: 입력이 스펙트럼(분광 반사율)이 아니라 “sRGB 3채널”이므로, 생물학적 시각을 ‘물리적으로 완전 복원’하는 것은 불가능하다. 본 프로젝트는 논문에서 정당화된 범위의 **시각화/근사 시뮬레이션**을 목표로 한다.

### 0.2 전체 처리 파이프라인(모듈 수준)

아래 순서는 **항상 고정**이다. 특히 감마(선형화) 순서를 바꾸면 색이 망가진다.

```text
[입력 이미지(sRGB, 8-bit)]
        |
        v
(1) sRGB → linear RGB (감마 제거)
        |
        v
(2) (선택) domain shrink / gamut 안정화
        |
        v
(3) linear RGB → LMS (원추 반응 공간)
        |
        v
(4) dichromat 시뮬레이션(LMS에서 차원 축소)
    - dog: deutan(=M 결손 근사) 기반 + dog 목표 현상에 맞춘 후처리
    - cat: deutan과 거의 동일한 축소(또는 cat 파라미터로 약간 이동)
        |
        v
(5) LMS → linear RGB → sRGB (표시/저장용)
        |
        v
(6) (dog 전용) HSV 기반 ‘현상 강제’ 후처리
        |
        v
(7) (선택) 클릭 기반 초점/심도(공간가변 defocus blur)
        |
        v
[출력/다운로드]
```

### 0.3 왜 “이론 변환(행렬)”과 “현상 강제(HSV)”를 분리하는가?

- **이론 변환(행렬)**: sRGB→linear→LMS→dichromat→RGB의 변환은 “색각 차원 축소”를 구현하는 **핵심 수학 단계**다.
- **현상 강제(HSV 후처리)**: dog 논문에서 말하는 “2-hue”, “cyan-blue-green이 gray로 붕괴” 같은 **인지적/현상적 관찰**은, 입력이 sRGB라는 한계 때문에 행렬만으로는 충분히 뚜렷하게 나타나지 않을 수 있다.  
  따라서 “과학적 정직성”을 유지하기 위해, (a) 논문 기반 수학 변환과 (b) 시각화 목적의 후처리를 **구분**해 설계한다.

### 0.4 교수님 데모용 최소 검증 체크포인트

1) **감마 순서 검증**: sRGB에서 바로 행렬곱을 하지 않고, 반드시 선형화 이후 LMS로 가는지  
2) **Neutral point 검증(정성)**: 특정 파장대/색 영역에서 회색화가 발생하는지(특히 dog 480nm 부근, cat 505nm 부근 서술과의 정합)  
3) **Dog 2-hue 현상 검증(정성)**: dog 모드에서 hue가 “대략 두 군”으로 뭉치는지  
4) **UI/파라미터 공개**: 후처리(HSV) 파라미터가 노출되어 사용자가 조절 가능하고, “논문값 vs 튜닝값”이 문서에 구분되어 있는지  
5) (선택) **Defocus 효과 검증**: 클릭 지점이 초점면이라는 UI 약속이 일관되게 적용되는지(전경/배경 분리 느낌)

---

## 1. 통합 본문(원문 보존형)

이 섹션부터는 두 원문을 부록에 그대로 싣되, 읽기 흐름이 깨지지 않도록 ‘원문 A/B’의 위치를 명확히 한다.

- **부록 A**: `theory_expanded_professor_clean.md` (원문 그대로)
- **부록 B**: `theory_filled_expanded.md` (원문 그대로)

실제 보고/제출 시에는 보통 **부록 B(확장·세부판)**이 가장 강력하며, 부록 A는 “한 장 요약 + 교수님용 흐름”이 좋다.

---

## 부록 A. 원문: theory_expanded_professor_clean.md

# 심전실 프로젝트 이론 문서(확장판): 인간 이미지를 개/고양이 시각으로 변환하기

본 문서는 “사람의 눈으로 본 세상(sRGB 사진)”을 입력으로 받아, **개(dog)** 또는 **고양이(cat)** 의 시각적 인상을 **비전(영상 처리)만으로** 재현하는 Streamlit 프로젝트의 이론적 근거와 구현 원리를, 처음 보는 사람도 따라올 수 있도록 단계별로 설명한다.

---

## 0. 전체 구현 개요(한 장 요약)

### 0.1 입력/출력
- 입력: 일반 사진(대부분 sRGB, 8-bit, 3채널) → 구현상 `BGR uint8`
- 출력: 동물 모드별 변환 이미지(선택적으로 클릭 기반 초점/심도 효과 포함)

### 0.2 파이프라인(모듈 수준)
아래 순서를 “항상 같은 방식으로” 적용한다. 이 순서가 바뀌면 색이 망가질 수 있다(특히 감마).

1) **입력 로드**: `BGR uint8`
2) **(색 변환) sRGB→선형→LMS→(이색형 시뮬레이션)→RGB→sRGB**
3) **(dog 전용) 현상 강제 후처리(HSV 기반)**
4) **(선택) 클릭 기반 초점/심도(공간가변 defocus blur)**
5) **표시/다운로드**

이 파이프라인은 기존 문서의 구현 관점 파이프라인과 동일하다.

### 0.3 “각 섹션이 프로젝트에서 맡는 역할”
- **(2. 생물학적 타깃 정의)**: “무엇을 재현해야 하는가?”를 논문 근거로 못 박는다.
  - dog: 2-hue(blue/yellow) + 480nm 근처 neutral point + blue-green이 gray로 보일 수 있음
  - cat: dichromat이며 neutral point가 505nm, 인간 deuteranope와 거의 동일
- **(3~5. 색 변환 수식)**: “어떻게 계산할 것인가?”를 고정한다(코드 직결).
  - 핵심 아이디어: dichromat는 원추(LMS) 3성분 중 1성분이 생리적으로 미정이므로, 그 성분을 어떤 규칙으로 채울지의 문제다
- **(6~7. dog 후처리/튜닝)**: dog 논문이 요구하는 ‘현상 제약’을 sRGB에서 강제하기 위한 공학적 단계다.
  - dog 논문은 파장대(430–475, 475–485, 500–620nm) 수준의 정성 제약을 제공한다
  - 그러나 입력은 sRGB 3채널이므로 픽셀에서 파장(nm)을 역산해 “그대로” 강제하는 것은 불가능하다
- **(8. 클릭 기반 defocus)**: 깊이(depth)가 없는 단일 사진에서, “초점면”을 사용자가 지정하게 해서 문제를 단순화한다
  - 광학적으로 심도/defocus는 렌즈·조리개·거리(CoC)에 의해 정해진다는 원리를 근거로 삼는다
  - 공간가변 blur map(=defocus map)로 얕은 심도를 근사하는 접근은 단일 이미지 기반 후처리 문헌에서도 일반적이다

---

## 1. 왜 “개/고양이 시각 변환”이 단순 필터가 아닌가?

### 1.1 핵심 난점: 입력이 스펙트럼이 아니라 “sRGB 3채널”이다
개/고양이의 시각은 본질적으로 “파장(λ)에 대한 원추 반응” 문제다. 하지만 우리가 가진 입력은 카메라가 이미 압축한 3채널(RGB)이며, 이는 **서로 다른 스펙트럼이 같은 RGB로 기록되는 메타머(metamer)** 문제가 있어 “파장 자체”를 복원할 수 없다. 그래서 **정밀 생리모델(파장 적분)을 그대로 구현하는 것은 원칙적으로 불가능**하며, 우리는 “정당한 근사”를 선택해야 한다.

### 1.2 그러면 무엇이 가능한가?
- (가능) **RGB→LMS 같은 선형 변환으로** “사람/표준 관측자의 원추 반응 공간”을 근사하고,
- (가능) **이색형(dichromat)** 조건을 만족하도록 “결손 원추 성분”을 규칙적으로 대체하여,
- (가능) 다시 RGB로 되돌려서 “사람이 보는 화면”에 렌더링한다.

이때 핵심 이론은 Brettel(1997)에서 명확히 말한다: dichromat에게는 LMS 3성분 중 하나가 **physiologically undetermined**이며, 그 값을 어떤 방식으로 “deliberately chosen”하여 정상 관측자에게 재현할지의 문제다.

---

## 2. 타깃(재현 목표) 정의: dog vs cat

### 2.1 개(dog): “2색상군 + cyan/blue-green 회색화 + 480nm neutral point”
Vision in dogs(1995)는 개가 2종류 원추를 갖는 이색형으로 요약되며, 대략 429–435nm와 555nm에 최대 감도가 있다고 설명한다.
또한 개의 가시 스펙트럼이 두 색상군으로 나뉘는 경향을 제시한다:

- 430–475nm: 개에게 blue로 보일 가능성
- 500–620nm: 개에게 yellow로 보일 가능성
- 475–485nm(blue-green): white/gray로 보일 수 있는 **spectral neutral point** 대역

그리고 사람의 deuteranopia와 유사하지만, 개의 neutral point가 480nm 쪽으로 이동해(사람 deuteranopia는 505nm) 차이가 난다고 명시한다.

**프로젝트 목표로 번역하면**:
- 하늘/바다/청록(cyan, blue-green) 계열이 **회색화되는 경향**이 드러나야 한다.
- 전체 색이 무지개처럼 다양한 것이 아니라 **blue 계열 vs yellow 계열** 두 덩어리로 뭉치는 경향이 보여야 한다.
- 회색 물체는 회색으로 남아야 한다(중요: “그냥 desaturation”이 아니다).

### 2.2 고양이(cat): “deuteranope와 거의 동일한 505nm neutral point”
Neutral point testing(2016)은 고양이가 두 photopic receptor(긴 파장 ~560nm, 짧은 파장 ~460nm)를 가져 dichromatic vision의 신경학적 기반이 있다는 기존 결과를 요약하고, 행동 실험으로 neutral point를 테스트한다.
실험 결과 두 고양이가 505nm에서만 일관되게 구별 실패하여, **neutral point가 505nm 근처**이며 고양이가 dichromatic일 강한 근거를 제공한다고 결론낸다.
또한 이 neutral point가 인간 deuteranope의 505nm와 거의 동일하다고 명시한다.

**프로젝트 목표로 번역하면**:
- “사람 deuteranopia 시뮬레이션”이 곧 “고양이의 색각 시뮬레이션”에 꽤 좋은 1차 근사가 된다.

---

## 3. 색 변환의 큰 그림: RGB가 아니라 LMS에서 작업하는 이유

### 3.1 LMS는 “원추 반응 공간”이다
Brettel(1997)은 색 자극을 LMS 공간 벡터로 나타내고, dichromat 시뮬레이션을 LMS 변환으로 표현한다.
이 관점이 중요한 이유는 다음과 같다.

- RGB는 “디스플레이 3원색의 혼합 비율”이라서, 생리적 의미가 직접적이지 않다.
- LMS는 “원추가 받은 자극(quantum catch)”에 가까운 표현이어서, 결손 원추(예: M 결손 deutan)를 수학적으로 다루기 쉽다.

### 3.2 dichromat 시뮬레이션은 ‘정보 차원 축소’ 문제다
정상 시각은 3차원(L,M,S) 색공간을 쓰지만, dichromat는 두 원추만으로 구분하므로 2차원 색공간으로 축소된다.
즉, 어떤 색들은 “구분 불가능한 같은 색”으로 붕괴한다. 이것이 우리가 만들고 싶은 효과의 본질이다.

---

## 4. 색 변환 알고리즘(코드 직결): sRGB→LMS→deutan→RGB

> 여기서는 “수식이 왜 필요한지”를 설명하고, 바로 구현 가능한 형태로 정리한다.
> 고양이 모드(cat)는 아래 deutan 변환만 적용한다(§2.2 근거).

### 4.1 감마 처리: sRGB를 선형으로 바꾸는 이유
행렬 곱(선형 변환)은 **선형 광도 공간**에서 의미가 있다. 그런데 sRGB 값은 대체로 감마가 적용된 비선형 값이다.
따라서 다음을 한다.

- 정규화: $R_s,G_s,B_s\in[0,1]$
- 선형화(근사):
  $$R=R_s^{\gamma},\quad G=G_s^{\gamma},\quad B=B_s^{\gamma}$$
  여기서 $\gamma\approx2.2$ 를 사용한다(구현 단순화).

※ 엄밀한 sRGB는 piecewise 감마이지만, 본 프로젝트는 논문 기반 행렬 파이프라인을 단순 파워 감마로 구현해도 “시각적 목적”에 충분하도록 설계했다(실무에서도 흔한 선택).

### 4.2 Linear RGB → LMS
선형화된 RGB 벡터 $\mathbf{r}=[R,G,B]^T$를 LMS로 보내는 선형 변환을 사용한다.

$$
\begin{bmatrix}L\\M\\S\end{bmatrix}
=
\mathbf{M}_{RGB\to LMS}
\begin{bmatrix}R\\G\\B\end{bmatrix}
$$

프로젝트 구현에서는 다음 수치를 사용한다(코드 하드코딩).

### 4.3 deutan 변환(LMS에서 ‘M 결손’ 근사)
deuteranopia(deutan)는 M 원추 성분이 효과적으로 결손된 상황으로 볼 수 있다. 따라서 $M$ 성분을 $L,S$의 조합으로 대체하는 형태의 선형 근사를 사용한다.

$$
\begin{bmatrix}L_d\\M_d\\S_d\end{bmatrix}
=
\mathbf{M}_{deutan}
\begin{bmatrix}L\\M\\S\end{bmatrix}
$$

구현에서는 다음 형태(두 번째 행이 $L,S$로 $M_d$를 재구성)를 사용한다.

### 4.4 LMS → Linear RGB (역변환)
화면에 다시 그리려면 RGB로 돌아와야 한다. 원칙은 역행렬이다.

$$
\begin{bmatrix}R'\\G'\\B'\end{bmatrix}
=
\mathbf{M}_{LMS\to RGB}
\begin{bmatrix}L_d\\M_d\\S_d\end{bmatrix},
\quad
\mathbf{M}_{LMS\to RGB}=\mathbf{M}_{RGB\to LMS}^{-1}
$$

프로젝트는 역행렬을 코드에서 계산한다.

### 4.5 gamut 안정화(domain shrink)의 필요성
행렬 변환을 거치면 $R',G',B'$가 $[0,1]$ 범위를 벗어나는 경우가 흔하다(클리핑 발생).
클리핑은 색 왜곡(특히 채도/명도 깨짐)을 강하게 유발하므로, 입력 선형 RGB에 affine shrink를 적용해 범위를 줄여주는 실무적 안정화가 필요하다. 프로젝트는 다음 형태를 사용한다.

$$
\mathbf{r}\leftarrow k\mathbf{r}+b,\quad (k=0.957237,\ b=0.0213814)
$$

### 4.6 선형 → sRGB(감마 복원)
$$
R_s'=\operatorname{clip}(R',0,1)^{1/\gamma}
$$
$G_s',B_s'$도 동일.

---

## 5. 왜 “cat = deutan만”이 합리적인가?

cat 모드를 단순화할 수 있는 핵심 근거는 **neutral point의 일치**다. 고양이는 505nm 근처에서 neutral point를 보이고, 이는 인간 deuteranope의 505nm와 거의 동일하다고 명시된다.
즉, “사람 deuteranopia 시뮬레이션(=deutan)”을 적용하면 고양이의 색각 저차원화(붕괴) 패턴과 상당히 부합할 가능성이 높다.

---

## 6. 왜 “dog는 deutan만으로 부족”하고 HSV 후처리가 필요한가?

### 6.1 dog의 neutral point는 480nm대(사람 deuteranopia는 505nm)
Vision in dogs(1995)는 개의 neutral point가 475–485nm(약 480nm)로 “파란 쪽으로 이동”해 있고, 사람 deuteranopia의 neutral point(505nm)와 다르다고 직접 비교한다.
따라서 **cat처럼 “그냥 deutan”으로 끝내면**, dog가 보여야 하는 “blue-green 회색화” 위치가 맞지 않을 수 있다.

### 6.2 dog 논문이 제공하는 것은 ‘현상 제약’이지 ‘sRGB에서의 정확한 파라미터’가 아니다
dog 논문은 430–475nm는 blue, 500–620nm는 yellow, 475–485nm는 gray/white 가능 등 **파장대 기반 정성 제약**을 준다.
하지만 우리의 입력은 sRGB이므로, 픽셀별 “파장”을 직접 알 수 없다.
그래서 프로젝트는 다음과 같이 정직하게 선을 긋는다:

- **정량(논문 수치)**: deutan 선형 변환(행렬, shrink, 감마 흐름)
- **정성(논문 현상)**: HSV에서 “cyan 회색화”와 “2-hue 강제”를 재현하는 시각화 파라미터

이 구조 자체가 프로젝트의 설계 철학(“정직한 근사”)이다.

---

## 7. dog HSV 후처리의 구현 원리(수식/파라미터가 의미하는 것)

dog 모드는 다음 두 단계를 합친다.
1) base: deutan 시뮬레이션(정량)
2) post: dog 현상 강제(정성)

### 7.1 단계 A: cyan(blue-green) 대역 채도 감소 → gray에 가깝게
HSV에서 Hue를 $H$, Saturation을 $S$라고 하자. “cyan 중심 hue”를 $H_0$로 잡고, 그 주변에서만 채도를 누른다.

- 거리: $d_H=\min(|H-H_0|,180-|H-H_0|)$ (원형 hue 거리)
- 가중치(가우시안 윈도우):
  $$w(H)=\exp\left(-\frac{d_H^2}{2\sigma^2}\right)$$
- 채도 감소:
  $$S\leftarrow S\cdot (1-\alpha\, w(H))$$

여기서
- $H_0$는 “dog의 neutral point가 blue-green 쪽(480nm)으로 이동한다”는 서술을 sRGB hue로 옮긴 중심값이다.
- $\sigma$는 “475–485nm 대역이 회색화될 수 있다”는 ‘대역 폭’을 HSV에서 근사한 값이다.
- $\alpha$는 회색화 강도(채도 억제율)이다.

코드 구조는 실제로 위와 동일한 형태를 쓴다.

### 7.2 단계 B: 2-hue 강제(blue / yellow) = Hue “압축”
dog 논문은 스펙트럼이 두 색상군(blue vs yellow)으로 요약되는 경향을 말한다.
이를 HSV에서 다음처럼 구현한다.

- 임계값 $H_c$로 “blue 쪽”과 “yellow 쪽”을 나눈다.
- 각 영역의 hue를 목표 hue($H_b$ 또는 $H_y$)로 당긴다(affine pull):

$$
H\leftarrow (1-\beta)H+\beta H_{target}
$$

$H_{target}$은 blue 영역에서는 $H_b$, yellow 영역에서는 $H_y$이며,
$\beta$가 클수록 더 강하게 “두 덩어리”로 뭉친다.

이 역시 코드가 그대로 구현하고 있다.

### 7.3 단계 C: 전역 채도 스케일(전체 과포화 억제)
“2-hue로 뭉치게 하는 압력”은 종종 인공적인 색을 만든다. 이를 완화하려고 전역 채도 스케일 $s_g$를 곱한다.

$$S\leftarrow s_g\,S$$

---

## 8. dog HSV 파라미터를 ‘논문 문장’을 만족하도록 튜닝하는 절차(프로토콜)

> 목표: “감으로 숫자 맞추기”가 아니라, **논문이 요구한 현상 제약을 만족시키도록** 재현 가능한 과정을 문서화한다.

### 8.1 dog 논문에서 가져온 ‘필수 제약 3개’
1) 2-hue 경향: 430–475nm는 blue, 500–620nm는 yellow
2) cyan/blue-green neutral band: 475–485nm는 white/gray 가능
3) neutral point shift: dog neutral point는 480nm 쪽, 사람 deuteranopia는 505nm

### 8.2 튜닝용 테스트 입력(최소 세트)
- **Hue Wheel**(색상환): 2-hue로 붕괴하는지 확인
- **Spectrum Strip**(좌→우로 hue가 연속 변화): cyan 대역 회색화 위치/폭 확인
- **Gray Ramp**(검정→흰색): 회색이 색으로 오염되지 않는지 확인

(선택) 자연 이미지 3장: 하늘/바다, 잔디/숲, 사람 얼굴(피부 톤)

### 8.3 정량 점검(간단하지만 재현 가능)
정량 지표는 “완벽한 생리 정량”이 아니라, **현상 제약 충족 여부**를 자동화하기 위한 체크다.

#### (A) Gray 보존 검사(필수)
Gray Ramp 입력(각 픽셀 $R=G=B$)에 대해 출력에서
$$\Delta_{gray}=\max(|R'-G'|,|G'-B'|,|B'-R'|)$$
가 작은지(예: 평균이 임계값 이하) 확인한다.

#### (B) Cyan 회색화 검사(필수)
자연 이미지 또는 Spectrum Strip에서, cyan 후보 픽셀 집합 $\Omega_{cyan}$를
- 입력 HSV에서 $|H-H_0|\leq\sigma$로 정의한 뒤,
출력의 평균 채도 $\mathbb{E}[S'|\Omega_{cyan}]$가 충분히 낮아지는지 확인한다.

#### (C) 2-hue 붕괴 검사(필수)
Hue Wheel 출력의 hue 히스토그램이 (1) blue 근처, (2) yellow 근처 두 봉우리로 몰리는지 확인한다.
- 단순 기준: 출력 hue의 분산이 크게 줄고, K-means($K=2$) 중심이 $(H_b,H_y)$ 근처로 수렴.

### 8.4 튜닝 순서(권장)
1) **A(Gray 보존)** 먼저 맞춘다. (안 맞으면 다 무의미)
2) 그다음 **A( cyan 회색화 )**로 $H_0,\sigma,\alpha$를 조정한다.
3) 마지막으로 **B(2-hue)**로 $H_c,H_b,H_y,\beta_{blue},\beta_{yellow}$를 조정한다.
4) 최종적으로 전역 채도 $s_g$로 과한 인공 느낌을 줄인다.

### 8.5 시작점(기본값 예시)
프로젝트 문서에 포함된 시작점 예시를 그대로 사용해도 된다.
다만 이 값은 생리 상수가 아니라 “시각화 파라미터”이며, 위 프로토콜로 재현 가능하게 고정해야 한다.

---

## 9. 클릭 기반 초점/심도(공간가변 defocus blur): 왜 필요한가, 왜 이 방식인가?

### 9.1 광학적 정당성: 심도는 렌즈/조리개/거리에서 나온다
Potmesil & Chakravarty(1981)는 핀홀 카메라 대신 렌즈·조리개를 포함한 모델을 소개하며, 임의 평면에 포커싱하고 depth of field를 포함한 합성 이미지를 생성할 수 있음을 말한다.
즉, “심도/defocus”는 물리적으로 매우 타당한 지각 요소다.

### 9.2 단일 사진의 한계와 UI 설계 선택
단일 사진에는 깊이 정보가 없으므로, 광학식을 그대로 적용할 수 없다. 그래서 프로젝트는 **사용자 클릭을 초점면 지정**으로 해석한다.
이 선택은 “정밀 depth 추정”을 회피하면서도, 사용자에게 직관적인 제어를 제공한다.

### 9.3 blur map(σ 맵) 정의: 구현 단순 + 안정성
클릭 좌표 $(x_0,y_0)$로부터의 거리
$$d(x,y)=\sqrt{(x-x_0)^2+(y-y_0)^2}$$
를 이용해, $r_0$(초점 유지 반경), $r_1$(블러 시작 반경)을 둔다.

- 정규화:
$$t=\operatorname{clip}\left(\frac{d-r_0}{r_1-r_0},0,1\right)$$
- smoothstep:
$$t\leftarrow t^2(3-2t)$$
- sigma 맵:
$$\sigma(x,y)=\sigma_{max}\,t^p$$

이 방식은 “물리적 CoC”를 그대로 쓰지 않지만, “초점에서 멀수록 blur가 커진다”는 구조를 안정적으로 재현한다.

### 9.4 이 접근이 논문적으로 납득되는 이유
Bae & Durand(2007)은 단일 이미지에서 공간가변 blur 양을 나타내는 **defocus map**을 추정하고, 그 맵을 이용해 out-of-focus는 더 blur, in-focus는 유지하는 방식으로 얕은 심도를 시뮬레이션한다.
또한 이들은 “정밀 depth 추정이 필요하지 않다”고 분명히 한다.
즉, 프로젝트의 blur map 방식은 “정밀 광학 복원”이 아니라 “지각적 효과 재현”을 목표로 하는 합리적 선택이다.

추가로 Zhu et al.(2013)은 defocus PSF가 단일 스케일 파라미터로 요약될 수 있고, 그 스케일의 2D 맵을 **defocus blur map**이라 부르며, 단일 이미지에서 blur map을 추정하는 것이 중요한 응용을 가진다고 정리한다.
프로젝트는 “추정”까지는 하지 않고 “클릭으로 지정”하지만, blur map을 핵심 표현으로 쓰는 점은 같은 계열이다.

---

## 10. 구현 관점(코드 구조와 이론의 연결)

### 10.1 핵심 함수 2개
- `simulate_vienot_deutan(bgr_u8, params)`
  - §4의 파이프라인(감마→RGB2LMS→deutan→LMS2RGB→감마 복원)을 수행
- `dog_postprocess_hsv(bgr_u8, dog_post_params)`
  - §7의 A/B/C( cyan 회색화 + 2-hue 압축 + 전역 채도 스케일 ) 수행

최종 선택 로직은 다음처럼 “cat은 base만, dog는 base+post”로 단순하다.

### 10.2 Streamlit UI와의 연결
- dog 파라미터는 슬라이더로 노출되어 실험 프로토콜(§8)을 따라 튜닝 가능하다.
- 초점/심도도 r0,r1,sigma_max,p,levels를 슬라이더로 제어한다.

---

## 11. 한계와 “정직한” 해석(교수님에게 꼭 말해야 하는 부분)

1) **스펙트럼 복원이 불가능**: 입력이 sRGB이므로 nm 기반 모델을 그대로 적용할 수 없다.
2) **dog 후처리는 생리 상수가 아니다**: 논문 현상을 sRGB에서 재현하기 위한 시각화 파라미터다.
3) **defocus는 클릭 기반 근사**: 실제 depth를 추정하지 않는다(대신 사용자 지정).
4) **시뮬레이션의 목적은 지각적 납득(qualitative)**: Brettel(1997)도 “타인의 감각을 완전히 확신할 수는 없지만” 시뮬레이션이 residual color information을 정량화·시각화하는 수단이라고 말한다.

---

## 12. 참고문헌(프로젝트 파일 기반)
- Vision in dogs (JAVMA, 1995)
- Neutral point testing of color vision in the domestic cat (Exp. Eye Research, 2016)
- Brettel et al., Computerized simulation of color appearance for dichromats (JOSA A, 1997)
- Potmesil & Chakravarty, A lens and aperture camera model for synthetic image generation (SIGGRAPH, 1981)
- Bae & Durand, Defocus Magnification (Eurographics, 2007)
- Zhu et al., Estimating Spatially Varying Defocus Blur From A Single Image (IEEE TIP, 2013)

---

## 부록 B. 원문: theory_filled_expanded.md

# A. 프로젝트 구현 개괄(처음 읽는 사람용)

## A.1 이 프로젝트가 “무엇을, 어떻게” 하는가

**목표:** 사람에게 보이는 일반 사진(스마트폰/카메라로 찍은 sRGB 이미지)을 입력으로 받아, **개/고양이의 시각 체계에서 “색이 어떻게 붕괴(collapse)되는지”**를 보여주는 변환 결과를 출력한다.

- 입력: JPEG/PNG 등 일반 이미지(대부분 sRGB, 8-bit)
- 출력: (1) 개 시점 색 변환 이미지, (2) 고양이 시점 색 변환 이미지  
  옵션: (3) 클릭 기반 초점/심도(Defocus) 효과를 적용한 이미지
- 핵심 원리(요약):
  1. **색 공간 선형화(sRGB→linear)**: 선형 조합(행렬곱)이 의미 있게 동작하도록, 먼저 감마를 제거해 선형 영역으로 변환한다.
  2. **감마/범위 보정(domain shrink)**: 변환 후 값이 0~1을 넘거나 음수가 되는 것을 완화하기 위해, 선형 RGB에서 affine 축소를 한 번 적용한다.
  3. **RGB→LMS→(dichromat)→LMS→RGB**: 색각 모델링에서 표준적으로 쓰는 “원추세포(cone) 신호 공간(LMS)”에서, **dichromat(2-원추) 시각의 색 붕괴**를 선형 근사한다.
  4. **(개 전용) HSV 기반 현상 강제(post-process)**: 논문에서 서술하는 “2-hue(blue/yellow)”와 “blue–green 중립대(gray)” 같은 현상을, 사용자에게 더 분명히 보이도록 후처리로 강화한다.
  5. **(선택) 클릭 기반 Defocus**: 단일 이미지에서 실제 깊이를 복원하는 대신, “사용자 클릭=초점면 지정”이라는 UI 약속으로 심도감을 제공한다.

> 이 문서는 “과학적 정직성” 관점에서, (a) 논문에서 직접 수치를 가져온 부분과 (b) 구현/시각화 목적의 근사·튜닝 파라미터를 분리해 설명한다. (기존 문서의 #9, #9A를 핵심으로 삼음)

---

## A.2 한 장으로 보는 전체 처리 파이프라인

```text
[입력 이미지(sRGB, 8-bit)]
        |
        | (성능) 리사이즈/형식 통일
        v
[색 변환(고정 알고리즘)]
  1) BGR->RGB, [0,1] 정규화
  2) sRGB -> linear (감마 제거)
  3) domain shrink (선형 RGB에서 affine 축소)
  4) RGB -> LMS (원추세포 공간)
  5) dichromat 근사 (LMS에서 색 정보 축소)
  6) LMS -> RGB
  7) linear -> sRGB (감마 복원)
        |
        | (개 모드일 때만)
        v
[Dog HSV 후처리(현상 강제)]
  - cyan 대역 desaturate(중립대 강화)
  - blue/yellow로 hue compress(2-hue 강화)
  - global saturation 스케일(과도한 인공색 억제)
        |
        | (선택)
        v
[초점/심도(클릭 기반)]
  - 클릭 좌표를 기준으로 공간가변 σ(x,y) 맵 생성
  - Gaussian blur stack + 픽셀별 보간
        |
        v
[출력/시각화(Streamlit)]
```

---

## A.3 “이론 변환(행렬)”과 “현상 강제(HSV)”를 분리하는 이유

- **행렬 기반 변환**은, dichromat 시각의 “색 정보 차원 축소”라는 핵심을 가장 직접적으로 구현한다.  
  (LMS에서 한 축을 잃어 “confusion line”으로 붕괴하는 구조를 갖기 때문)
- 하지만 현실 사진(sRGB, 비선형, 장면 조명/카메라/화이트밸런스에 의존)에서는, 논문 서술의 현상이 **사용자에게 충분히 선명하게 드러나지 않을 수 있다.**
- 그래서 본 프로젝트는:
  - **(정당한) 생물학적 핵심:** dichromacy에 의한 색 붕괴(행렬)
  - **(정직한) 시각화 강화:** 2-hue/neutral-band 같은 “관찰 서술”을 만족하도록 보정(HSV 튜닝)
  를 **서로 다른 레이어로** 구현한다.

---

## A.4 문서 섹션이 프로젝트에서 맡는 역할(읽는 순서 가이드)

| 문서 섹션 | 프로젝트에서의 역할 | 구현 파일/함수(대표) |
|---|---|---|
| #1 | 목표/범위/가정 정의(무엇을 안/하는지) | 보고서 전반(요구사항) |
| #2 | “왜 이런 변환이 필요한가” 생물학적 근거 제시 | 논문 근거(개/고양이) |
| #3 | 데이터 플로우/모듈 경계 정의(구현 설계) | app.py, color_sim.py, focus_blur.py |
| #4 | 색 변환의 논리(왜 LMS/왜 deutan 근사/왜 후처리) | color_sim.py |
| #5 | 바로 구현 가능한 수식/연산 순서(테스트 기준) | color_sim.py |
| #6 | dog HSV 후처리 설계(현상 강제) | color_sim.py (dog_postprocess_hsv) |
| #7 | Defocus 설계(클릭 기반 UI 약속 + 근사) | focus_blur.py (apply_focus_blur_bgr) |
| #8 | 코드 구조/파라미터 인수화(재현성) | dataclass Params + 함수 시그니처 |
| #9/#9A | 논문 수치 vs 경험 파라미터의 출처를 “정직하게” 구분 | 파라미터 문서화/튜닝 프로토콜 |
| #10 | 품질/성능 체크(디버깅 체크리스트) | 테스트/리그레션 |
| #11 | 참고문헌 목록(추적 가능성) | 보고서/발표 자료 |

---

## A.5 논문이 “어느 단계의 정당성”을 담당하는가

| 논문 | 이 프로젝트에서 정당화하는 것 | 연결되는 구현 요소 |
|---|---|---|
| Vision in dogs (1995) | 개의 dichromacy, 2-hue(blue/yellow) 서술, blue–green 중립대/neutral point 서술 | dog HSV 후처리의 목표 제약(2-hue, cyan-gray) + 튜닝 프로토콜 |
| Neutral point testing of color vision in the domestic cat (2016) | 고양이의 색각 특성(중립점/비구분 영역)과 “deuteranope 유사성” 근거 | 고양이 색 변환에서 deutan 근사 채택의 정당성(1차 근사) |
| PHOTOPIC SPECTRAL SENSITIVITY OF THE CAT (1987) | 고양이 원추세포(photopic) 분광 민감도/피크의 실험 근거 | 고양이 모델링이 “인간 삼원색”이 아니라 “원추 민감도”를 따라야 함을 설명 |
| Brettel et al. (1997) | dichromat 색 모사의 핵심 개념: 혼동선(confusion line), 중립색 유지, 자극 공간의 축소 | LMS 공간에서 색 차원 축소(행렬)라는 설계 철학 |
| Potmesil & Chakravarty (1981) | 렌즈/조리개로 인한 depth of field, circle of confusion 등 “광학적 defocus” 개념 | 클릭 기반 Defocus의 “원리 설명” 및 한계 정당화 |
| Bae & Durand (2007), Zhu et al. (2013) | 단일 이미지에서 공간가변 blur(blur map/defocus map) 추정 또는 조절의 연구 흐름 | 향후 확장(자동 blur map) 또는 현 설계(σ 맵 + 레벨 스택)의 정당화 |
| Troscianko & Stevens (2017), QCPA (2018/2020) | **정량적 animal vision 모델링은 보정/선형화/스펙트럼 정보가 필요**하다는 방법론적 경고 | “우리는 질적 시각화”라는 범위 정의 + 향후 RAW/보정 파이프라인 로드맵 |

---

## A.6 최소 검증(교수님 데모용) 체크포인트

- **중립색 보존:** 회색/흰색/검정은 변환 전후에도 “색이 크게 끼지” 않아야 한다(특히 post-process 이후).
- **색 붕괴의 방향성:** 빨강-초록 계열이 유사해지고, 파랑-노랑 축이 상대적으로 강조되는 경향이 관찰돼야 한다(질적 관찰).
- **클리핑 억제:** 특정 채널이 0 또는 255에 과도하게 붙으면 domain shrink 계수/후처리 압력이 과한 신호로 본다.
- **파라미터 재현성:** 슬라이더로 튜닝한 파라미터를 그대로 dataclass 기본값으로 고정할 수 있어야 한다(실험 재현성).

---



---

# 0. 외부 평가 요약 및 반영 내역

> **이 섹션의 역할:** 외부 피드백(“이론 설명 부족” 등)을 어떤 방식으로 문서/설계에 반영했는지 추적 가능하게 남긴다.  
> **프로젝트 가치:** 교수님/심사자 관점에서 “요구사항-수정-근거”의 연결이 보이며, 문서 신뢰도가 올라간다.

## 0.1 외부 평가(요약)

* 문서의 논리(논문 기반 값 vs 추정/경험값 구분, 근사에 대한 정직한 서술)가 강점으로 평가됨.
* 구현 착수는 가능하나, **UI 예시 코드가 2개 버전(고정/가변)이 섞여 충돌**하는 문제가 지적됨.
* 권장 수정: `연구용 모드` 토글을 두고, 토글 여부에 따라 **파라미터 UI(슬라이더) 노출**만 달라지게 하되, 내부 처리는 하나의 코드 경로로 통일.

## 0.2 이번 수정에서 반영한 핵심

* 문서 전체를 하나로 정리하고, **UI(app.py) 코드를 1개 버전으로 통일**.
* “고정식 구현”을 제거하고, 색/후처리/블러 파라미터는 전부 **함수 인수(파라미터 객체)로 전달**하도록 설계.
* 단, **각 동물의 ‘변환 방법(알고리즘)’ 자체는 1개로 고정**:

  * `cat`: Viénot et al.(1999) deutan 선형 시뮬레이션
  * `dog`: Viénot et al.(1999) deutan 선형 시뮬레이션 + (Vision in dogs, 1995)에서 서술된 현상(2-hue + blue-green 중립대역)을 재현하는 후처리

---

# 1. 프로젝트 목표 및 범위

> **이 섹션의 역할:** 프로젝트가 **무엇을 하는지/안 하는지**를 명확히 해, 이후 근사(approximation)가 ‘범위 밖 문제 회피’인지 ‘정당한 단순화’인지 판단할 기준선을 제공한다.

## 1.1 목표(학부 과제 수준)

* 입력: 일반 사진(png/jpg/jpeg, sRGB 가정)
* 출력: 선택한 동물(dog/cat) 시점의 근사 변환 이미지

  * 색 변환(동물 모드별)
  * (선택) 사용자 클릭 기반 초점/심도(Defocus) 근사
* UI(Streamlit):

  * 동물 선택(dog/cat)
  * 연구용 모드 토글(파라미터 슬라이더 노출)
  * 이미지 클릭으로 초점 지정
  * 결과 이미지 표시 및 다운로드

## 1.2 범위/가정

## 1.3 정확도 레벨(‘질적 시각화’와 ‘정량 시각 모델’의 구분)

이 프로젝트는 **질적(qualitative) 시각화 도구**를 목표로 한다. 그 이유는 다음과 같다.

- 일반 사진(JPEG/PNG)은 사람에게 보기 좋도록 **비선형 톤 커브/감마/화이트밸런스/색보정**을 거친 결과물이다. 이런 이미지는 장면의 실제 방사휘도(radiance)에 선형적으로 비례하지 않기 때문에, 그대로는 **정량적 색/반사율 측정**에 부적합하다.
- 동물 시각 모델(특히 cone-catch 기반)을 **정량적으로** 적용하려면, (1) RAW 기반 선형화, (2) 조명 보정(그레이 스탠더드), (3) 카메라 분광 민감도, (4) 목표 동물의 원추 민감도 등의 정보가 필요하다.

따라서 본 프로젝트는:
- “논문 기반 생물학적 사실(예: dichromacy, neutral band)”을 **관찰 가능한 방향으로** 반영하되,
- RAW/보정/분광까지 포함한 엄밀한 cone-catch 재현은 **향후 확장**으로 둔다.

(이 구분은 #9에서 파라미터 출처를 ‘정직하게’ 나누는 구조와 연결된다.)


* 단일 sRGB 이미지로는 분광 정보(파장별 반사율)를 알 수 없으므로, **정밀 cone-catch 적분 기반 모델은 목표가 아님** (Troscianko & Stevens, 2017; QCPA 관련 프레임워크 문헌).
* 초점/심도는 원래 거리(depth), 조리개(aperture), 렌즈 모델에 의존하지만, 단일 이미지에는 depth가 없으므로 **클릭 기반 공간가변 블러(blur map)**로 근사한다 (Potmesil & Chakravarty, 1981; Bae & Durand, 2007; Zhu & Milanfar, 2013).

---

# 2. 논문 기반 생물학적 근거(왜 dog/cat 변환이 필요한가)

> **이 섹션의 역할:** “왜 이런 변환이 타당한가?”라는 질문에 대해, 개/고양이 시각 연구의 실험적 결론을 근거로 **변환 목표(현상 제약)**를 정의한다.

## 2.1 개(Dog)

* 개는 2종류 원추를 가진 이색형(dichromat)으로 요약되며, 원추 최대감도는 대략 429–435nm 및 555nm로 서술됨 (Vision in dogs, 1995).
* 개의 spectral neutral point는 475–485nm(약 480nm)로 제시되며, 인간 deuteranopia와 유사하지만 neutral point 위치가 다르다고 명시됨 (Vision in dogs, 1995).
* 개는 430–475nm 구간이 ‘blue’, 500–620nm 구간이 ‘yellow’로 보이는 2-hue 성격을 보이며, 475–485nm(blue-green)은 white/gray로 보일 수 있고 greenish-blue를 gray와 구분하지 못할 수 있다고 서술됨 (Vision in dogs, 1995).

## 2.2 고양이(Cat)

* 고양이도 이색형(dichromat)일 가능성이 높으며, photopic receptor가 장파장(≈550–560nm) 및 단파장(≈450–460nm) 근처로 제시됨 (Neutral point testing of color vision in the domestic cat, 2016; Loop et al., 1987).
* 고양이 neutral point는 505nm이며 이는 인간 deuteranope neutral point(505nm)와 거의 동일하다고 명시됨 (Neutral point testing…, 2016).

---

## 2.3 “논문 문장”을 “구현 제약”으로 바꾸는 번역 규칙(중요)

논문은 보통 “480nm 근처는 중립(gray)로 보인다”, “두 가지 hue로 주로 지각된다”처럼 **현상(phenomenology)**을 서술한다.  
하지만 입력 데이터는 **sRGB 사진**이므로, 픽셀 하나가 “몇 nm의 단색광”인지로 역변환할 수 없다(메타머리즘, 카메라·조명 의존).

그래서 본 프로젝트는 다음과 같은 **번역 규칙**을 채택한다.

1. **현상 기반 제약을 정의한다.**  
   - (예) “blue–green 영역은 채도가 낮아져 회색에 가까워진다(중립대)”  
   - (예) “대부분의 색이 blue 또는 yellow 축으로 뭉친다(2-hue)”
2. **제약을 만족하는 ‘관찰 가능한 지표’를 만든다.**  
   - (예) 특정 hue 구간에서 평균 채도 $\bar S$가 충분히 작아야 한다.  
   - (예) hue 분포가 두 개의 모드(blue/yellow)로 수렴해야 한다.
3. **행렬 변환(이론) + HSV 후처리(시각화)로 역할을 분리한다.**  
   - 행렬: dichromacy에 의한 색 차원 축소(핵심 이론)  
   - HSV: 위 제약이 사용자에게 분명히 드러나도록 강화(근사/튜닝)

이 번역 규칙이 #9A의 튜닝 프로토콜로 이어진다.


# 3. 시스템 파이프라인(구현 관점)

> **이 섹션의 역할:** 논문 아이디어를 실제 코드/UX로 옮기는 과정에서, 데이터 플로우·모듈 경계·파라미터화 전략을 명확히 한다.  
> **핵심 메시지:** (1) 색 변환은 순수 함수(파라미터 인수 기반)로 고정, (2) 조절은 파라미터만 바꿔 재현 가능하게 한다.

1. 이미지 로드(png/jpg) → `BGR uint8`
2. (선택) UI 클릭 좌표 획득 `(x0,y0)`
3. 색 변환(동물 모드별)
4. (선택) 클릭 기반 초점/심도 근사(공간가변 blur)
5. 출력 표시 및 다운로드

---

# 4. 색 변환 설계(논문 기반 + 구현 가능한 근사)

> **이 섹션의 역할:** “왜 이 수식/파라미터를 적용해야 하는가”의 논리 중심축.  
> **핵심 메시지:** (a) dichromacy는 색 정보 차원 축소 문제이며(LMS에서 구현), (b) 현실 이미지에서는 후처리로 관찰 현상을 강화해야 한다.

## 4.1 핵심 아이디어

* dichromat 시뮬레이션은 “결손 원추 성분이 미정(undetermined)”이라는 점을 인정하고, 어떤 규칙으로 그 성분을 선택/대체할지 설계하는 문제라는 관점이 제시됨 (Brettel et al., 1997).
* 본 과제는 구현 안정성과 단순성을 위해, Brettel(1997) 계열 아이디어를 선형 근사로 제공하는 **Viénot et al.(1999) deutan**을 기반 변환으로 채택한다.

## 4.2 Dog/Cat 변환 방법(알고리즘) 고정

* `cat`: Viénot(1999) deutan 선형 시뮬레이션만 적용

  * 정당화: cat neutral point(505nm) ≈ deuteranope(505nm) (Neutral point testing…, 2016)
* `dog`: Viénot(1999) deutan 선형 시뮬레이션 + dog 현상 강제 후처리

  * 정당화: dog는 neutral point가 480nm대로 이동하고, 2-hue(blue/yellow) 및 blue-green 중립대역(gray) 성질을 보인다는 서술 (Vision in dogs, 1995)

> 중요: dog 후처리는 “정밀 생리 모델의 수치”가 아니라, 논문이 제공하는 ‘현상 제약’을 sRGB 색공간에서 재현하기 위한 공학적 후처리이며, 선정 절차는 9A에서 정당화한다.

---

## 4.3 왜 ‘RGB→LMS’인가? (핵심 배경을 아주 쉽게)

- 디지털 이미지는 보통 RGB 3채널이지만, 이것은 **디스플레이/카메라 표준**에 맞춘 좌표계다.
- 생물의 망막은 RGB가 아니라, 원추세포(cone)의 분광 민감도에 따른 **LMS(장파/중파/단파)** 신호로 광을 샘플링한다.
- 따라서 “동물 시각”을 이야기하려면, 최소한 한 번은 **원추 기반 좌표계(LMS)**로 옮겨서 생각해야 한다.

특히 dichromat(2-원추)에서는:
- 어떤 한 원추 채널이 없거나, 두 채널만 의미 있게 남는다.
- 결과적으로 색 자극 공간이 3D에서 2D로 줄어들고, 서로 다른 색이 같은 지각으로 **붕괴**한다(혼동선/혼동면 개념).

이 프로젝트의 행렬 기반 변환은, 바로 이 “차원 축소”를 구현하는 장치다.

## 4.4 Brettel 계열 dichromat 시뮬레이션의 직관(왜 ‘confusion line’이 나오나)

dichromat는 한 종류의 원추 입력이 없기 때문에, 어떤 방향의 색 변화는 구분할 수 없다.  
그래서 원래는 다른 스펙트럼이더라도, 남아 있는 두 원추의 반응이 동일해지면 같은 색으로 보인다.

이때 “구분 불가능한 변화 방향”이 **confusion line**으로 나타난다.  
즉, 다양한 원색이 특정 선(또는 면)으로 투영되며, 최종적으로는 **자극 공간이 축소(reduced stimulus surface)**된다.

본 프로젝트에서는 Brettel의 핵심 개념을 “LMS 공간에서의 선형 연산”으로 단순화하여 구현한다(구현 편의 + OpenCV 행렬 연산과의 정합성).

## 4.5 domain shrink를 왜 선형 RGB에서 먼저 하느냐(실무적 이유)

LMS 변환과 dichromat 근사를 거치면, 수학적으로는 다음이 쉽게 발생한다.
- $R,G,B$ 중 하나가 0보다 작아지거나, 1보다 커짐(색역 밖)
- 그 결과 8-bit로 돌아갈 때 클리핑이 많아져, 색이 “띠”처럼 깨지거나(밴딩) 과도한 영역 포화가 발생

이를 완화하려면 “어디에선가” 스케일을 줄여야 하는데,
- 감마가 적용된 sRGB 영역에서 줄이면 밝기·채도 관계가 비선형이라 부작용이 크다.
- 따라서 **선형 RGB에서 affine 축소(domain shrink)**를 먼저 하고, 이후 LMS 변환을 수행한다.

이 설계는 #5의 수식 순서(선형화→shrink→행렬)로 고정되며, #10 체크리스트로 검증한다.


# 5. 색 변환 수식(바로 구현용)

> **이 섹션의 역할:** 구현자가 그대로 옮겨도 동일 결과가 나오도록, 연산 순서와 수식을 ‘코드 직결’ 형태로 고정한다.

## 5.1 sRGB → 선형(감마 제거)

* 근사: `linear = srgb ** 2.2` (Viénot et al., 1999 구현 가정)

## 5.2 Linear RGB → LMS (Viénot et al., 1999, Eq.(4))

[
\begin{bmatrix}L\M\S\end{bmatrix}
=================================

\begin{bmatrix}
17.8824 & 43.5161 & 4.11935\
3.45565 & 27.1554 & 3.86714\
0.0299566 & 0.184309 & 1.46709
\end{bmatrix}
\begin{bmatrix}R\G\B\end{bmatrix}
]

## 5.3 deutan 변환(LMS, Viénot et al., 1999, Eq.(5))

[
\begin{bmatrix}L_d\M_d\S_d\end{bmatrix}
=======================================

\begin{bmatrix}
1 & 0 & 0\
0.494207 & 0 & 1.24827\
0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}L\M\S\end{bmatrix}
]

## 5.4 LMS → Linear RGB

* 원칙: `M_LMS2RGB = inv(M_RGB2LMS)` (Viénot 1999에서 역변환 원칙)
* 구현에서는 역행렬을 코드에서 계산하거나, 재현 가능한 계산값을 하드코딩한다.

## 5.5 gamut 안정화(입력 affine shrink, Viénot et al., 1999, Eq.(2))

* deutan에서 입력 선형 RGB에 다음을 적용(클리핑 완화):

  * `RGB_lin = 0.957237 * RGB_lin + 0.0213814`

## 5.6 선형 → sRGB(감마 복원)

* `srgb = clip(linear,0,1) ** (1/2.2)`

---

# 6. dog 후처리(현상 강제형) 설계

> **이 섹션의 역할:** 논문 서술(2-hue, neutral band)을 UI에서 분명히 보이도록 만드는 **시각화 레이어**를 정의한다.  
> **주의:** 여기의 파라미터는 “생리값”이 아니라 “현상 만족을 위한 시각화 튜닝값”이다(#9A에서 절차로 정당화).

## 6.1 dog 논문이 제공하는 ‘현상 제약’

* 430–475nm → blue
* 500–620nm → yellow
* 475–485nm(blue-green) → white/gray(중립대역) 가능, greenish-blue를 gray와 구분 못할 수 있음
* neutral point가 480nm대로 이동
  (위 서술: Vision in dogs, 1995)

## 6.2 sRGB에서의 구현 전략

* nm→픽셀 파장 역변환이 불가능하므로, 색공간(HSV/Lab 등)에서 대역을 정의하여 현상을 재현한다.
* 본 과제는 구현 단순성을 위해 HSV 기반 후처리를 사용:

  1. cyan(blue-green) 근처의 채도를 감소시켜 gray에 가까워지게 함(중립대역)
  2. hue를 ‘blue 목표’와 ‘yellow 목표’ 쪽으로 압축하여 2-hue 성질을 강화

> 주의: HSV hue는 파장과 1:1이 아니다. 따라서 아래 수치는 생리 상수가 아니라 “현상 재현용 시각화 파라미터”이며 9A의 절차로 고정한다.

---

# 7. 클릭 기반 초점/심도(Defocus) 설계

> **이 섹션의 역할:** 색 변환만으로 부족한 “동물 시각의 흐릿함/공간 해상도 차이”를, 단일 이미지 제약 하에서 UI 친화적으로 보여주는 방법을 정의한다.

## 7.1 왜 클릭 기반인가?

* 광학적으로 defocus blur는 렌즈/조리개/거리(CoC)에 의해 결정됨 (Potmesil & Chakravarty, 1981).
* 단일 사진에는 depth가 없으므로 물리 모델을 그대로 적용할 수 없다.
* 따라서 “사용자 클릭 = 초점면 지정”이라는 UI 약속으로 문제를 단순화하고, 공간가변 blur map으로 구현한다.

## 7.2 blur map(σ 맵) 정의

* 클릭 좌표 `(x0,y0)`
* 거리 `d(x,y) = sqrt((x-x0)^2 + (y-y0)^2)`
* `t = clip((d-r0)/(r1-r0), 0, 1)`
* `t = t^2 (3-2t)` (smoothstep)
* `σ(x,y) = σ_max * t^p`

## 7.3 빠른 구현(블러 스택 + 픽셀 보간)

* 여러 sigma 레벨로 미리 `GaussianBlur` 결과를 만들고
* 각 픽셀의 sigma에 맞춰 인접한 두 레벨을 선형 보간

---

## 7.4 논문 모델과 본 프로젝트 근사의 대응(정당화)

**논문에서의 defocus(광학):**
- 렌즈/조리개/초점거리/피사체 거리로 인해, 초점면에서 벗어난 점상이 원반(circle of confusion) 형태로 퍼진다.
- 결과적으로 장면에는 깊이(depth of field)가 생기고, 시선 유도(중요 부위 강조) 같은 효과를 준다.

**본 프로젝트에서의 제약:**
- 단일 사진에는 깊이 정보가 없다.
- 따라서 “물리적으로 정확한 CoC 반경”을 픽셀마다 계산할 수 없다.

**그래서 우리가 채택한 근사:**
- 사용자 클릭으로 초점면을 지정하고,
- 클릭점에서 멀어질수록 blur가 커지는 $\sigma(x,y)$ 맵을 만든 뒤,
- 공간가변 블러를 빠르게 합성한다.

이 접근은 “물리 기반 모델(존재하는 현상)”을 “단일 이미지 UI(가능한 상호작용)”로 번역한 것이다.  
향후에는 Bae & Durand(Defocus Magnification) 또는 Zhu et al.(spatially varying defocus blur estimation) 계열처럼, 이미지에서 blur map을 자동 추정하는 방향으로 확장할 수 있다(그러나 계산량·구현 난이도가 상승).


# 8. 구현 코드(함수는 모두 ‘파라미터 인수’ 기반)

> **이 섹션의 역할:** 코드를 ‘재현 가능한 실험 장치’로 만들기 위한 설계.  
> **핵심 메시지:** 슬라이더는 실험 UI일 뿐이며, 최종 결과는 파라미터(dataclass)로 고정 가능해야 한다.

## 8.1 requirements.txt(권장)

* streamlit
* numpy
* opencv-python-headless (서버/배포)
* streamlit-image-coordinates

## 8.2 color_sim.py

```python
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class VienotDeutanParams:
    gamma: float
    # Eq.(2)
    domain_shrink_k: float
    domain_shrink_b: float
    # Eq.(4)
    M_rgb2lms: np.ndarray  # (3,3)
    # Eq.(5)
    M_deutan_lms: np.ndarray  # (3,3)
    # inv(Eq.(4))
    M_lms2rgb: np.ndarray  # (3,3)


@dataclass
class DogPostParams:
    # HSV 기반 현상 강제 파라미터(시각화 파라미터)
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
    vienot: VienotDeutanParams
    dog_post: DogPostParams


def srgb_to_linear_pow(rgb01: np.ndarray, gamma: float) -> np.ndarray:
    return np.power(np.clip(rgb01, 0.0, 1.0), gamma, dtype=np.float32)


def linear_to_srgb_pow(lin01: np.ndarray, gamma: float) -> np.ndarray:
    return np.power(np.clip(lin01, 0.0, 1.0), 1.0 / gamma, dtype=np.float32)


def simulate_vienot_deutan(bgr_u8: np.ndarray, p: VienotDeutanParams) -> np.ndarray:
    # BGR->RGB, [0,1]
    rgb01 = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # sRGB -> linear
    rgb_lin = srgb_to_linear_pow(rgb01, p.gamma)

    # domain shrink (Eq.(2))
    rgb_lin = p.domain_shrink_k * rgb_lin + p.domain_shrink_b

    # RGB->LMS (Eq.(4))
    lms = cv2.transform(rgb_lin, p.M_rgb2lms)

    # deutan (Eq.(5))
    lms_d = cv2.transform(lms, p.M_deutan_lms)

    # LMS->RGB
    rgb_d_lin = cv2.transform(lms_d, p.M_lms2rgb)

    # linear -> sRGB
    rgb_d = linear_to_srgb_pow(rgb_d_lin, p.gamma)

    out_bgr = cv2.cvtColor((rgb_d * 255.0 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)
    return out_bgr


def dog_postprocess_hsv(bgr_u8: np.ndarray, p: DogPostParams) -> np.ndarray:
    hsv = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # (A) cyan(blue-green) 대역 채도 감소 -> gray에 가깝게
    dh = np.minimum(np.abs(H - p.cyan_h0), 180.0 - np.abs(H - p.cyan_h0))
    w = np.exp(-(dh * dh) / (2.0 * p.cyan_sigma * p.cyan_sigma))
    S = S * (1.0 - p.cyan_desat * w)

    # (B) 2-hue 강제(blue / yellow)
    is_blue = (H >= p.blue_cutoff)
    H2 = H.copy()
    H2[is_blue] = (1.0 - p.blue_compress) * H[is_blue] + p.blue_compress * p.blue_h
    H2[~is_blue] = (1.0 - p.yellow_compress) * H[~is_blue] + p.yellow_compress * p.yellow_h

    # (C) 전체 채도 소폭 감소
    S2 = np.clip(S * p.sat_global, 0.0, 255.0)

    hsv2 = np.stack([np.clip(H2, 0.0, 179.0), S2, V], axis=-1).astype(np.uint8)
    return cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)


def simulate_animal_color(bgr_u8: np.ndarray, animal: str, p: ColorSimParams) -> np.ndarray:
    base = simulate_vienot_deutan(bgr_u8, p.vienot)

    if animal == "cat":
        # cat: deutan만 적용 (Neutral point testing…, 2016)
        return base

    if animal == "dog":
        # dog: deutan + 현상 강제 후처리 (Vision in dogs, 1995)
        return dog_postprocess_hsv(base, p.dog_post)

    raise ValueError("animal must be 'cat' or 'dog'")


def default_color_params() -> ColorSimParams:
    # Viénot(1999) 값(논문 수치)
    M_rgb2lms = np.array([
        [17.8824,    43.5161,    4.11935],
        [ 3.45565,   27.1554,    3.86714],
        [ 0.0299566,  0.184309,  1.46709],
    ], dtype=np.float32)

    M_deutan = np.array([
        [1.0,      0.0,     0.0],
        [0.494207, 0.0,     1.24827],
        [0.0,      0.0,     1.0],
    ], dtype=np.float32)

    M_lms2rgb = np.linalg.inv(M_rgb2lms).astype(np.float32)

    vienot = VienotDeutanParams(
        gamma=2.2,
        domain_shrink_k=0.957237,
        domain_shrink_b=0.0213814,
        M_rgb2lms=M_rgb2lms,
        M_deutan_lms=M_deutan,
        M_lms2rgb=M_lms2rgb,
    )

    # dog 후처리 기본값(시각화 파라미터): 보고서 9A의 절차로 확정한 값을 여기에 넣는다.
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
```

## 8.3 focus_blur.py

```python
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class FocusBlurParams:
    r0: float
    r1: float
    sigma_max: float
    p: float
    levels: int


def apply_focus_blur_bgr(bgr_u8: np.ndarray, x0: int, y0: int, p: FocusBlurParams) -> np.ndarray:
    H, W = bgr_u8.shape[:2]

    # blur levels
    sigma_levels = np.linspace(0.0, p.sigma_max, p.levels, dtype=np.float32)

    # stack
    stack = []
    for s in sigma_levels:
        if s <= 1e-6:
            stack.append(bgr_u8.astype(np.float32))
        else:
            stack.append(cv2.GaussianBlur(bgr_u8, (0, 0), sigmaX=float(s), sigmaY=float(s)).astype(np.float32))
    stack = np.stack(stack, axis=0)  # (N,H,W,3)

    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - x0) ** 2 + (yy - y0) ** 2).astype(np.float32)

    t = (d - p.r0) / max(1e-6, (p.r1 - p.r0))
    t = np.clip(t, 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)  # smoothstep

    sigma = p.sigma_max * np.power(t, p.p)

    idx1 = np.searchsorted(sigma_levels, sigma, side="right")
    idx1 = np.clip(idx1, 1, len(sigma_levels) - 1)
    idx0 = idx1 - 1

    s0 = sigma_levels[idx0]
    s1 = sigma_levels[idx1]
    alpha = (sigma - s0) / np.maximum(1e-6, (s1 - s0))
    alpha3 = alpha[..., None]

    out = stack[0].copy()
    for k in range(len(sigma_levels) - 1):
        mask = (idx0 == k)
        if not np.any(mask):
            continue
        m = mask[..., None]
        out[m] = (1.0 - alpha3[m]) * stack[k][m] + alpha3[m] * stack[k + 1][m]

    return np.clip(out, 0, 255).astype(np.uint8)
```

## 8.4 app.py(단일 버전, 연구용 모드 토글)

```python
import streamlit as st
import numpy as np
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

from color_sim import default_color_params, simulate_animal_color, DogPostParams
from focus_blur import FocusBlurParams, apply_focus_blur_bgr


def decode_upload(uploaded_file):
    data = np.frombuffer(uploaded_file.read(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


st.title("개/고양이 시점 이미지 변환")

uploaded = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
if uploaded is None:
    st.stop()

bgr = decode_upload(uploaded)
H0, W0 = bgr.shape[:2]

# 성능 팁: 큰 이미지는 리사이즈(긴 변 기준)
max_side = st.select_slider("처리 해상도(긴 변)", options=[960, 1280, 1920, 2560], value=1280)
scale = max_side / max(H0, W0)
if scale < 1.0:
    bgr = cv2.resize(bgr, (int(W0 * scale), int(H0 * scale)), interpolation=cv2.INTER_AREA)

animal = st.selectbox("동물", ["dog", "cat"])
research_mode = st.checkbox("연구용 모드(파라미터 조절)", value=False)

# 1) 기본 파라미터 로드(함수 인수 기반)
params = default_color_params()

# 2) 연구용 모드일 때만 dog 후처리 파라미터 조절(하지만 함수는 항상 인수 기반)
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

# 3) 색 변환(고정 알고리즘, 인수 기반)
out = simulate_animal_color(bgr, animal, params)

# 4) 클릭 초점(색 변환 결과 위에서 클릭)
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
    blur_p = FocusBlurParams(r0=float(r0), r1=float(r1), sigma_max=float(sigma_max), p=float(pow_p), levels=int(levels))
    out = apply_focus_blur_bgr(out, x0, y0, blur_p)

st.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
```

---

# 9. 파라미터 출처(정직한 구분)

> **이 섹션의 역할:** 교수님이 가장 중요하게 보는 “출처/정당성” 파트.  
> **원칙:** 논문에서 ‘그대로 가져온 수치’와, ‘근사/시각화 목적의 튜닝값’을 명확히 분리해 과학적 정직성을 지킨다.

## 9.1 논문에서 ‘수치 그대로’ 가져온 값

* Viénot et al.(1999)

  * RGB→LMS 행렬(Eq.(4))
  * deutan LMS 변환 행렬(Eq.(5))
  * domain shrink affine 계수(Eq.(2))
  * 감마 근사(2.2) 기반 선형화/복원 흐름

## 9.2 논문 원칙에 따라 ‘계산으로 얻은 값’

* `M_LMS2RGB = inv(M_RGB2LMS)`

  * 논문은 “역행렬로 복원” 원칙을 쓰며, 역행렬 수치는 구현자가 계산해 재현 가능

## 9.3 논문 서술(현상)을 sRGB에서 재현하기 위한 ‘시각화 파라미터’

* dog 후처리 파라미터(DogPostParams)

  * 근거 현상: 2-hue(blue/yellow), blue-green 중립대역(gray), neutral point shift 등 (Vision in dogs, 1995)
  * 단, 입력이 sRGB 이미지이므로 nm 기반 정량 파라미터를 직접 쓸 수 없어 HSV 대역/압축 강도를 도입

---

# 9A. 경험(시각화) 파라미터 정당화/선정 절차

> **이 섹션의 역할:** dog HSV 파라미터를 “감(감각)”이 아니라 **재현 가능한 프로토콜**로 결정하도록 만든다.  
> **핵심:** 논문 문장(480nm neutral point, 2-hue, cyan-gray)을 직접 ‘수치’로 옮기기 어렵기 때문에, 이미지 관찰 제약을 만족하도록 튜닝 절차를 설계한다.

## 9A.1 정당화 원칙

1. 논문이 제공하는 것은 ‘현상 제약(qualitative constraint)’이다.
2. 입력은 sRGB 3채널 이미지이며 파장 정보를 복원할 수 없다.
3. 따라서 본 과제는 현상 제약을 sRGB 색공간(HSV)에서 강제하는 공학적 후처리를 사용한다.
4. 후처리 수치는 생리 상수가 아니라 시각화 파라미터이며, 아래 절차로 선택해 재현 가능하게 만든다.

## 9A.2 선정 프로토콜(실험 프로토콜+기본값 추천까지)

이 절의 목표는 “dog HSV 후처리 파라미터가 왜 필요한지”를 논문 문장으로 정당화하고,
그 숫자를 임의 감(감각)으로 정하지 않고 **재현 가능한 절차로 고정**하는 것이다.

dog 논문이 제공하는 핵심 제약은 다음 4개다.

- “두 개의 색상군”으로 요약되는 경향: 430~475nm는 blue로, 500~620nm는 yellow로 인식될 가능성이 큼
- 475~485nm(blue-green)는 white 또는 gray로 보일 가능성이 큼
- spectral neutral point가 480nm로, 사람 deuteranopia(505nm)보다 더 파란쪽으로 이동
- 입력이 sRGB 3채널이므로, 픽셀에서 파장(nm)을 역산해 그대로 강제하는 것은 불가능

따라서 본 프로젝트는 “Viénot deutan(정량)” 위에 “HSV 현상 강제(정성 제약)”를 얹어,
위 문장들이 시각적으로 드러나도록 만든다.

---

### 9A.2.1 튜닝용 테스트 입력(필수 3종+선택)

dog 파라미터는 자연 이미지 몇 장만으로 맞추면 재현성이 떨어진다.
반드시 아래 3종의 “합성 테스트”를 같이 사용한다.

1) Hue Wheel(색상 원)
- 배경은 중성 회색, 원형으로 hue를 0~179(또는 0~360deg) 연속 변화
- S는 255 고정, V는 255(또는 200~255 범위) 고정

2) Spectrum Strip(스펙트럼 스트립, proxy)
- 목적: “480nm 근처에서 회색화가 일어나는가”를 정량적으로 잡기 위한 장치
- 구현은 두 가지 중 하나를 선택(둘 다 proxy이며, ‘물리 진실’이 아니라 ‘튜닝 도구’임)
  - (A) HSV 기반 proxy: H를 0~179로 선형 스윕, S=255,V=255로 만들기
  - (B) wavelength→sRGB 근사식을 써서 400~700nm 색 띠를 만들기(근사)

3) Gray Ramp+Skin Patch
- 회색 램프(검정→흰색)가 변환 후에도 색이 끼지 않는지 확인
- 피부톤/목재/흙색 같이 “현실에서 중요한 색”이 과도하게 이상해지지 않는지 확인

선택(권장): 자연 이미지 20~50장(실내/실외/원색/자연/인물/야간 포함)

---

### 9A.2.2 논문 문장을 HSV 제약으로 번역

OpenCV HSV에서 $H\in[0,179]$, $S\in[0,255]$, $V\in[0,255]$이다.

- 475~485nm(gray band) 제약은 HSV에서 “cyan(blue-green) 근처의 채도 감소”로 번역한다.
  - 가우시안 가중치 $w(H)$를 두고, $S\leftarrow S(1-\alpha w)$로 만들면
    특정 hue 대역만 회색화(채도 감소)된다.
- 2-hue 제약은 HSV에서 “두 개의 attractor hue로 끌어당김”으로 번역한다.
  - $H\leftarrow(1-\beta)H+\beta H_{\mathrm{target}}$ 형태로 hue를 압축하면
    색이 두 덩어리(blue/yellow)로 모인다.
- 480nm neutral point 제약은 “스펙트럼 스트립에서 최소 채도 지점이 480nm proxy 부근에 오도록”
  cyan 중심 $H_0$를 조정하는 문제로 번역한다.

중요: 여기서 $H_0$는 “480nm의 생리 상수”가 아니다.
$H_0$는 “입력 sRGB/HSV에서 480nm 현상이 가장 잘 드러나는 위치”를 재현하는 **시각화 파라미터**다.

---

### 9A.2.3 튜닝 순서(권장)

dog 파라미터는 서로 영향을 준다. 아래 순서를 지키면 빠르고 재현성 있게 맞출 수 있다.

0) 기준 고정
- Viénot deutan 변환은 고정(이 부분은 논문 수치)
- dog 후처리만 조절(HSV 단계만)

1) cyan 중심과 폭을 먼저 맞춘다: `cyan_h0`, `cyan_sigma`
- Spectrum Strip에서 “회색화 대역”이 너무 넓거나 좁지 않게 만든다.
- Gray band(475~485nm)가 “좁은 대역”이라는 문장에 맞게,
  `cyan_sigma`는 과도하게 크게 잡지 않는다(권장 8~16).

2) 회색화 강도를 맞춘다: `cyan_desat`
- Hue Wheel에서 cyan 부근이 “채도가 빠져 회색에 가까워지는지”를 확인한다.
- 동시에 Gray Ramp에서 회색에 색이 끼지 않는지 확인한다.

3) 두 목표 hue를 잡는다: `blue_h`, `yellow_h`
- 처음에는 표준 HSV에서 blue와 yellow에 해당하는 목표값으로 시작한다.
- 이후 자연 이미지에서 “blue와 yellow로 뭉치는 느낌”이 부족하면 목표값을 소폭 이동한다.

4) 분기 경계를 정한다: `blue_cutoff`
- 가장 단순한 정책은 `blue_cutoff≈cyan_h0`로 두는 것이다.
- 직관: neutral band(회색화) 근처를 기준으로 “그보다 hue가 큰 쪽은 blue군으로 압축”한다.

5) 압축 강도를 조정한다: `blue_compress`, `yellow_compress`
- 목표: hue 히스토그램이 2개의 피크로 더 뾰족해지되,
  인공적인 밴딩/포스터라이즈가 눈에 띄지 않게 한다.
- 보통 `blue_compress`를 `yellow_compress`보다 약간 크게 시작하는 편이 안정적이다.

6) 전체 채도를 마지막에 조정한다: `sat_global`
- 전체적으로 “색이 덜 화려해 보이는” 경향을 반영한다.
- 너무 낮추면 모든 것이 회색으로 죽는다. 마지막에 미세 조정한다.

---

### 9A.2.4 정량 지표(계산 가능한 형태로 정의)

정량 지표는 “튜닝의 방향성”을 잡는 용도다.
정량이 좋아도 사람이 보기엔 이상할 수 있으므로, 반드시 정성 평가를 병행한다.

아래는 구현이 쉬운 지표 4개다.

#### (1) cyan-gray 만족도: $J_{\mathrm{cyan}}$

HSV에서 cyan band 가중치 $w(H)$는

$$
d_H=\min(|H-H_0|,180-|H-H_0|),\quad
w(H)=\exp\left(-\frac{d_H^2}{2\sigma_H^2}\right)
$$

로 두고, 가중 평균 채도

$$
J_{\mathrm{cyan}}=\frac{\sum S_{\mathrm{out}}\,w(H)}{\sum w(H)}
$$

를 최소화한다. 목표는 “cyan band 채도가 확실히 낮아지는 것”이다.

#### (2) 2-hue 압축도: $J_{\mathrm{2hue}}$

고채도 픽셀만 대상으로($S_{\mathrm{out}}\ge S_{\min}$) hue가 목표점에 얼마나 모이는지 본다.

원형 거리

$$
d(H,H_t)=\min(|H-H_t|,180-|H-H_t|)
$$

를 쓰면,

$$
J_{\mathrm{2hue}}=\mathbb{E}\left[\min(d(H,H_B),d(H,H_Y))\right]
$$

가 작을수록 hue가 blue/yellow 목표로 잘 뭉친 것이다.

#### (3) 회색 오염 방지: $J_{\mathrm{gray}}$

입력에서 회색(또는 저채도)인 픽셀($S_{\mathrm{in}}\le S_{\mathrm{gray}}$)이
출력에서 색이 생기지 않는지 확인한다.

$$
J_{\mathrm{gray}}=\mathbb{E}\left[S_{\mathrm{out}}\mid S_{\mathrm{in}}\le S_{\mathrm{gray}}\right]
$$

이 값이 커지면 “회색이 물드는” 오류가 난다.

#### (4) 밝기 보존: $J_Y$

dog 후처리는 색(특히 $H,S$)을 건드리지만, 밝기(V 또는 선형 휘도 Y)는 크게 바뀌면 안 된다.
선형 RGB에서

$$
Y=0.2126R+0.7152G+0.0722B
$$

로 두고, Viénot base 출력과 dog-post 출력의 평균 절대 차이를 본다.

$$
J_Y=\mathbb{E}\left[|Y_{\mathrm{post}}-Y_{\mathrm{base}}|\right]
$$

---

### 9A.2.5 단일 점수로 묶는 방법(옵션)

랜덤 탐색이나 그리드 탐색을 자동화하고 싶다면 아래처럼 묶는다.

$$
\mathcal{L}=\lambda_1J_{\mathrm{cyan}}+\lambda_2J_{\mathrm{2hue}}+\lambda_3J_{\mathrm{gray}}+\lambda_4J_Y
$$

권장 시작 가중치(상대적 중요도): $\lambda_1:\lambda_2:\lambda_3:\lambda_4=4:3:2:1$

- gray band 구현이 dog 차별점의 핵심이므로 $J_{\mathrm{cyan}}$ 비중을 크게 둔다.
- 회색 오염($J_{\mathrm{gray}}$)은 사용자 체감 품질을 크게 망치므로 중간 이상 비중을 둔다.

---

### 9A.2.6 정성 평가 체크(최소 6개)

정량 지표가 좋아도 아래 중 하나라도 망가지면 탈락이다.

- (필수) dog 출력이 cat 출력과 명확히 구분되는가(“그럴듯한 차이”가 보이는가)
- (필수) sky/sea/cyan 물체가 dog에서 회색화되는 경향이 보이는가
- (필수) 회색(벽, 아스팔트, 흰 셔츠)이 색으로 오염되지 않는가
- (권장) 인물 피부가 과도하게 황색/회색으로 죽지 않는가
- (권장) 채도가 높은 원색에서 밴딩/포스터라이즈가 두드러지지 않는가
- (권장) 전체적으로 “필터 느낌”이 아니라 “지각 변화 느낌”이 나는가

---

## 9A.3 보고서 필수 포함(권장)

- dog 후처리 ON/OFF 비교 이미지(같은 입력)
- 최종 파라미터 테이블(DogPostParams)
- 합성 테스트(Hue Wheel, Spectrum Strip, Gray Ramp) 결과 이미지

---

## 9A.4 DogPostParams 기본값 추천(시작점)

아래 값은 “dog 논문 제약을 만족시키기 쉬운 시작점”이다.
환경(이미지 분포, 조명, 디스플레이)에 따라 조정될 수 있으며,
이 값 자체를 생리 상수로 해석하면 안 된다.

### 9A.4.1 권장 범위와 기본값

| 파라미터 | 권장 범위 | 시작 기본값 | 역할(논문 제약과 연결) |
|---|---:|---:|---|
| `cyan_h0` | 95~105 | 100 | 480nm neutral point를 HSV에서 재현하기 위한 중심 |
| `cyan_sigma` | 8~16 | 12 | 475~485nm “좁은 회색 대역” 폭 |
| `cyan_desat` | 0.40~0.85 | 0.65 | cyan 대역을 얼마나 gray로 빼는지 |
| `blue_h` | 110~125 | 120 | 430~475nm를 blue군으로 압축(목표 hue) |
| `yellow_h` | 25~35 | 30 | 500~620nm를 yellow군으로 압축(목표 hue) |
| `blue_cutoff` | 85~105 | 95 | blue/yellow 분기 경계(대체로 `cyan_h0` 근처) |
| `blue_compress` | 0.30~0.75 | 0.55 | blue군 압축 강도(2-hue 강화) |
| `yellow_compress` | 0.20~0.65 | 0.40 | yellow군 압축 강도 |
| `sat_global` | 0.75~0.95 | 0.85 | 전체 채도 감소(원추 수 감소로 인한 색감 약화) |

### 9A.4.2 코드로 바로 쓰는 기본값 예시

```python
DogPostParams(
    cyan_h0=100.0,
    cyan_sigma=12.0,
    cyan_desat=0.65,
    blue_h=120.0,
    yellow_h=30.0,
    blue_cutoff=95.0,
    blue_compress=0.55,
    yellow_compress=0.40,
    sat_global=0.85,
)
```

### 9A.4.3 기본값에서 “어느 방향으로” 움직이면 되는가(빠른 디버깅)

- cyan band가 너무 넓게 회색이면: `cyan_sigma`를 낮추거나 `cyan_desat`를 낮춘다.
- cyan band가 티가 안 나면: `cyan_desat`를 올리거나 `cyan_sigma`를 약간 올린다.
- blue/yellow로 안 뭉치면: `blue_compress`,`yellow_compress`를 올린다.
- 밴딩/인공 느낌이 강하면: compress를 내리고, 대신 `sat_global`만 소폭 낮춘다.
- 하늘이 너무 회색으로 죽으면: `cyan_desat`를 내리고 `sat_global`을 올린다.
- 회색 벽이 푸르스름/누르스름해지면: (우선) `cyan_desat`를 올리는 것이 아니라,
  `sat_global`을 올리고 compress를 낮춰 “색 왜곡 압력”을 줄인다.

---

# 10. 품질/성능 체크리스트

> **이 섹션의 역할:** 구현 실수(감마 순서 뒤집힘, 클리핑 폭증 등)를 빠르게 잡아내는 리그레션 체크리스트.

* 감마 처리 순서가 유지되는지(입력 sRGB→선형화→행렬 연산→감마 복원)
* clipping이 심하면 domain shrink가 적용되는지
* 4K 등 고해상도 입력에서 리사이즈로 Streamlit 응답성을 유지하는지

---

# 11. 참고문헌(프로젝트에서 사용)

> **이 섹션의 역할:** 모든 설계 선택이 “어느 논문/어느 주장”에 기대고 있는지 추적 가능하게 한다.

* Vision in dogs (1995)
* Neutral point testing of color vision in the domestic cat (2016)
* PHOTOPIC SPECTRAL SENSITIVITY OF THE CAT (Loop et al., 1987)
* Brettel et al., Computerized simulation of color appearance for dichromats (1997)
* Viénot et al., (1999) deutan 선형 근사
* Potmesil & Chakravarty, A lens and aperture camera model… (1981)
* Bae & Durand, Defocus Magnification (2007)
* Zhu & Milanfar, Depth from defocus / coded aperture 관련(2013)
* Troscianko & Stevens, Image calibration and analysis toolbox (2017)
* QCPA: Quantitative Colour Pattern Analysis framework (2018)
