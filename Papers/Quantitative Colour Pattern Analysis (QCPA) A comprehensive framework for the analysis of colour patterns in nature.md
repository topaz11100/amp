# Quantitative Colour Pattern Analysis (QCPA): 자연계의 색채 패턴 분석을 위한 종합적 프레임워크

* 저자: Cedric P. van den Berg, Jolyon Troscianko, John A. Endler, N. Justin Marshall, Karen L. Cheney
* 저자 주: Cedric P. van den Berg와 Jolyon Troscianko는 공동 제1저자임.
* 기관: The School of Biological Sciences, The University of Queensland, Australia; Centre for Ecology & Conservation, Exeter University, UK; School of Life & Environmental Sciences, Deakin University, Australia; Queensland Brain Institute, The University of Queensland, Australia
* 교신저자: Jolyon Troscianko ([jt@jolyon.co.uk](mailto:jt@jolyon.co.uk))
* 수리: 2019-06-25, 게재 승인: 2019-10-18
* 학술지: Methods in Ecology and Evolution 11:316–332
* DOI: 10.1111/2041-210X.13328
* 라이선스: Creative Commons Attribution (CC BY 4.0)

---

## 초록 (Abstract)

1. 자연계의 색 신호 기능을 이해하려면, 생태적으로 관련 있는 종(수용자)의 시각으로 볼 때 동식물의 색채 패턴이 자연 배경에 대해 어떻게 나타나는지를 추정할 수 있는 견고한 정량적 분석 프레임워크가 필요하다. 기존 방법의 정량적 한계 때문에, 방대한 문헌과 수십 년의 공간-색채(spatio-chromatic) 패턴 분석의 중요성에도 불구하고 색(color)과 패턴(pattern)은 함께 분석되는 일이 드물었다. 더 나아가 동물 시각계의 핵심 생리적 제한(공간 분해능(spatial acuity), 분광 민감도(spectral sensitivities), 광수용체 풍부도(photoreceptor abundances), 수용체 잡음(receptor noise) 수준 등)이 색채 패턴 분석에서 함께 고려되는 경우도 드물다.
2. 본 연구에서는 ‘정량적 색채 패턴 분석(Quantitative Colour Pattern Analysis, QCPA)’이라 부르는 새로운 분석 프레임워크를 제시한다. 우리는 보정된 디지털 사진(calibrated digital photography)과 시각 모델링(visual modelling)을 결합함으로써 기존 색채 패턴 분석의 많은 정량적·정성적 한계를 극복하였다. 인접성(adjacency), 시각 대비(visual contrast), 경계 강도 분석(boundary strength analysis) 등 기존의 공간-색채 패턴 분석을 통합·업데이트하여, 다중분광 영상 분석 및 보정 도구(Multispectral Image Calibration and Analysis, MICA) 툴박스를 통해 보정된 디지털 사진으로 구현한다.
3. 보정 사진과 공간-색채 패턴 분석의 결합은 영상 분할(image segmentation)을 위한 심리물리적 색 및 휘도 판별 임계값(‘수용체 잡음 제한 군집화(Receptor Noise Limited Clustering, RNL clustering)’라 칭함)의 도입으로 가능해졌다(본 연구에서 최초 사용). 또한 공간 혹은 주파수 영역의 컨볼루션을 사용한 공간 분해능 모델링에 이어, 스무딩 후 중간 경계 인공물을 제거하여 선명한 경계를 복원하는 ‘수용체 잡음 제한 순위 필터(Receptor Noise Limited Ranked Filtering, RNL ranked filter)’라는 새로운 정신생리학적 접근을 제공한다. 아울러 새로운 유형의 색채 패턴 분석인 ‘국지(edge) 강도 분석(Local Edge Intensity Analysis, LEIA)’과 다양한 공간-색채 데이터 시각화 방법을 제시한다.
4. QCPA는 새로운 분석과 기존 패턴 분석 프레임워크를 통합한 통일적(unified), 자유·오픈소스 툴박스로서, MICA에 매끄럽게 통합되어 동작하며 동작 절차 전반에 걸친 사용자 친화적 환경을 제공한다.

**주요어 (Keywords)**: 동물 색채(Animal colouration), 색채 패턴 분석(Colour pattern analysis), 색 지각(Colour perception), 색 공간(Colour space), 영상 분석(Image analysis), 수용체 잡음 제한 모델(Receptor Noise Limited model), 시각 모델링(Visual modelling)

---

## 1. 서론 (Introduction)

