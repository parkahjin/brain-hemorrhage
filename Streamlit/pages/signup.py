"""
============================================================
회원가입 페이지 (signup.py)
============================================================

새 사용자를 등록하는 회원가입 페이지입니다.

페이지 구성:
1. 아이디 입력
2. 비밀번호 입력
3. 비밀번호 확인
4. 이름 입력
5. 이메일 입력
6. 회원가입 버튼
7. 로그인 페이지로 이동 버튼

유효성 검사:
- 모든 필드 필수 입력
- 비밀번호 일치 확인
- 이메일 형식 확인 (간단한 검사)

실행 방법:
    이 파일은 직접 실행하지 않습니다.
    brain_ct_improved.py에서 페이지 전환으로 접근합니다.
"""

import streamlit as st
import sys
import os
import re
import time

# 상위 폴더의 모듈을 import하기 위해 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_utils import signup, init_session

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="회원가입 - 뇌출혈 진단 시스템",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 세션 초기화
# ============================================================
init_session()

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

    /* 전체 페이지 스타일 */
    .main {
        max-width: 500px;
        margin: 0 auto;
    }

    /* 헤더 스타일 */
    .signup-header {
        text-align: center;
        padding: 2rem 0;
    }

    .signup-header h1 {
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .signup-header p {
        color: #666;
        font-size: 1rem;
    }

    /* 폼 컨테이너 */
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* 입력 필드 라벨 */
    .field-label {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.3rem;
    }

    /* 도움말 텍스트 */
    .help-text {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
    }

    /* 성공 메시지 박스 */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* 에러 메시지 박스 */
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
    }

    /* 링크 스타일 */
    .login-link {
        text-align: center;
        margin-top: 1.5rem;
        color: #666;
    }

    .login-link a {
        color: #1f77b4;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 헤더
# ============================================================
st.markdown("""
    <div class="signup-header">
        <h1>🧠 회원가입</h1>
        <p>뇌출혈 진단 시스템에 오신 것을 환영합니다</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# 회원가입 폼
# ============================================================

# 아이디 입력
st.markdown('<p class="field-label">아이디</p>', unsafe_allow_html=True)
username = st.text_input(
    "아이디",
    placeholder="4자 이상 20자 이하",
    label_visibility="collapsed",
    key="signup_username"
)
st.markdown('<p class="help-text">영문, 숫자 조합 4~20자</p>', unsafe_allow_html=True)

# 비밀번호 입력
st.markdown('<p class="field-label">비밀번호</p>', unsafe_allow_html=True)
password = st.text_input(
    "비밀번호",
    type="password",
    placeholder="6자 이상",
    label_visibility="collapsed",
    key="signup_password"
)
st.markdown('<p class="help-text">6자 이상 입력해주세요</p>', unsafe_allow_html=True)

# 비밀번호 확인
st.markdown('<p class="field-label">비밀번호 확인</p>', unsafe_allow_html=True)
password_confirm = st.text_input(
    "비밀번호 확인",
    type="password",
    placeholder="비밀번호를 다시 입력하세요",
    label_visibility="collapsed",
    key="signup_password_confirm"
)

# 비밀번호 일치 여부 실시간 표시
if password and password_confirm:
    if password == password_confirm:
        st.success("비밀번호가 일치합니다.")
    else:
        st.error("비밀번호가 일치하지 않습니다.")

# 이름 입력
st.markdown('<p class="field-label">이름</p>', unsafe_allow_html=True)
name = st.text_input(
    "이름",
    placeholder="실명을 입력하세요",
    label_visibility="collapsed",
    key="signup_name"
)

# 이메일 입력
st.markdown('<p class="field-label">이메일</p>', unsafe_allow_html=True)
email = st.text_input(
    "이메일",
    placeholder="example@email.com",
    label_visibility="collapsed",
    key="signup_email"
)

# 이메일 형식 검사 (간단한 정규식)
if email:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        st.warning("올바른 이메일 형식을 입력해주세요.")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 회원가입 버튼
# ============================================================
if st.button("회원가입", type="primary", use_container_width=True):
    # 유효성 검사
    errors = []

    if not username:
        errors.append("아이디를 입력해주세요.")
    elif len(username) < 4 or len(username) > 20:
        errors.append("아이디는 4자 이상 20자 이하로 입력해주세요.")

    if not password:
        errors.append("비밀번호를 입력해주세요.")
    elif len(password) < 6:
        errors.append("비밀번호는 6자 이상 입력해주세요.")

    if not password_confirm:
        errors.append("비밀번호 확인을 입력해주세요.")
    elif password != password_confirm:
        errors.append("비밀번호가 일치하지 않습니다.")

    if not name:
        errors.append("이름을 입력해주세요.")
    elif len(name) < 2:
        errors.append("이름은 2자 이상 입력해주세요.")

    if not email:
        errors.append("이메일을 입력해주세요.")
    else:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("올바른 이메일 형식을 입력해주세요.")

    # 오류가 있으면 표시
    if errors:
        for error in errors:
            st.error(error)
    else:
        # 회원가입 API 호출
        with st.spinner("회원가입 처리 중..."):
            result = signup(username, password, name, email)

        if result.get('success'):
            st.success(result.get('message', '회원가입이 완료되었습니다!'))
            st.info("잠시 후 로그인 페이지로 이동합니다...")

            # 2초 대기 후 로그인 페이지로 자동 이동
            time.sleep(2)
            st.switch_page("brain_ct_improved.py")
        else:
            st.error(result.get('message', '회원가입에 실패했습니다.'))

# ============================================================
# 로그인 페이지로 이동 링크
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        '<p style="text-align: center; color: #666;">이미 계정이 있으신가요?</p>',
        unsafe_allow_html=True
    )
    if st.button("로그인하기", use_container_width=True):
        st.switch_page("brain_ct_improved.py")

# ============================================================
# 푸터
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.8rem;">
        <p>뇌출혈 조기 진단 프로젝트 | AI 기반 의료 영상 분석</p>
    </div>
""", unsafe_allow_html=True)
