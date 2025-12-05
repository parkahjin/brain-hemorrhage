# streamlit_brain_ct_app_sidebar_single_model.py
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import base64

st.set_page_config(layout="wide")

st.title("뇌출혈 조기 진단 프로젝트")
st.header("CNN과 ResNet 기반 뇌출혈 예측 모델 비교 연구")
st.write("사이드바에서 이미지를 업로드하고 모델을 선택하세요.")

# -----------------------------
# 1. 사이드바: 이미지 업로드
# -----------------------------
uploaded_file = st.sidebar.file_uploader("이미지 업로드", type=["jpg","png","jpeg"])

# -----------------------------
# 2. 사이드바: 모델 선택
# -----------------------------
model_option = st.sidebar.radio(
    "모델 선택",
    ("CNN", "ResNet from scratch", "ResNet50 transfer", "ResNet50 fine-tuned")
)

# -----------------------------
# 3. 모델 로드 (캐시)
# -----------------------------
@st.cache_resource
def load_models():
    cnn_model = load_model("model/cnn_brain_ct.h5")
    resnet_scratch = load_model("model/resnet_scratch_brain_ct.h5")
    resnet_transfer = load_model("model/resnet_transfer_brain_ct.h5")
    resnet_finetuned = load_model("model/resnet_transfer_fast_brain_ct.h5")
    return cnn_model, resnet_scratch, resnet_transfer, resnet_finetuned

cnn_model, resnet_scratch, resnet_transfer, resnet_finetuned = load_models()

# -----------------------------
# 4. 이미지 전처리 및 예측
# -----------------------------
if uploaded_file is not None:
    img = Image.open(uploaded_file).convert('RGB')

    # -----------------------------
    # 이미지 base64 변환 함수
    # -----------------------------
    def img_to_base64(img):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    img_base64 = img_to_base64(img)

    # 모델별 입력 크기 설정
    def get_img_array(model_name, img):
        size = (128, 128) if model_name == "ResNet50 fine-tuned" else (224, 224)
        img_array = image.img_to_array(img.resize(size))
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array

    # 예측 함수
    def predict_label(model, img_array):
        pred = model.predict(img_array)[0][0]
        label = "hemorrhage" if pred >= 0.5 else "normal"
        return label, pred

    # 모델 선택
    model = {
        "CNN": cnn_model,
        "ResNet from scratch": resnet_scratch,
        "ResNet50 transfer": resnet_transfer,
        "ResNet50 fine-tuned": resnet_finetuned
    }[model_option]

    img_array = get_img_array(model_option, img)
    label, pred = predict_label(model, img_array)

    st.write(f"### 선택 모델: {model_option}")

    # -----------------------------
    # 결과 텍스트 생성
    # -----------------------------
    if label == "hemorrhage":
        border_color = "red"
        animation = "blink"
        result_html = (
            "<h3 style='color:red;'>결과 예측 : 뇌출혈 가능성</h3>"
            "<p style='font-size:18px;'>"
            "<b><u>:: 모델이 뇌출혈로 판단한 이유:</u></b><br>"
            "1. CT 영상 내에서 <b><u>고밀도(밝은 부분)가 비정상적으로 강조</u></b>된 영역이 탐지될 때<br>"
            "2. 뇌 좌우 구조에서 <b><u>비대칭 패턴</u></b>이 감지될 때<br>"
            "3. 주변 조직의 <b><u>경계 흐림 또는 음영 변화</u></b>가 발생할 때<br><br>"
            "※ 본 모델의 설명은 학습용이며, 의학적 확진은 아닙니다."
            "</p>"
        )
    else:
        border_color = "green"
        animation = "none"
        result_html = (
            "<h3 style='color:green;'>결과 예측 : 정상</h3>"
            "<p style='font-size:18px;'>"
            "<b><u>:: 모델이 정상으로 판단한 이유:</u></b><br>"
            "1. CT 영상에서 <b><u>비정상적인 고밀도(밝은 부분)</u></b>가 발견되지 않았을 때<br>"
            "2. 좌우 뇌 구조가 <b><u>대칭적으로 유지</u></b>되어 구조적 이상이 보이지 않았을 때<br>"
            "3. 뇌조직 내 <b><u>부종, 경계 흐림, 음영 변화</u></b> 등이 나타나지 않았을 때<br><br>"
            "※ 경미한 이상은 자동검출이 어려울 수 있으므로 전문의 진단을 권장합니다."
            "</p>"
        )

    # -----------------------------
    # 깜박임 CSS (이미지 테두리)
    # -----------------------------
    animation_css = f"animation: {animation} 1s infinite;" if animation != "none" else ""
    st.markdown(
        f"""
        <style>
        @keyframes blink {{
            0% {{ border-color: {border_color}; }}
            50% {{ border-color: transparent; }}
            100% {{ border-color: {border_color}; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------
    # 좌우 배치: st.columns 사용
    # -----------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(
            f"""
            <div style="
                border: 5px solid {border_color};
                padding: 5px;
                {animation_css};
            ">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; height:auto;">
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(result_html, unsafe_allow_html=True)
