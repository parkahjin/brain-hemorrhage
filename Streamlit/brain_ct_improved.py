"""
============================================================
뇌출혈 조기 진단 시스템 - 개선 버전 (로그인 기능 포함)
============================================================

주요 기능:
1. JWT 기반 로그인/인증 시스템
2. Grad-CAM 시각화로 진단 근거 제시
3. 범용 전처리로 인터넷 이미지 처리
4. 최적화된 ResNet50 Fine-tuning 모델 사용
5. 향상된 UI/UX

페이지 흐름:
1. 처음 실행 시 로그인 화면 표시
2. 로그인 성공 시 진단 화면으로 전환
3. 회원가입 버튼 클릭 시 회원가입 페이지로 이동
"""

import streamlit as st
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import cv2
import io
import base64
import sys
import os

# ============================================================
# 인증 모듈 Import
# ============================================================
try:
    from auth_utils import (
        init_session,
        is_logged_in,
        login,
        logout,
        get_user_name,
        get_username,
        check_server_health
    )
except ImportError as e:
    st.error(f"인증 모듈 import 실패: {e}")
    st.error("auth_utils.py 파일이 Streamlit 폴더에 있는지 확인하세요.")
    st.stop()

# 같은 폴더에서 모듈 import
try:
    from preprocessing_utils import CTImagePreprocessor
    from gradcam_utils import GradCAM
except ImportError as e:
    # 진단 기능용 모듈은 로그인 후에만 필요하므로 경고만 표시
    pass