동물의 색채 패턴은 포식자 회피(위장(camouflage), 경고색(aposematism)), 사회적 신호(social signalling), 열 조절(thermoregulation) 등 다양한 목적을 수행하는 복합 형질이다(Cott, 1940). 색채 패턴이 동물에 의해 어떻게 지각되는지는 특정 맥락에서의 주어진 시각계에 고유하며, 관찰되는 시각 배경(visual background), 신호 수용자의 시각 능력, 패턴을 보는 거리(viewing distance), 주변 광 환경(ambient light environment)에 따라 달라진다(Cuthill et al., 2017; Endler, 1978, 1990; Lythgoe, 1979; Merilaita et al., 2001). 동물의 시각계는 눈의 형태와 크기, 시각 색소의 수와 흡수 최대치, 광수용체 유형과 수, 망막 및 망막 이후(post-retinal) 처리 등에서 매우 다양하다(Cronin et al., 2014; Lythgoe, 1979). 그러므로 타 동물의 색채 패턴 지각을 결정하려면, 공간 분해능(및 시거리)뿐 아니라 색 및 휘도 판별 능력 또한 반드시 고려해야 한다(Endler, 1978). 인간은 대부분의 척추동물보다(일부 조류 제외) 더 높은 공간 분해능과 대비 민감도를 가지며(Caves et al., 2016; da Silva Souza et al., 2011), 수용체 종류의 수와 분광 민감도 범위도 많은 동물과 다르다(Cronin et al., 2014). 예컨대 대부분의 다른 포유류는 이색시(dichromat; 원뿔세포 2종)를 보이는 반면, 다수의 조류·파충류·일부 양서류·거미·어류는 자외선(UV) 민감 원뿔을 보유하여 사색시(tetrachromat)일 가능성이 높다(Cronin & Bok, 2016; Osorio & Vorobyev, 2005, 2008). 무척추동물에서는 수용체 종류의 수가 10을 넘는 경우도 있다(Cronin et al., 2014).

동물의 시각 신호 지각을 조사하기 위해, 연구들은 일반적으로 색(color), 휘도(luminance), 패턴 특성 등을 측정한다(예: Allen & Higham, 2013; Cortesi & Cheney, 2010; Marshall et al., 2006; Xiao & Cuthill, 2016; Zylinski et al., 2011). 예를 들어, 동물 내부의 색 패치들 사이 또는 동물과 배경 사이의 색(색채; chromatic) 및 휘도(무채; achromatic) 대비를, 종종 수용체 잡음 제한 모델(Receptor Noise Limited, RNL; Vorobyev & Osorio, 1998)을 사용하여 색 공간에서의 지각적 거리(perceptual distance)로 계산한다. 이 모델은 광수용체 내부 잡음, 상대적 풍부도, 반대색(opponent) 처리 기제가 색 및 휘도 대비 지각의 근본 한계임을 가정한다. 그 후 광수용체 상대 자극(relative stimulation)을 이용하여 색 공간에서 색 패치 간 지각 거리들을 사상할 수 있다(Renoult et al., 2017). 이러한 유클리드 또는 기하학적 거리들은 ΔS 값으로 표기되며(Siddiqi et al., 2004; Vorobyev et al., 2001), 모델 조건과 가정이 충족되면 ‘최소 변별 차이(Just Noticeable Difference, JND)’가 ΔS = 1에 해당한다고 예측한다(Vorobyev & Osorio, 1998). 패턴의 공간적 성질을 정량화하기 위해서는 디지털 이미지의 픽셀 강도에 대한 고속 푸리에 변환(Fast Fourier Transform, FFT; Switkes et al., 1978), 위치 의존 전이 행렬(transition matrices; Endler, 2012), 또는 기준점(landmark) 기반 패턴 지표(Lowe, 1999; Troscianko et al., 2017; Van Belleghem et al., 2018) 등이 사용된다.

이러한 분석들은 망막 수준의 시각 정보 처리를 계산적으로 재현하는 것을 목표로 하지만, 종종 색, 휘도, 패턴 대비를 각각 고립적으로 탐구한다. 예컨대 Cheney et al.(2014)은 누드브랜치(연체동물)의 눈에 띄는 정도(conspicuousness)를 디지털 이미지에 대한 FFT로 자연 배경 대비의 패턴 대비를 측정하고, 분광광도계로 얻은 점 측정값으로 동물과 배경 사이의 색채 대비(ΔS)를 산출하였다. 많은 동물 색채 연구에 유용하긴 하나, 이러한 개별 분석은 지각의 다양한 단계에서의 시각 정보 상호작용을 무시한다(Endler & Mappes, 2017; Ng et al., 2018; Rowe, 2013; Ruxton et al., 2018; Stevens & Merilaita, 2011). 반면 복잡한 시각 신호의 지각—나아가 설계, 기능, 진화—를 조사할 때 시각 정보를 통합적으로 고려해야 한다는 필요성은 계속 강조되고 있다(Dalziell & Welbergen, 2016; Endler, 1978, 1984, 2012; Endler et al., 2018; Hebets & Papaj, 2005; Osorio et al., 2004; Rowe, 1999, 2013; Rowe & Guilford, 1999; Ruxton et al., 2018; Shapley & Hawken, 2011; Stevens & Merilaita, 2011). 예컨대 시각 신호의 효율성은 특정 색의 존재 여부뿐 아니라 그 색들이 패턴 내에 어떻게 배열되어 있는지에 좌우된다(Endler & Houde, 1995; Green et al., 2018; Sibeaux, Cole, & Endler, 2019; Troscianko et al., 2017).

