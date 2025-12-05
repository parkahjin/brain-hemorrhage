# app_ui_confusion_matrix_side_by_side.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# --------------------------
# 0️⃣ 페이지 설정
# --------------------------
st.set_page_config(
    page_title="🧠 뇌출혈 진단",  # 브라우저 탭 제목
    layout="wide"                 # 화면을 가로 전체 폭으로 사용
)
st.title("🧠 뇌출혈 조기 진단 시뮬레이션")  # 화면 상단 제목

# --------------------------
# 1️⃣ CSV 업로드
# --------------------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")
if uploaded_file:
    data = pd.read_csv(uploaded_file)  # CSV 파일 읽기
    
    # label 컬럼 존재 여부 체크
    if 'label' not in data.columns:
        st.error("CSV에 'label' 컬럼이 필요합니다.")
    else:
        # --------------------------
        # 2️⃣ 입력(X), 정답(y) 분리
        # --------------------------
        X = data.drop("label", axis=1)  # feature(입력 데이터)
        y = data["label"]               # target(정답 라벨)

        # 학습용/테스트용 데이터 분리
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,       # 20%를 테스트용
            random_state=42,     # 재현 가능하게 난수 고정
            stratify=y           # 클래스 비율 유지
        )

        # --------------------------
        # 3️⃣ 데이터 미리보기 / 학습 설정
        # --------------------------
        col1, col2 = st.columns([1,1])  # 좌우 2개 컬럼 생성

        with col1:
            st.subheader("📋 데이터 미리보기")
            st.dataframe(data.head())  # 데이터 앞부분 5줄 표시
            st.write(f"총 샘플: {len(data)} | 학습: {len(X_train)} | 테스트: {len(X_test)}")

        with col2:
            st.subheader("⚙️ 학습 설정")
            st.write("모델: XGBoost")
            st.write("n_estimators: 300, max_depth: 4")
            st.write("learning_rate: 0.05, subsample: 0.8, colsample_bytree: 0.8")

        # --------------------------
        # 4️⃣ 모델 학습 버튼
        # --------------------------
        if st.button("모델 학습 및 평가"):
            with st.spinner("모델 학습 중..."):  # 학습 중 로딩 스피너
                # XGBoost 모델 정의
                model = XGBClassifier(
                    n_estimators=300,         # 트리 300개
                    max_depth=4,              # 최대 깊이 4
                    learning_rate=0.05,       # 학습률
                    subsample=0.8,            # 데이터 샘플링 비율
                    colsample_bytree=0.8,     # 특성 샘플링 비율
                    objective='binary:logistic',  # 이진 분류
                    eval_metric='logloss',    # 손실 함수
                    random_state=42            # 재현 가능
                )
                model.fit(X_train, y_train)  # 모델 학습

                # 예측 확률 및 클래스 결정
                y_prob = model.predict_proba(X_test)[:, 1]  # 1 클래스 확률
                y_pred = (y_prob > 0.5).astype(int)          # Threshold 0.5

                # --------------------------
                # 5️⃣ 모델 성능 + Confusion Matrix 옆으로 배치
                # --------------------------
                st.subheader("📊 모델 성능 및 Confusion Matrix")
                col3, col4 = st.columns([1,1])  # 좌우 2개 컬럼 생성

                with col3:
                    # classification_report 출력
                    st.text(classification_report(y_test, y_pred))
                    # TP, TN, FP, FN 기반 Precision, Recall, F1-score 확인 가능

                with col4:
                    st.subheader("📈 Confusion Matrix")
                    # confusion_matrix 계산
                    # y_test: 실제 값, y_pred: 모델 예측 값
                    # 결과 배열 [[TN, FP], [FN, TP]]
                    cm = confusion_matrix(y_test, y_pred)

                    # 그래프 크기 설정
                    plt.figure(figsize=(4,3))  # Streamlit 화면에 맞게 조정

                    # Heatmap 시각화
                    sns.heatmap(
                        cm,
                        annot=True,    # 각 칸에 숫자 표시
                        fmt='d',       # 정수 표시
                        cmap='Blues',  # 파란색 계열
                        xticklabels=[0,1],  # x축 레이블
                        yticklabels=[0,1]   # y축 레이블
                    )

                    # X축, Y축 레이블 및 제목
                    plt.xlabel("Predicted label")  # 모델이 예측한 값
                    plt.ylabel("True label")       # 실제 값
                    plt.title("Confusion Matrix")
                    plt.tight_layout()  # 레이블 겹침 방지

                    # Streamlit 화면에 그래프 출력
                    st.pyplot(plt)

# --------------------------
# 🔹 Confusion Matrix 해석
# --------------------------
# TN = True Negative = 32 → 실제 0을 0으로 맞춤
# FP = False Positive = 2 → 실제 0을 1로 틀림
# FN = False Negative = 6 → 실제 1을 0으로 틀림
# TP = True Positive = 1 → 실제 1을 1로 맞춤
# 모델이 비출혈(0)은 잘 맞추지만, 출혈(1)은 거의 못 맞춤
# Precision, Recall, F1-score로 소수 클래스 성능 평가 가능