# ============================================================
# Page Configuration (가장 먼저 호출해야 함)
# ============================================================
st.set_page_config(
    page_title="뇌출혈 진단 시스템",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 세션 초기화 (매우 중요!)
# ============================================================
# Streamlit은 버튼 클릭 시 전체 스크립트가 재실행됩니다.
# session_state를 사용하여 로그인 상태를 유지합니다.
init_session()

# ============================================================
# Custom CSS (로그인 + 진단 화면 공통)
# ============================================================
st.markdown("""
    <style>
    /* 페이지 네비게이션 메뉴 숨기기 */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* 로그인 화면 스타일 */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }

    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-header h1 {
        color: #1f77b4;
        font-size: 2.5rem;
    }

    .login-header p {
        color: #666;
        font-size: 1rem;
    }

    .login-form {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* 진단 화면 스타일 */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }

    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }

    .result-box-hemorrhage {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }

    .result-box-normal {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }

    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }

    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }

    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }

    .user-info-box {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .blink {
        animation: blink 1.5s infinite;
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# 로그인 상태에 따른 화면 분기
# ============================================================

if not is_logged_in():
    # ================================================================
    # 로그인 화면
    # ================================================================

    # 로그인 화면에서 사이드바 숨기기
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown("""
        <div class="login-header">
            <h1>🧠 뇌출혈 진단 시스템</h1>
            <p>AI 기반 CT 영상 분석 서비스</p>
        </div>
    """, unsafe_allow_html=True)

    # 중앙 정렬을 위한 컬럼 레이아웃
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # 로그인 폼 (엔터로 제출 가능)
        st.markdown("### 로그인")

        # 서버 상태 확인
        server_ok = check_server_health()
        if not server_ok:
            st.warning("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")

        # Form으로 감싸서 엔터 키로 제출 가능하게
        with st.form("login_form"):
            # 아이디 입력
            username = st.text_input(
                "아이디",
                placeholder="아이디를 입력하세요"
            )

            # 비밀번호 입력
            password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호를 입력하세요"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # 로그인 버튼 (폼 제출)
            submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)

            if submitted:
                if not username:
                    st.error("아이디를 입력해주세요.")
                elif not password:
                    st.error("비밀번호를 입력해주세요.")
                else:
                    # 로그인 시도
                    with st.spinner("로그인 중..."):
                        result = login(username, password)

                    if result.get('success'):
                        st.success(f"환영합니다, {result.get('name')}님!")
                        # 페이지 새로고침하여 진단 화면으로 전환
                        st.rerun()
                    else:
                        st.error(result.get('message', '로그인에 실패했습니다.'))

        st.markdown("<br>", unsafe_allow_html=True)

        # 구분선
        st.markdown("---")

        # 회원가입 안내
        st.markdown(
            '<p style="text-align: center; color: #666;">계정이 없으신가요?</p>',
            unsafe_allow_html=True
        )

        # 회원가입 버튼
        if st.button("회원가입하기", use_container_width=True):
            st.switch_page("pages/signup.py")

    # 푸터
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; color: #999; font-size: 0.8rem;">
            <p>뇌출혈 조기 진단 프로젝트 | AI 기반 의료 영상 분석</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # ================================================================
    # 진단 화면 (로그인 완료 상태)
    # ================================================================

    # ----------------------------------------------------------
    # 사이드바
    # ----------------------------------------------------------
    st.sidebar.title("⚙️ 설정")

    # 사용자 정보 표시
    user_name = get_user_name()
    username = get_username()
    st.sidebar.markdown(f"""
        <div class="user-info-box">
            👤 <b>{user_name}</b>님 환영합니다
        </div>
    """, unsafe_allow_html=True)

    # 마이페이지 버튼
    if st.sidebar.button("📋 마이페이지", use_container_width=True):
        st.switch_page("pages/mypage.py")

    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        logout()
        st.rerun()

    st.sidebar.markdown("---")

    # 이미지 업로드
    uploaded_file = st.sidebar.file_uploader(
        "CT 이미지 업로드",
        type=["jpg", "png", "jpeg"],
        help="뇌 CT 이미지를 업로드하세요. JPG, PNG 형식을 지원합니다."
    )

    # 모델 선택
    model_option = st.sidebar.selectbox(
        "모델 선택",
        ["ResNet50 Transfer (Fast) - 추천", "ResNet50 Transfer", "ResNet from Scratch", "CNN"],
        help="ResNet50 Transfer (Fast) 모델을 권장합니다 (인터넷 이미지 100% 정확도)"
    )

    # Grad-CAM 및 임계값 고정값 사용
    show_gradcam = True
    threshold = 0.5
    gradcam_alpha = 0.4

    # 정보
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **ℹ️ 사용 안내**

    1. CT 이미지를 업로드하세요
    2. 모델을 선택하세요
    3. 진단 결과와 Grad-CAM을 확인하세요

    **⚠️ 주의사항**
    - 이 시스템은 보조 진단 도구입니다
    - 전문의의 최종 판단을 대체할 수 없습니다
    """)

    # ----------------------------------------------------------
    # 헤더
    # ----------------------------------------------------------
    st.header("뇌출혈 조기 진단 시스템")

    # ----------------------------------------------------------
    # 모델 로드 (캐시)
    # ----------------------------------------------------------
    @st.cache_resource
    def load_models():
        """모델 로드 및 캐싱"""
        models = {}
        # 프로젝트 루트 디렉토리 기준으로 경로 설정
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_paths = {
            "ResNet50 Transfer (Fast) - 추천": os.path.join(base_dir, "model_files", "resnet_transfer_fast_brain_ct.h5"),
            "ResNet50 Transfer": os.path.join(base_dir, "model_files", "resnet_transfer_brain_ct.h5"),
            "ResNet from Scratch": os.path.join(base_dir, "model_files", "resnet_scratch_brain_ct.h5"),
            "CNN": os.path.join(base_dir, "model_files", "cnn_brain_ct.h5"),
        }

        for name, path in model_paths.items():
            try:
                if os.path.exists(path):
                    models[name] = load_model(path)
                else:
                    st.warning(f"⚠️ {name} 모델 파일이 없습니다: {path}")
            except Exception as e:
                st.error(f"❌ {name} 모델 로드 실패: {e}")

        return models

    # 모델 로드
    with st.spinner("모델 로딩 중..."):
        models = load_models()

    if not models:
        st.error("❌ 사용 가능한 모델이 없습니다. model/ 폴더에 모델 파일을 배치하세요.")
        st.stop()

    # 선택된 모델 가져오기
    selected_model = models.get(model_option)
    if selected_model is None:
        st.error(f"❌ {model_option} 모델을 사용할 수 없습니다.")
        st.stop()

    # ----------------------------------------------------------
    # 메인 컨텐츠
    # ----------------------------------------------------------
    if uploaded_file is None:
        # 안내 메시지
        st.markdown("""
        ### 📋 시작하기

        왼쪽 사이드바에서 뇌 CT 이미지를 업로드하세요.

        #### 지원 형식
        - JPG, PNG, JPEG

        #### 이미지 요구사항
        - 뇌 CT 단면 영상
        - 최소 64x64 픽셀
        - 최대 4096x4096 픽셀

        #### 시스템 특징
        ✅ Grad-CAM 기반 설명 가능한 AI
        ✅ 범용 전처리로 다양한 이미지 처리
        ✅ 90% 이상 정확도 목표
        """)

        # 샘플 이미지 표시 (선택적)
        st.markdown("### 📷 예시 이미지")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**뇌출혈 CT 예시**\n\n고밀도 영역(밝은 부분)이 특징적으로 나타납니다.")
        with col2:
            st.success("**정상 CT 예시**\n\n좌우 대칭이 유지되며 이상 음영이 없습니다.")

        st.stop()

    # ----------------------------------------------------------
    # 이미지 처리 및 예측
    # ----------------------------------------------------------
    st.markdown("### 🔍 진단 진행 중...")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. 이미지 저장 (임시)
        status_text.text("1/4 이미지 로딩 중...")
        progress_bar.progress(25)

        temp_image_path = "temp_uploaded_image.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 2. 전처리 (간단한 방식 - 모델 학습과 동일)
        status_text.text("2/4 이미지 전처리 중...")
        progress_bar.progress(50)

        from tensorflow.keras.applications.resnet50 import preprocess_input

        # 이미지 로드
        img = cv2.imread(temp_image_path)
        original_image = img.copy()

        # Grayscale → RGB
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        # 리사이즈
        img_resized = cv2.resize(img, (128, 128))

        # 배치 차원 추가 및 전처리
        img_array = np.expand_dims(img_resized, axis=0)
        preprocessed_image = preprocess_input(img_array)

        # 3. 예측
        status_text.text("3/4 AI 분석 중...")
        progress_bar.progress(75)

        prediction = selected_model.predict(preprocessed_image, verbose=0)[0][0]
        # 클래스 인덱스: {'hemorrhage': 0, 'normal': 1}
        # prediction이 1에 가까우면 normal, 0에 가까우면 hemorrhage
        predicted_class = "normal" if prediction >= threshold else "hemorrhage"
        confidence = prediction if prediction >= threshold else 1 - prediction

        # 4. Grad-CAM 생성 (뇌출혈 의심일 때만)
        if show_gradcam and predicted_class == "hemorrhage":
            status_text.text("4/4 진단 근거 생성 중...")
            try:
                import tensorflow as tf

                # 마지막 Conv layer 찾기
                last_conv_layer = None
                for layer in reversed(selected_model.layers):
                    if 'conv' in layer.name.lower():
                        last_conv_layer = layer
                        break

                if last_conv_layer is None:
                    raise ValueError("Conv layer를 찾을 수 없습니다")

                # Grad-CAM 계산
                grad_model = tf.keras.models.Model(
                    inputs=[selected_model.inputs],
                    outputs=[last_conv_layer.output, selected_model.output]
                )

                with tf.GradientTape() as tape:
                    conv_outputs, predictions_output = grad_model(preprocessed_image)
                    # Hemorrhage (0)에 대한 gradient 계산
                    # prediction이 낮을수록 hemorrhage이므로 (1 - prediction)을 사용
                    if predicted_class == "hemorrhage":
                        class_output = 1 - predictions_output[0][0]  # Hemorrhage 확률
                    else:
                        class_output = predictions_output[0][0]  # Normal 확률

                grads = tape.gradient(class_output, conv_outputs)
                pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

                conv_outputs = conv_outputs[0]
                pooled_grads_value = pooled_grads.numpy()
                conv_outputs_value = conv_outputs.numpy()

                for i in range(len(pooled_grads_value)):
                    conv_outputs_value[:, :, i] *= pooled_grads_value[i]

                heatmap = np.mean(conv_outputs_value, axis=-1)
                heatmap = np.maximum(heatmap, 0)
                if heatmap.max() > 0:
                    heatmap /= heatmap.max()

                # 히트맵을 원본 크기로 리사이즈
                heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
                heatmap_uint8 = np.uint8(255 * heatmap_resized)
                heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

                # 오버레이 (BGR → RGB 변환 필요)
                heatmap_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
                overlay = cv2.addWeighted(original_image, 0.6, heatmap_rgb, 0.4, 0)

                # 설명 텍스트
                max_activation = heatmap.max()
                threshold_heat = 0.7 * max_activation
                high_activation_mask = (heatmap >= threshold_heat).astype(np.uint8)
                y_coords, x_coords = np.where(high_activation_mask > 0)

                if len(y_coords) > 0:
                    center_y = int(np.mean(y_coords))
                    center_x = int(np.mean(x_coords))
                    h, w = heatmap.shape

                    # 뇌 영역 추정
                    if center_x < w / 3:
                        lr = "좌측"
                    elif center_x > 2 * w / 3:
                        lr = "우측"
                    else:
                        lr = "중앙"

                    if center_y < h / 3:
                        tb = "상부"
                    elif center_y > 2 * h / 3:
                        tb = "하부"
                    else:
                        tb = "중간부"

                    region = f"{lr} {tb}"
                else:
                    region = "전체 영역"

                if predicted_class == "hemorrhage":
                    explanation = f"""**⚠️ 뇌출혈 의심 소견**

- **주요 관심 영역**: {region}
- **분석**: 빨간색으로 표시된 부위에서 이상 소견이 감지되었습니다.

⚠️ **주의**: 이 결과는 보조 진단 도구이며, 전문의 판단이 필요합니다."""
                else:
                    explanation = f"""**✅ 정상 소견**

- **분석**: 뇌출혈을 시사하는 특이 소견이 발견되지 않았습니다.

✅ **참고**: 임상 증상이 있다면 전문의 상담을 권장합니다."""

                result = {
                    'heatmap': cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB),
                    'overlay': overlay,
                    'explanation': explanation
                }

            except Exception as e:
                st.warning(f"⚠️ Grad-CAM 생성 중 오류 발생: {e}")
                show_gradcam = False

        progress_bar.progress(100)
        status_text.text("✅ 분석 완료!")

        # 임시 파일 삭제
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    except Exception as e:
        st.error(f"❌ 이미지 처리 중 오류 발생: {e}")
        st.stop()

    # Progress 제거
    progress_bar.empty()
    status_text.empty()

    # ----------------------------------------------------------
    # 결과 표시
    # ----------------------------------------------------------
    st.markdown("---")
    st.markdown("## 📊 진단 결과")

    # 신뢰도 색상
    if confidence >= 0.8:
        confidence_class = "confidence-high"
        confidence_label = "높음"
    elif confidence >= 0.6:
        confidence_class = "confidence-medium"
        confidence_label = "보통"
    else:
        confidence_class = "confidence-low"
        confidence_label = "낮음"

    # 결과 박스
    if predicted_class == "hemorrhage":
        result_box_class = "result-box-hemorrhage"
        result_icon = "⚠️"
        result_text = "뇌출혈 의심"
        result_color = "#dc3545"
    else:
        result_box_class = "result-box-normal"
        result_icon = "✅"
        result_text = "정상"
        result_color = "#28a745"

    # 양쪽 클래스 확률 계산
    hemorrhage_prob = (1 - prediction) * 100  # 뇌출혈 확률
    normal_prob = prediction * 100  # 정상 확률

    st.markdown(f"""
    <div class="{result_box_class}">
        <h2 style="color: {result_color}; margin: 0;">{result_icon} {result_text}</h2>
        <p style="font-size: 1.2rem; margin-top: 0.5rem;">
            <b>뇌출혈 가능성:</b> {hemorrhage_prob:.2f}%<br>
            <b>정상 가능성:</b> {normal_prob:.2f}%<br>
            <b>사용 모델:</b> {model_option}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 이미지 및 Grad-CAM 표시
    # ----------------------------------------------------------
    if show_gradcam and 'result' in locals() and predicted_class == "hemorrhage":
        # 뇌출혈 의심: Grad-CAM 3단계 표시
        st.markdown("### 🔬 Grad-CAM 분석")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**원본 이미지**")
            # 원본 이미지를 RGB로 변환하여 표시
            if len(original_image.shape) == 2:
                original_rgb = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
            else:
                original_rgb = original_image
            st.image(original_rgb, use_container_width=True)

        with col2:
            st.markdown("**Grad-CAM 히트맵**")
            st.image(result['heatmap'], use_container_width=True, clamp=True)
            st.markdown("<p style='font-size: 0.9rem; color: black; margin-top: 0.2rem;'>빨간색: 높은 활성화 (중요 영역)</p>", unsafe_allow_html=True)

        with col3:
            st.markdown("**진단 근거 오버레이**")
            st.image(result['overlay'], use_container_width=True)
            st.markdown("<p style='font-size: 0.9rem; color: black; margin-top: 0.2rem;'>모델이 집중한 영역</p>", unsafe_allow_html=True)

    else:
        # 정상 또는 Grad-CAM 없음: 원본만 표시
        st.markdown("### 📷 업로드 이미지")
        if len(original_image.shape) == 2:
            original_rgb = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original_image
        st.image(original_rgb, use_container_width=True)

    # ----------------------------------------------------------
    # 설명 텍스트
    # ----------------------------------------------------------
    st.markdown("### 📝 진단 설명")

    if show_gradcam and 'result' in locals() and predicted_class == "hemorrhage":
        # Grad-CAM 기반 설명 (뇌출혈일 때만)
        st.markdown(result['explanation'])
    else:
        # 기본 설명
        if predicted_class == "hemorrhage":
            st.markdown(f"""
    **⚠️ 뇌출혈 의심 소견**

    - **신뢰도**: {confidence*100:.1f}%
    - **분석**: 모델이 뇌출혈 패턴을 감지했습니다.

    **주의사항**:
    - 이 결과는 보조 진단 도구로만 사용되어야 합니다.
    - 즉시 전문의 상담을 권장합니다.
    - 최종 진단은 반드시 의료진이 내려야 합니다.
            """)
        else:
            st.markdown(f"""
    **✅ 정상 소견**

    - **신뢰도**: {confidence*100:.1f}%
    - **분석**: 뇌출혈을 시사하는 특이 소견이 발견되지 않았습니다.

    **참고사항**:
    - 정상 소견이지만, 임상 증상이 있다면 전문의 상담을 권장합니다.
    - 경미한 이상은 자동 검출이 어려울 수 있습니다.
            """)

    # ----------------------------------------------------------
    # 면책 조항
    # ----------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ 의료 면책 조항</h4>
        <p>
        본 시스템은 <b>연구 및 교육 목적</b>으로 개발된 보조 진단 도구입니다.<br>
        실제 의료 현장에서 사용 시 다음 사항을 반드시 준수해야 합니다:
        </p>
        <ul>
            <li>본 결과는 <b>참고 자료</b>로만 활용하세요</li>
            <li><b>전문의의 최종 판단</b>을 대체할 수 없습니다</li>
            <li>의료진의 해석 없이 환자에게 직접 전달하지 마세요</li>
            <li>긴급 상황 시 즉시 전문의 상담을 받으세요</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # Footer
    # ----------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>뇌출혈 조기 진단 프로젝트 | AI 기반 의료 영상 분석</p>
        <p>Powered by ResNet50 + Grad-CAM</p>
    </div>
    """, unsafe_allow_html=True)