공간-색채 패턴 분석의 기존 방법들(Endler, 2012; Endler et al., 2018; Endler & Mielke, 2005)은 최근 PAVO 2(Maia et al., 2019)에 의해 구현되었으며, 기하학적 복잡도(geometric complexity), 규칙성(regularity), 색상(hue), 채도(saturation) 등 색채 패턴의 기하학적·색채적 속성을 매개변수화한다. 또한 색채 패턴의 공간적·색채적 속성에 의해 동시에 형성되는 매개변수(예: 풍부도 가중 색채 대비 지표)도 제공한다. 그러나 이러한 분석은 분할(segmented)된 이미지를 필요로 하며, 즉 개별 색 패치가 구분되어 있어야 한다. 따라서 색 차이가 매우 뚜렷한(높은 색채/무채 대비의 날카로운 경계) 패턴이나 장면, 혹은 각 색 패치에서 스펙트럼 데이터를 쉽게 채취할 수 있는 경우에만 적합하다. 그렇지 않으면 자연 변이의 전형적 수준을 포함하는 장면에서 분광 측정을 위해 비현실적으로 많은 지점이 요구될 수 있다. 디지털 이미징은 각 이미지가 수백만 개의 점 표본을 빠르고 비침습적으로 포착하여 필요한 색채·공간 정보를 제공할 수 있으므로 이러한 분석에 이상적이다. 그러나 현재 사용 가능한 영상 분할 및 처리 기법은 생태적으로 관련 있는 관찰자의 생리적·인지적 제한을 충분히 통합하지 못한다. 실제로 많은 접근법이 인간 관찰자가 색 패턴 요소의 외곽선을 수동으로 그리거나, 디지털 이미지의 RGB 값(해석되지 않은)을 이용하는 군집화 알고리즘에 의존한다(Endler & Houde, 1995; Isaac & Gregory, 2013; Winters et al., 2017). 이러한 접근은 색이 명확한 범주에 속하고 분광계나 보정된 디지털 촬영으로 검증된 경우가 아니라면, 동물 색채 해석에 인류 중심적(정성적)·정량적 편향을 도입할 수밖에 없다.

본 논문은 이러한 문제를 해결하기 위한 방법을 제공하고, ‘정량적 색채 패턴 분석(QCPA)’이라 부르는 사용자 친화적 오픈소스 프레임워크를 제시한다. QCPA는 자연계의 색채 패턴의 설계와 기능을 연구하기 위한 포괄적 접근으로, 보정된 디지털 사진(Stevens et al., 2007), 시각 모델링, 색채 패턴 분석을 ‘다중분광 영상 보정 및 분석 툴박스(Multispectral Image Calibration and Analysis, MICA; Troscianko & Stevens, 2015)’에 매끄럽게 통합한 분석 틀이다. QCPA는 기존·수정·신규 색채 패턴 분석을 전례 없는 정량·정성 규모에서 가능하게 한다. 이는 결합된 색 및 휘도 판별 임계값을 사용하는 영상 분할(RNL clustering 또는 나이브 베이즈 군집화; 보충자료)과 향상된 시각 분해능 모델링(RNL ranked filtering)에 의해 뒷받침된다. QCPA에 포함된 패턴 분석은 색 인접성 분석(Colour Adjacency Analysis, CAA), 시각 대비 분석(Visual Contrast Analysis, VCA), 경계 강도 분석(Boundary Strength Analysis, BSA) 등이며, 이를 확장·적응·수정하였다. 예컨대 분할 이미지를 요구하지 않으면서 시각계의 수용체장(receptive field) 규모를 근사해 색채 패턴의 경계 강도를 분석하는 국지(edge) 강도 분석(LEIA)을 도입한다. QCPA는 시각 정보를 고도로 기술적인 수치 배열과 대표 그림으로 변환하는 자유롭게 조합 가능한 영상 처리 도구망을 제공하며, 이를 통해 다양한 진화·행동·생태 질문을 탐구할 수 있다(그림 1). QCPA의 잠재적 적용 분야에는 배경 맞춤(background matching), 교란 위장(disruptive colouration), 다형(polymorphism), 의태(mimicry), 경고색(aposematism), 성 신호(sexual signalling), 영역 신호(territorial signalling), 열 조절(thermoregulation), 경관 분석(landscape analysis) 등이 있다.

