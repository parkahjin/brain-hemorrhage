"""
============================================================
마이페이지 (mypage.py)
============================================================

환자 CT 이력 관리 및 추적 관찰 시스템 UI

주요 기능:
1. 내 정보 표시
2. 환자별 CT 이력 관리
3. 출혈 변화 추이 그래프
4. 이전 검사와 비교 화면

※ 현재는 더미 데이터로 UI만 구현 (향후 백엔드 연동 예정)
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# 상위 폴더의 모듈을 import하기 위해 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_utils import init_session, is_logged_in, get_user_name, get_username, logout

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="마이페이지 - 뇌출혈 진단 시스템",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 세션 초기화 및 로그인 확인
# ============================================================
init_session()

if not is_logged_in():
    st.warning("로그인이 필요합니다.")
    if st.button("로그인 페이지로 이동"):
        st.switch_page("brain_ct_improved.py")
    st.stop()

# ============================================================
# 더미 데이터 로드
# ============================================================
@st.cache_data
def load_sample_data():
    """더미 환자 데이터 로드"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_patients.json")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("샘플 데이터 파일을 찾을 수 없습니다.")
        return {"patients": []}

sample_data = load_sample_data()

# ============================================================
# CSS 스타일
# ============================================================
st.markdown("""
    <style>
    /* 페이지 네비게이션 및 사이드바 숨기기 */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        display: none;
    }

    /* 전체 페이지 */
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }

    /* 카드 스타일 */
    .info-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    .info-card h3 {
        color: #1f77b4;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }

    .info-item {
        display: flex;
        margin-bottom: 0.5rem;
    }

    .info-label {
        font-weight: bold;
        width: 80px;
        color: #555;
    }

    .info-value {
        color: #333;
    }

    /* 결과 뱃지 */
    .badge-hemorrhage {
        background-color: #dc3545;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }

    .badge-normal {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }

    /* 변화량 표시 */
    .change-positive {
        color: #28a745;
        font-weight: bold;
    }

    .change-negative {
        color: #dc3545;
        font-weight: bold;
    }

    /* 경고 박스 */
    .demo-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        text-align: center;
    }

    /* 이미지 비교 컨테이너 */
    .image-compare-container {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }

    .image-compare-title {
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 헤더
# ============================================================
col_header1, col_header2 = st.columns([4, 1])

with col_header1:
    st.markdown(f"<h1 class='main-header'>📋 마이페이지</h1>", unsafe_allow_html=True)
    st.markdown(f"**{get_user_name()}**님의 환자 관리 페이지")

with col_header2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 진단 화면으로", use_container_width=True):
        st.switch_page("brain_ct_improved.py")

st.markdown("---")

# ============================================================
# 메인 레이아웃 (좌측: 내 정보, 우측: 환자 CT 이력)
# ============================================================
col_left, col_right = st.columns([1, 3])

# ------------------------------------------------------------
# 좌측: 내 정보
# ------------------------------------------------------------
with col_left:
    st.markdown("### 👤 내 정보")

    st.markdown(f"""
    <div class="info-card">
        <div class="info-item">
            <span class="info-label">아이디</span>
            <span class="info-value">{get_username()}</span>
        </div>
        <div class="info-item">
            <span class="info-label">이름</span>
            <span class="info-value">{get_user_name()}</span>
        </div>
        <div class="info-item">
            <span class="info-label">이메일</span>
            <span class="info-value">-</span>
        </div>
        <div class="info-item">
            <span class="info-label">가입일</span>
            <span class="info-value">-</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 로그아웃 버튼
    if st.button("🚪 로그아웃", use_container_width=True):
        logout()
        st.switch_page("brain_ct_improved.py")

# ------------------------------------------------------------
# 우측: 환자 CT 이력 관리
# ------------------------------------------------------------
with col_right:
    st.markdown("### 🏥 환자 CT 이력 관리")

    # 환자 선택
    patients = sample_data.get("patients", [])
    patient_options = {f"{p['name']} ({p['patient_id']})": p for p in patients}

    selected_patient_key = st.selectbox(
        "환자 선택",
        options=list(patient_options.keys()),
        help="추적 관찰할 환자를 선택하세요"
    )

    if selected_patient_key:
        patient = patient_options[selected_patient_key]
        ct_records = patient.get("ct_records", [])

        # 환자 기본 정보
        st.markdown(f"""
        **환자 정보**: {patient['name']} | {patient['gender']} | 생년월일: {patient['birth_date']}
        """)

        st.markdown("---")

        if len(ct_records) > 0:
            # --------------------------------------------------------
            # 1. 출혈 변화 추이 그래프
            # --------------------------------------------------------
            st.markdown("#### 📈 출혈 부피 변화 추이")

            df = pd.DataFrame(ct_records)
            df['scan_date'] = pd.to_datetime(df['scan_date'])
            df = df.sort_values('scan_date')

            # Plotly 그래프
            fig = go.Figure()

            # 부피 라인
            fig.add_trace(go.Scatter(
                x=df['scan_date'],
                y=df['estimated_volume_cc'],
                mode='lines+markers+text',
                name='출혈 부피 (cc)',
                line=dict(color='#dc3545', width=3),
                marker=dict(size=12),
                text=[f"{v}cc" for v in df['estimated_volume_cc']],
                textposition='top center',
                textfont=dict(size=12, color='#dc3545')
            ))

            fig.update_layout(
                xaxis_title="촬영 날짜",
                yaxis_title="추정 출혈 부피 (cc)",
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(tickformat='%m/%d'),
                yaxis=dict(rangemode='tozero')
            )

            st.plotly_chart(fig, use_container_width=True)

            # --------------------------------------------------------
            # 2. CT 촬영 이력 테이블
            # --------------------------------------------------------
            st.markdown("#### 📋 CT 촬영 이력")

            # 테이블 데이터 생성
            table_data = []
            for record in ct_records:
                result_badge = "🔴 출혈" if record['result'] == 'hemorrhage' else "🟢 정상"
                table_data.append({
                    "촬영일": record['scan_date'],
                    "결과": result_badge,
                    "출혈 확률": f"{record['probability']*100:.0f}%",
                    "추정 부피": f"{record['estimated_volume_cc']}cc",
                    "위치": record['location']
                })

            st.dataframe(
                pd.DataFrame(table_data),
                use_container_width=True,
                hide_index=True
            )

            # --------------------------------------------------------
            # 3. 이전 검사와 비교
            # --------------------------------------------------------
            st.markdown("---")
            st.markdown("#### 🔍 이전 검사와 비교")

            if len(ct_records) >= 2:
                col_select1, col_select2 = st.columns(2)

                date_options = [r['scan_date'] for r in ct_records]

                with col_select1:
                    compare_date1 = st.selectbox(
                        "비교 검사 1 (이전)",
                        options=date_options,
                        index=0,
                        key="compare1"
                    )

                with col_select2:
                    compare_date2 = st.selectbox(
                        "비교 검사 2 (현재)",
                        options=date_options,
                        index=len(date_options)-1,
                        key="compare2"
                    )

                # 선택된 기록 찾기
                record1 = next((r for r in ct_records if r['scan_date'] == compare_date1), None)
                record2 = next((r for r in ct_records if r['scan_date'] == compare_date2), None)

                if record1 and record2:
                    col_img1, col_img2 = st.columns(2)

                    # 이미지 경로
                    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "sampledata")

                    with col_img1:
                        st.markdown(f"""
                        <div class="image-compare-container">
                            <div class="image-compare-title">📅 {record1['scan_date']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        img_path1 = os.path.join(base_path, record1['image'])
                        if os.path.exists(img_path1):
                            st.image(img_path1, use_container_width=True)
                        else:
                            st.info(f"이미지: {record1['image']}")

                        result_color1 = "#dc3545" if record1['result'] == 'hemorrhage' else "#28a745"
                        st.markdown(f"""
                        - **결과**: <span style="color:{result_color1}">{'출혈' if record1['result'] == 'hemorrhage' else '정상'}</span>
                        - **출혈 부피**: {record1['estimated_volume_cc']}cc
                        - **위치**: {record1['location']}
                        """, unsafe_allow_html=True)

                    with col_img2:
                        st.markdown(f"""
                        <div class="image-compare-container">
                            <div class="image-compare-title">📅 {record2['scan_date']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        img_path2 = os.path.join(base_path, record2['image'])
                        if os.path.exists(img_path2):
                            st.image(img_path2, use_container_width=True)
                        else:
                            st.info(f"이미지: {record2['image']}")

                        result_color2 = "#dc3545" if record2['result'] == 'hemorrhage' else "#28a745"
                        st.markdown(f"""
                        - **결과**: <span style="color:{result_color2}">{'출혈' if record2['result'] == 'hemorrhage' else '정상'}</span>
                        - **출혈 부피**: {record2['estimated_volume_cc']}cc
                        - **위치**: {record2['location']}
                        """, unsafe_allow_html=True)

                    # 변화량 계산 및 표시
                    st.markdown("---")
                    volume_change = record2['estimated_volume_cc'] - record1['estimated_volume_cc']

                    if record1['estimated_volume_cc'] > 0:
                        change_percent = (volume_change / record1['estimated_volume_cc']) * 100
                    else:
                        change_percent = 0

                    # 변화 상태 판단
                    if volume_change < 0:
                        status = "✅ 호전"
                        status_color = "#28a745"
                    elif volume_change > 0:
                        status = "⚠️ 악화"
                        status_color = "#dc3545"
                    else:
                        status = "➖ 유지"
                        status_color = "#6c757d"

                    col_result1, col_result2, col_result3 = st.columns(3)

                    with col_result1:
                        st.metric(
                            label="부피 변화",
                            value=f"{volume_change:+.1f}cc",
                            delta=f"{change_percent:+.1f}%"
                        )

                    with col_result2:
                        st.metric(
                            label="이전 → 현재",
                            value=f"{record1['estimated_volume_cc']}cc → {record2['estimated_volume_cc']}cc"
                        )

                    with col_result3:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem;">
                            <span style="font-size: 2rem; color: {status_color};">{status}</span>
                        </div>
                        """, unsafe_allow_html=True)

            else:
                st.info("비교를 위해서는 2개 이상의 CT 기록이 필요합니다.")

        else:
            st.info("등록된 CT 기록이 없습니다.")

# ============================================================
# 하단 안내 메시지
# ============================================================
st.markdown("""
<div class="demo-warning">
    <strong>⚠️ 시연용 샘플 데이터</strong><br>
    현재 표시되는 데이터는 시연용 샘플 데이터입니다.<br>
    실제 환자 데이터 연동 및 정확한 출혈 부피 측정 기능은 향후 업데이트 예정입니다.
</div>
""", unsafe_allow_html=True)

# ============================================================
# 푸터
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8rem;">
    뇌출혈 조기 진단 프로젝트 | AI 기반 의료 영상 분석 | v4.0
</div>
""", unsafe_allow_html=True)
