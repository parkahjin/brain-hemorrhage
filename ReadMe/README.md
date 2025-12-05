# 뇌출혈 조기 진단 프로젝트

AI 기반 CT 영상 분석을 통한 뇌출혈 진단 보조 시스템

## 📋 목차
- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [모델 학습](#모델-학습)
- [테스트 방법](#테스트-방법)
- [성능](#성능)

---

## 🎯 프로젝트 개요

ResNet50 기반 딥러닝 모델을 사용하여 뇌 CT 영상에서 뇌출혈을 자동으로 감지하는 시스템입니다.

### 핵심 특징
- **정확도 목표**: 90% 이상
- **설명 가능한 AI**: Grad-CAM 기반 시각화
- **범용성**: 인터넷의 임의 CT 이미지 처리 가능
- **웹 인터페이스**: Streamlit 기반 사용자 친화적 UI

---

## ✨ 주요 기능

### 1. 정확도 90% 달성을 위한 최적화
- Kaggle/논문 성공 사례 기반 하이퍼파라미터 튜닝
- 2단계 Fine-tuning 전략
- Class imbalance 처리 (class weights)
- 강화된 Data Augmentation

### 2. 범용 이미지 처리
- 학습/추론 일관된 전처리 파이프라인
- DICOM 및 일반 이미지 형식 지원
- CT 특화 Window Leveling
- 자동 이미지 검증

### 3. Grad-CAM 기반 설명
- 진단 근거 시각화 (히트맵)
- 이상 부위 자동 탐지
- 뇌 영역 위치 추정
- 신뢰도 기반 설명 텍스트

### 4. Streamlit 웹 인터페이스
- 직관적인 이미지 업로드
- 실시간 진단 결과
- Grad-CAM 오버레이 표시
- 의료 면책 조항 포함

---

## 🔧 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd 뇌출혈
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 모델 파일 배치
학습된 모델을 `model/` 폴더에 배치:
```
model/
├── resnet50_final_optimized.h5  # 최적화 모델 (권장)
├── resnet_transfer_fast_brain_ct.h5
├── resnet_scratch_brain_ct.h5
└── cnn_brain_ct.h5
```

---

## 🚀 사용 방법

### 1. Streamlit 웹앱 실행
```bash
cd Streamlit
streamlit run brain_ct_improved.py
```

브라우저에서 `http://localhost:8501` 접속

### 2. 이미지 업로드 및 진단
1. 사이드바에서 CT 이미지 업로드
2. 모델 선택 (ResNet50 Fine-tuned 권장)
3. 결과 및 Grad-CAM 확인

### 3. Google Colab에서 모델 학습
```python
# Colab 노트북에서
!git clone <repository-url>
%cd 뇌출혈/Model_code

# 학습 코드 실행
!python ResNet50_Optimized_90percent.py
```

---

## 📁 프로젝트 구조

```
뇌출혈/
├── Dataset/                    # 데이터셋
│   ├── train/
│   │   ├── hemorrhage/        # 2,152장
│   │   └── normal/            # 3,371장
│   └── test/
│       ├── hemorrhage/        # 538장
│       └── normal/            # 843장
│
├── Model_code/                # 모델 학습 코드
│   ├── ResNet50_Optimized_90percent.py   # 최적화 학습 코드
│   ├── preprocessing_utils.py            # 전처리 모듈
│   ├── gradcam_utils.py                  # Grad-CAM 모듈
│   ├── 최적_하이퍼파라미터_정리.md        # 하이퍼파라미터 문서
│   ├── 전체 코드.txt                     # 기존 실험 코드
│   └── brain_ct.ipynb                   # Jupyter 노트북
│
├── Streamlit/                 # 웹 인터페이스
│   ├── brain_ct_improved.py   # 개선된 Streamlit 앱
│   └── brain_ct.py           # 기존 앱
│
├── Slide/                     # 발표 자료
│   └── 뇌출혈 조기 진단 프로젝트.pptx
│
├── model/                     # 학습된 모델 (생성 필요)
│   └── resnet50_final_optimized.h5
│
├── requirements.txt           # 패키지 목록
└── README.md                 # 이 문서
```

---

## 🧠 모델 학습

### 1. 데이터 준비
Google Drive에 데이터 업로드:
```
/content/drive/MyDrive/brain_ct/
├── train/
│   ├── hemorrhage/
│   └── normal/
└── test/
    ├── hemorrhage/
    └── normal/
```

### 2. Colab에서 학습 실행
```python
# Google Drive 마운트
from google.colab import drive
drive.mount('/content/drive')

# 학습 코드 실행
%run ResNet50_Optimized_90percent.py
```

### 3. 학습 설정 (하이퍼파라미터)
```python
# Learning Rate
initial_lr = 1e-4

# Epochs
epochs_stage1 = 5   # Top layers만
epochs_stage2 = 25  # Fine-tuning

# Data Augmentation
rotation_range = 20
zoom_range = 0.2
width_shift_range = 0.15
brightness_range = [0.8, 1.2]

# Class Weights
class_weights = {0: 1.0, 1: 1.3}
```

### 4. 학습 결과 확인
- `training_curves.png`: 학습 곡선
- `resnet50_final_optimized.h5`: 최종 모델
- Test Accuracy 출력

---

## 🧪 테스트 방법

### 1. 데이터셋 내 이미지 테스트
```python
from tensorflow.keras.models import load_model
from preprocessing_utils import CTImagePreprocessor

# 모델 로드
model = load_model('model/resnet50_final_optimized.h5')

# 전처리 및 예측
preprocessor = CTImagePreprocessor()
image = preprocessor.preprocess('path/to/ct_image.jpg')
prediction = model.predict(image)[0][0]

print(f"Prediction: {'hemorrhage' if prediction >= 0.5 else 'normal'}")
print(f"Confidence: {prediction:.4f}")
```

### 2. 인터넷 CT 이미지 테스트
인터넷에서 뇌 CT 이미지를 다운로드하여 테스트:

**추천 검색어**:
- "brain hemorrhage CT scan"
- "normal brain CT scan"
- "ICH CT image"

**테스트 절차**:
1. 이미지 다운로드 (JPG/PNG)
2. Streamlit 앱에 업로드
3. 결과 확인 (Grad-CAM 포함)

### 3. Grad-CAM 테스트
```python
from gradcam_utils import explain_with_gradcam

result = explain_with_gradcam(
    model=model,
    image_path='test_image.jpg',
    preprocessor=preprocessor,
    save_path='result_gradcam.jpg'
)

print(result['explanation'])
```

---

## 📊 성능

### 목표 성능
- **Test Accuracy**: ≥ 90%
- **Sensitivity**: ≥ 85% (뇌출혈 감지율)
- **Specificity**: ≥ 85% (정상 판별율)

### 현재 성능 (기존 모델)
| 모델 | Test Accuracy | 실제 예측 |
|------|---------------|-----------|
| CNN | 99.13% | ❌ 실패 (과적합) |
| ResNet from scratch | 84.50% | ❌ 실패 |
| ResNet50 Transfer | 80.45% | ❌ 실패 |
| **ResNet50 Fine-tuning** | **87.83%** | ✅ **성공** |

### 개선 목표
- ResNet50 Fine-tuning 최적화로 **90%+** 달성

---

## 🔍 추가 개선 사항

### 구현 완료
✅ 최적 하이퍼파라미터 적용
✅ 범용 전처리 파이프라인
✅ Grad-CAM 시각화
✅ 개선된 Streamlit UI

### 향후 개선 (선택)
- [ ] DICOM 형식 완전 지원
- [ ] Test-Time Augmentation (TTA)
- [ ] 모델 앙상블
- [ ] 다중 슬라이스 처리
- [ ] PDF 리포트 생성

---

## ⚠️ 주의사항

### 의료 면책
- 본 시스템은 **연구 및 교육 목적**입니다
- 실제 진단은 반드시 **전문의**가 수행해야 합니다
- 본 결과는 **보조 도구**로만 활용하세요

### 데이터 프라이버시
- 환자 개인정보 보호 필수
- 의료 데이터 사용 시 IRB 승인 필요

---

## 📚 참고 자료

### 성공 사례
- RSNA Intracranial Hemorrhage Detection (Kaggle)
- PMC Research Papers on ICH Detection
- GitHub: RSNA-Medical-Image-Detection

### 기술 스택
- TensorFlow/Keras
- ResNet50 (ImageNet pretrained)
- Grad-CAM
- Streamlit
- OpenCV, NumPy

---

## 👥 기여

이 프로젝트는 뇌출혈 조기 진단 연구의 일환으로 진행되었습니다.

---

## 📞 문의

프로젝트 관련 문의사항은 Issue를 통해 남겨주세요.

---

**마지막 업데이트**: 2025-11-25