---

## 2. 재료 및 방법 (Materials and Methods)

본 절에서는 보정된 디지털 이미지 획득과 관찰자 시각의 이론적 모델링을 간략히 설명한 뒤, QCPA의 개별 도구들을 자세히 기술한다.

### 포함 도구 개요

* **공간 분해능 모델링(Modelling of spatial acuity)**: FFT(고속 푸리에 변환) 적응 또는 가우시안 필터 사용.
* **영상 스무딩 및 경계 복원(Image smoothing and edge reconstruction)**: RNL 순위 필터(Ranked Filter) 사용.
* **영상 분할(Image segmentation)**: RNL 군집화(clustering) 및 나이브 베이즈 군집화.
* **패턴 분석(Pattern analysis)**: 인접성(CAA), 경계 강도(BSA), 시각 대비(VCA), 국지(edge) 강도 분석(LEIA), 입자 분석(particle analysis).
* **데이터 시각화(Data visualization)**: ΔS 경계 강도 이미지, XYZ 반대색(opponency) 영상, RNL 채도(saturation) 영상, RNL 색좌표 공간의 컬러맵(colour maps).

마지막으로, QCPA의 풍부한 수치 출력을 활용하여 자연계 색채 패턴의 설계·기능·진화를 조사하는 방법을 설명하며, 보충자료에는 상세 기술 정보, 용어집, 예제 작업이 포함되어 있다.

### 2.1 단계 1: 보정된 디지털 이미지 획득 (Acquisition of calibrated digital images)

장면의 공간-색채적 속성 분석에 적합한 데이터를 확보하는 것이 QCPA 구현의 첫 단계이다. 오픈소스·사용자 친화적인 MICA 툴박스는 거의 모든 디지털 카메라로부터 보정된 다중분광 이미지와 원뿔세포 포착(cone-catch) 이미지를 생성할 수 있다(Troscianko & Stevens, 2015). 원뿔 포착 이미지는 각 픽셀에서 동물의 광수용체 자극을 모델링하며, UV 민감 종의 시각을 모델링할 때 UV 민감 카메라를 추가로 지원한다(그림 1, 2). 초분광 카메라도 이 과업에 이론적으로 적합하나(Long & Sweet, 2006; Russell & Dierssen, 2015) 비용과 해상도 등의 제한이 있다. QCPA는 초분광 이미지 분석에도 사용 가능하다. 고품질 보정 이미지 데이터 획득 방법은 Troscianko and Stevens(2015)에 상세히 기술되어 있다.

MICA는 자체 영상 분석 도구 집합을 제공하며(Troscianko et al., 2017), QCPA도 여기에 기여한다. 특히 MICA는 임의의 광 환경에 대한 원뿔 포착을 모델링할 수 있어, 한 광 환경에서 관찰한 장면을 다른 광 환경으로 변환하여 볼 수 있다(예: 흐린 낮의 들판에서 본 꽃을, 장파장 풍부한 일출 광 스펙트럼으로 변환). 또한 종별 분광 민감도 정보가 있을 경우 서로 다른 종의 분광 민감도와 원뿔 채널 간 전환이 가능하다(예: 새와 벌의 관점 비교). 종특이 분광 민감도 정보는 얻기 어렵지만, 근연종 정보를 이용해 추정하기도 한다(Kemp et al., 2015; Olsson et al., 2018).

### 2.2 단계 2: 판별 임계값 정의 (Defining discrimination thresholds)

이미지 내 색채(ΔS_C) 및 무채(휘도; ΔS_L) 대비는 1~n차원 색 공간에서 임의의 두 픽셀 간 지각 거리로서 RNL 모델(Vorobyev & Osorio, 1998)을 사용해 계산할 수 있다(Hempel de Ibarra et al., 2001—색채 대비; Siddiqi et al., 2004—무채 대비). 현재 QCPA는 명시(photopic) 조건의 RNL 방정식을 사용한다(다른 변형은 논의에서 언급). 이러한 대비는 디지털 이미지에서 픽셀 잡음(센서 잡음으로 인한 강도 요동)을 제거하고, 색채 패턴으로의 영상 분할에도 사용된다. 시각계 종특 데이터(특히 수용체 잡음)는 얻기 어렵기 때문에(Olsson et al., 2015) 종종 모수 추정이 필요하며, 이는 RNL 가정의 편차와 맞물려 행동 실험을 통한 임계값·모수 검증 또는 보수적 임계값 선택의 필요성을 강조한다(Olsson et al., 2018).

QCPA의 RNL 기반 도구는 색 반대( opponent) 처리의 부재(Thoen et al., 2014) 또는 RNL 가정과 크게 다른 반대 처리(예: Rocha et al., 2008)가 의심되는 동물에는 주의하여 사용해야 하며, 이러한 경우를 위해 대체 분할 도구와 패턴 통계(보충자료)를 제공한다.

### 2.3 단계 3: 공간 분해능 모델링 (Modelling of spatial acuity)

동물이 패턴을 분해하여 인지할 수 있는 능력은 시각계의 공간 분해능(해부학·행동·생리 측정으로 결정 가능; Champ et al., 2014)과 관찰 거리의 함수이다. 특정 거리에서 패턴 요소가 동물에게 보이는지 조사하는 것이 중요하다(Endler, 1978; Marshall, 2000). 예컨대 일벌은 시각 분해능의 한계로 인해, 가까이 다가가기 전에는 벌꿀 저장을 안내하는 꽃의 복잡한 UV 패턴을 지각하지 못한다(그림 3). QCPA는 AcuityView(Caves & Johnsen, 2017) 적응과 가우시안 블러를 사용하여 공간 분해능 모델링 도구를 확장·적용한다.

### 2.4 단계 4: RNL 순위 필터로 분해능 관련 문제 보정 (Eliminating problems in acuity-related processing using the RNL Ranked Filter)

AcuityView 기반 블러링(단계 3)은 수용자 지각을 ‘보여주는’ 것이 아니라, 해당 시각계로는 해상할 수 없는 세부를 제거하려는 것이다(Caves & Johnsen, 2017). 많은 동물은 이용 가능한 시각 정보가 망막/망막 이후에서 통합되므로, 분명한 공간 정보를 지각할 가능성이 높다. 블러 경계는 군집화·경계 비교 기법에 문제를 일으키며 동물에게는 무의미한 처리 인공물을 만들 수 있다. 또한 카메라 센서의 픽셀 잡음 요동은 군집화에 간섭하여 거짓 경계나 인공 패턴 요소를 만들거나 경계 구조에 영향을 준다.

이를 해결하기 위해, 우리는 영상 분할 전에 적용하는 ‘RNL 순위 필터(Ranked Filter)’를 개발했다. 이는 사진 편집 소프트웨어의 ‘스마트 블러’ 및 기타 순위 선택 필터와 유사하게 커널 내 픽셀을 순위화하여 수정하지만, 본 알고리즘은 동물의 심리물리적 변별 능력(RNL 모델 사용)을 이용해 색·휘도 변별에 기초한 선명한 경계 재구성과 픽셀 잡음 감소를 수행한다(그림 4c, 보충자료). 다만 이 필터가 특정 종의 공간 정보 지각을 얼마나 반영하는지는 행동 실험으로 검증하는 것이 바람직하다.

### 2.5 단계 5: RNL 군집화를 이용한 심리물리적 영상 분할 (Psychophysical image segmentation using RNL Clustering)

입자성(granularity) 분석(Stoddard & Stevens, 2010)이나 NaturePatternMatch(Stoddard et al., 2014) 등 일부 패턴 분석은 비분할 이미지(단계 1–4)에 적용할 수 있다. 반면 Patternize(Van Belleghem et al., 2018)나 QCPA의 대부분 분석은 색 패턴 요소로 분할된 이미지를 요구한다. 그러나 영상 분할은 종종 연구자가 색 요소 개수를 주관적으로 추정하는 등 인간 지각에 의존해 이루어지며, 이는 복잡 패턴이나 인간과 크게 다른 시각계를 가진 종을 분석할 때 인류 중심적 편향을 초래할 수 있다. 이를 위해 우리는 색·휘도 변별 임계값(개별 또는 결합)을 사용하는 응집적 위계적 군집(agglomerative hierarchical clustering; Day & Edelsbrunner, 1984) 접근을 제시한다. 각 픽셀을 이웃과 비교하여, 로그 변환 RNL 모델로 두 픽셀이 해당 동물의 지각에서 색/휘도 대비로 구분 가능한지 판정한다. 전 영역에 적용하면, 동물의 심리생리학적 변별 임계값에 따라 분할된 이미지가 얻어진다(그림 4d). 이 접근은 컴퓨터 비전의 통계적 영역 병합(statistical region merging; Nock & Nielsen, 2004)과 유사점을 가진다. 공간·색채·무채 정보 지각의 관계는 연구마다 다르므로(Clery et al., 2013; Miquilini et al., 2017; Shapley & Hawken, 2011; Shevell & Kingdom, 2008), 결합 임계값은 맥락화된 행동 실험으로 확인할 것을 권한다. RNL 군집 메커니즘과 색·무채 임계값의 결합·가중에 대한 상세는 보충자료를 참조.

### 2.6 단계 6: 색채 패턴 분석 (Colour pattern analysis)

이제 동물 시각계의 생리·심리적 제한과 물리적 환경을 반영하여 필터링·수정된 이미지를 바탕으로, 색채 패턴의 설계·기능에 관한 질문을 정량화할 수 있다.

#### 2.6.1 색 인접성 분석 (Colour Adjacency Analysis, CAA)

CAA는 색채 패턴과 전체 시각 장면의 기하학적 성질을 측정하는 방법이다(Endler, 2012). 동물의 몸축에 평행·수직인 횡단선(transect)을 따라 전이 빈도를 측정하고, 전이 행렬을 구성하여 패턴 기하 및 잠재적 기능과 관련된 지표를 도출한다. 이 기법은 경관 생태학에서 패턴과 그 귀속 성질 정량화에 널리 쓰이는 전이 행렬을 시각 생태에 도입한 것이다(McGarigal & Marks, 1994; Wickham et al., 1996). CAA는 종종 모식·의태·경고색·위장·성 신호·진화적 발생 등에서 패턴 기하와 인접성의 정량화에 활용된다(그림 5 및 관련 문헌; 자세한 매개변수는 보충자료).

#### 2.6.2 시각 대비 분석 (Visual Contrast Analysis, VCA)

VCA는 공간과 색채, 휘도를 동시에 탐구하도록 설계된 분석으로, 패턴 요소의 상대 크기·위치(공간), 색상·채도(색채), 휘도(무채)가 신경계의 하위·상위 처리에서 통합되어 형성되는 ‘시각 대비’를 정량화한다. 예컨대 풍부도 가중 색채 지표 등 공간·색채 속성을 결합한 패턴 통계를 제공한다(Endler & Mielke, 2005; 보충자료). 보다 자세한 방정식·지침은 원 출판물과 보충자료, 실증 연구를 참조.

#### 2.6.3 경계 강도 분석 (Boundary Strength Analysis, BSA)

BSA(Endler et al., 2018)는 CAA의 확장으로, CAA에서 생성되는 전이 행렬을 이용해 인접 색 패턴 요소 사이의 경계 성질을 측정한다. 패턴 내 패치의 크기·풍부도·색·휘도·인접성, 그리고 인접 패치 사이 경계의 색채/무채 대비가 신호의 성질에 영향을 준다는 점에 근거한다(Endler et al., 2018; Green et al., 2018; Shapley & Hawken, 2011). 또한 관찰자 시점·운동의 효과까지 정량화할 수 있다. 세부 방정식과 최근 매개변수 수정은 보충자료를 참조.

#### 2.6.4 국지(edge) 강도 분석과 ΔS 경계 지도 (Local Edge Intensity Analysis, LEIA; ΔS edge maps)

BSA는 명확히 분할된 이미지(클러스터된 색 패턴 요소)에 의존하는데, 분할 과정은 지각 임계 이하(subthreshold)의 정보—특히 밝기와 색의 완만한 그라디언트—를 크게 제거한다. 이를 보완하기 위해, 분할을 요구하지 않는 ROI/이미지에서 색·휘도 대비를 로그-선형 RNL 반대색 공간(Renoult et al., 2017)에서 이웃(수평·수직·대각선) 픽셀과 비교하여 경계 강도를 정량화하는 LEIA를 제공한다. 결과는 ‘ΔS 경계 이미지(ΔS Edge Images)’로 시각화할 수 있다(그림 7). BSA가 경계 종류의 전역적 풍부도로 가중하는 반면, LEIA는 대략 수용체장의 규모에서의 국지적 경계 강도를 제공하며, 저수준의 경계·특징 탐지(Feature detection)가 이 수준에서 이루어진다는 견해에 부합한다(Marr, 2010; Marr & Hildreth, 1980). LEIA는 분해능 제어(비지각 경계/그라디언트 제거)와 RNL 순위 필터를 거쳐 국지 색·휘도 경계가 최대치로 복원된 이미지에 사용하는 것을 권한다. 또한 LEIA는 비정규 분포적 경계 강도(예: 균질 배경 위 작은 현저 물체)에 견고한 수치 출력을 제공한다.

---

### 2.7 단계 7: 데이터 시각화 (Data visualization)

보정 디지털 사진과 심리물리적 색 공간으로의 데이터 변환은 시각화에 도전이자 기회다. 우리는 ΔS 경계 강도 이미지에 더해, 컬러맵(colour maps), XYZ 반대색(opponency) 이미지, 채도(saturation) 이미지를 제공한다.

#### 2.7.1 컬러맵과 XYZ 색도/채도 이미지 (‘Colour maps’ and ‘XYZ chromaticity and saturation images’)

색 공간에서의 색채 정보 표현은 시각 생태에서 유용한 시각화 도구다(Endler & Mielke, 2005; Gawryszewski, 2018; Maia et al., 2013; Renoult et al., 2017). 지금까지 대부분의 연구는 분광계의 이산 측정값 또는 ROI의 원뿔 포착 평균 중심점으로 산출한 산점 형태로 데이터를 제시해 왔다. 점군 간 영역/부피 중첩이나 순열 검정 등을 이용해 두 색 패치의 이질성을 판정한다(예: Endler & Mielke, 2005; Kemp et al., 2015; Maia & White, 2018; Stoddard & Prum, 2008). 그러나 이러한 시각화는 일반적으로 공간(패턴) 정보를 포함하지 않는다. 보정 디지털 이미징은 각 ROI에서 수천~수백만의 색 측정을 제공하므로, 자연 패턴에 존재하는 색채 그라디언트의 전 범위를 포착할 수 있다(그림 8, 9 설명 참조).

---

## 3. 논의 (Discussion)

QCPA는 자연계의 색채 패턴을 전례 없는 정량·정성 수준에서 분석하기 위한 프레임워크이다. 핵심은 보정 디지털 사진의 장점을 활용하여 기존의 공간-색채 색채 패턴 분석을 가능하게 하고(그림 1), 포토레셉터 분광 민감도, 수용체 잡음 수준과 풍부도, 자연 광 환경, 복잡한 자연 배경, 공간 분해능, 관찰 거리 등을 맥락화할 수 있는 사용자 친화적 오픈소스 프레임워크를 제공하는 데 있다(표 1).

QCPA의 개별 모델링 구성요소는 기저 생물학적 과정에 대한 현시점 최선의 이해에 근거한 근사와 가정을 사용한다. 따라서 각 구성요소의 한계와 전제에 유의해야 한다. QCPA는 다양한 종(인간, 꿀벌, 조류, 도마뱀, 산호초·담수 어류 등)에서 행동적으로 검증된 수용체 잡음 제한(RNL) 모델을 광범위하게 사용한다. 다만 반대색 처리의 부재 또는 RNL 가정과 상이한 반대색 처리를 보일 가능성이 있는 종에서는 주의가 필요하며, 이를 위한 대체 도구와 지표가 제공된다(보충자료).

QCPA는 특정 맥락에서 소수 매개변수(예: 동물 대 배경의 평균 휘도 대비)와 반응변수(예: 포식자 공격률)를 연결하는 가설 검증에도 사용할 수 있다. 이런 실험은 구체적 공간·색채·시간 속성의 지각에 영향을 주는 교란 요인을 통제한 고도로 보정된 환경과 자극을 요구한다(Shapley & Hawken, 2011). 한편 색채 패턴은 색채·무채·공간 속성의 다양한 측면을 포착하는 다수 매개변수로 정량화될 수 있으며(QCPA는 그 일부만 포착), ‘복잡성’, ‘현저성(눈에 띔)’, ‘유사성’과 같은 용어는 흔히 단일 지표로 설명될 수 없고, 패턴과 배경의 물리적 속성이 변화하여 야기되는 지각적 결과를 포괄하는 상위 범주로 이해해야 한다. 많은 QCPA(및 기타 패턴 분석) 매개변수는 아직 경험적으로 충분히 검증되지 않았으므로, 맥락에 따른 보편적 추천을 제시하기 어렵다. 연구 질문이 단순하고 실험이 잘 통제될수록 소수 매개변수를 독립적으로 고려하는 것이 적절하다.

사전 선택 근거가 없는 경우, 주성분분석(PCA), (비)계량 다차원 척도법(MMDS/NMDS), 요인분석 등 다변량 분석으로 패턴 분석 출력과 동물 행동 간 상관을 식별하거나 분류군을 구분할 것을 권한다. 이는 ‘다차원 패턴 공간’에서 작업한다고 볼 수 있다(Cuthill, 2019; Stoddard & Osorio, 2019).

마지막으로, QCPA는 무료·오픈소스·GUI 기반이며 방대한 지원 자료를 제공함으로써 접근성과 사용자 친화성을 크게 높였다. ImageJ를 기반으로 하여 향후 의존 패키지의 비호환성 위험을 줄이고, QCPA와 MICA는 장기적 호환성에 강하다. 또한 스마트폰이나 저가 카메라와 색차트만으로도 활용이 가능하며, 분광광도계 접근성이 낮아도 모델링 출력 비교가 반드시 필요하지는 않다(장비 비용 측면에서 큰 이점). 결론적으로, 자연계 색채 패턴의 설계·기능·진화에 관한 수많은 이론과 예측은 아직 단순화된 혹은 정성적 방식으로만 탐구되어 왔다. QCPA는 이러한 이론들을 새로운 정량·정성 맥락에서 탐구할 강력한 프레임워크를 제공한다.

---

## 감사의 글 (Acknowledgements)

유익한 토론을 제공한 Simone Blomberg, Samuel Bear Powell에게 감사한다. 기술적 도움을 제공한 Miriam Heinze, Wen-Sung Chung에게 감사한다. 또한 귀중한 기여를 해준 심사자들에게 감사한다. 본 연구는 Australian Research Council Discovery Project Grants DP150102710(J.A.E., N.J.M., K.L.C.), DP150102817(J.A.E.)의 지원을 받았고, C.P.v.d.B는 Holsworth Wildlife Research Endowment의 지원을 받았다. J.T.는 NERC IRF Fellowship NE/P018084/1의 지원을 받았다. 편집: Graziella Iossa.

## 지원 정보 (Supporting Information)

추가 지원 정보는 온라인 보충자료(Supporting Information) 섹션에서 확인할 수 있다.

## 인용 정보 (How to cite this article)

van den Berg CP, Troscianko J, Endler JA, Marshall NJ, Cheney KL. Quantitative Colour Pattern Analysis (QCPA): A comprehensive framework for the analysis of colour patterns in nature. *Methods in Ecology and Evolution*. 2020;11:316–332. [https://doi.org/10.1111/2041-210X.13328](https://doi.org/10.1111/2041-210X.13328)

---

### 그림 설명 요약 (Figure captions)

* **그림 1. QCPA 프레임워크 개요**: 입력(원뿔 포착 이미지; MICA로 생성) → 공간 분해능 모델링(AcuityView 2.0 또는 가우시안 컨볼루션) → RNL 순위 필터로 경계 복원 → (선택) RNL/나이브 베이즈 군집화 → CAA/BSA/VCA/LEIA/입자 분석 → ΔS 경계 영상, XYZ 색도·채도 영상, RNL 색좌표 컬러맵 등 시각화. 별표는 본 프레임워크에서 새롭게 도입·중대 개편된 단계.
* **그림 2. MICA 출력 예시(다중분광 스택)**: 각 스택은 QCPA를 위한 휘도 채널을 포함.
* **그림 3. 벌의 공간 분해능과 UV 정보 지각**: 인간 관찰 시(3a) vs 벌의 UV 감지(3b) vs 1 m에서 0.5 cpd 공간 분해능 모형(3c) vs 벌의 휘도 채널 자극(3d).
* **그림 4. 새(blue tit) 원뿔 채널 기반 재구성 및 처리 파이프라인**: (a) 원뿔 자극 기반 RGB 재구성 → (b) FFT 기반 분해능 필터링 → (c) RNL 순위 필터로 경계 복원 → (d) RNL 군집화. 벌 UV 채널에 대해서도 (e–h) 유사 파이프라인 데모.
* **그림 5. CAA 예시(꿀벌을 모방하는 난초 Ophrys ciliata)**: 분할된 패턴의 수평·수직 횡단선 전이 행렬을 통해 복잡성(오프대각 전이 비율)을 정량화.
* **그림 7. LEIA의 ΔS 경계 강도 시각화**: 색은 가상의 경계 탐지 수용체장의 각도, 강도는 대비 크기를 나타냄.
* **그림 8. 로그 변환 RNL 색좌표 공간의 컬러맵**: 축 라벨은 사용된 수용체 채널(lw, mw, sw 등)에 따라 자동 생성되며, ROI 점군 경계는 1 ΔS를 반영.
* **그림 9. 반대색 채널(X: 적-녹, Y: 청-황, Z: UV)과 채도 맵 시각화**: 각 픽셀의 축 상 위치와 무채점까지의 유클리드 거리를 통해 채도를 표현.

> **참고:** 본 번역은 본문·그림 설명·감사의 글·지원 정보·인용 정보를 ‘원문 그대로 누락 없이’ 한국어로 옮긴 것이며, 요청에 따라 참고문헌(References) 목록은 제외하였다. 용어의 정확성을 위해 주요 기술 용어의 원어를 괄호로 병기하였다.
