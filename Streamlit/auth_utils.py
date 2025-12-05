"""
============================================================
인증 유틸리티 모듈 (auth_utils.py)
============================================================

Streamlit 앱에서 JWT 기반 인증을 처리하는 유틸리티 함수들입니다.

주요 기능:
1. 세션 상태 초기화 및 관리
2. 로그인/로그아웃 처리
3. 회원가입 API 호출
4. JWT 토큰 검증

사용 방법:
    from auth_utils import init_session, login, logout, is_logged_in

    # 앱 시작 시 세션 초기화
    init_session()

    # 로그인 상태 확인
    if is_logged_in():
        # 로그인된 사용자 화면
        pass
    else:
        # 로그인 화면
        pass

중요 사항:
- Streamlit은 버튼 클릭 시 전체 스크립트가 재실행됩니다.
- st.session_state를 사용하여 JWT 토큰을 유지해야 합니다.
- 페이지 새로고침 시에도 세션 상태가 유지됩니다.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any

# ============================================================
# 설정 상수
# ============================================================

# 백엔드 서버 주소 (Spring Boot)
API_BASE_URL = "http://localhost:8080/api/auth"

# API 엔드포인트
LOGIN_URL = f"{API_BASE_URL}/login"
SIGNUP_URL = f"{API_BASE_URL}/signup"
VALIDATE_URL = f"{API_BASE_URL}/validate"
HEALTH_URL = f"{API_BASE_URL}/health"

# 요청 타임아웃 (초)
REQUEST_TIMEOUT = 10


# ============================================================
# 세션 관리 함수
# ============================================================

def init_session() -> None:
    """
    세션 상태 초기화

    Streamlit 앱 시작 시 호출하여 세션 변수들을 초기화합니다.
    이미 초기화된 경우 아무 작업도 하지 않습니다.

    초기화되는 세션 변수:
    - jwt_token: JWT 액세스 토큰
    - user_info: 사용자 정보 (username, name)
    - logged_in: 로그인 상태 플래그

    사용 예:
        # 앱 시작 부분에서 호출
        init_session()
    """
    # JWT 토큰 (로그인 시 저장, 로그아웃 시 삭제)
    if 'jwt_token' not in st.session_state:
        st.session_state.jwt_token = None

    # 사용자 정보 딕셔너리 {"username": "...", "name": "..."}
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    # 로그인 상태 플래그
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 현재 페이지 (login, signup, diagnosis)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'


def is_logged_in() -> bool:
    """
    로그인 상태 확인

    세션에 JWT 토큰이 있고 logged_in 플래그가 True인지 확인합니다.

    Returns:
        bool: True면 로그인 상태, False면 로그아웃 상태

    사용 예:
        if is_logged_in():
            st.write(f"환영합니다, {get_user_name()}님!")
        else:
            st.write("로그인이 필요합니다.")
    """
    return (
        st.session_state.get('logged_in', False) and
        st.session_state.get('jwt_token') is not None
    )


def get_user_name() -> Optional[str]:
    """
    로그인한 사용자 이름 반환

    Returns:
        Optional[str]: 사용자 이름 (로그인 안 된 경우 None)

    사용 예:
        name = get_user_name()
        if name:
            st.write(f"안녕하세요, {name}님!")
    """
    user_info = st.session_state.get('user_info')
    if user_info:
        return user_info.get('name')
    return None


def get_username() -> Optional[str]:
    """
    로그인한 사용자 아이디 반환

    Returns:
        Optional[str]: 사용자 아이디 (로그인 안 된 경우 None)
    """
    user_info = st.session_state.get('user_info')
    if user_info:
        return user_info.get('username')
    return None


def get_jwt_token() -> Optional[str]:
    """
    저장된 JWT 토큰 반환

    Returns:
        Optional[str]: JWT 토큰 문자열 (없으면 None)

    사용 예:
        token = get_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}
    """
    return st.session_state.get('jwt_token')


# ============================================================
# 인증 API 호출 함수
# ============================================================

def login(username: str, password: str) -> Dict[str, Any]:
    """
    로그인 API 호출

    백엔드 서버에 로그인 요청을 보내고, 성공 시 JWT 토큰을 세션에 저장합니다.

    Args:
        username: 사용자 아이디
        password: 비밀번호

    Returns:
        Dict: API 응답
            - success: True/False
            - message: 결과 메시지
            - token: JWT 토큰 (성공 시)
            - username: 사용자 아이디 (성공 시)
            - name: 사용자 이름 (성공 시)

    사용 예:
        result = login("testuser", "password123")
        if result['success']:
            st.success("로그인 성공!")
            st.rerun()  # 페이지 새로고침
        else:
            st.error(result['message'])
    """
    try:
        # POST 요청으로 로그인 시도
        response = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )

        # JSON 응답 파싱
        data = response.json()

        # 로그인 성공 시 세션에 저장
        if data.get('success'):
            st.session_state.jwt_token = data.get('token')
            st.session_state.user_info = {
                "username": data.get('username'),
                "name": data.get('name')
            }
            st.session_state.logged_in = True

        return data

    except requests.exceptions.ConnectionError:
        # 백엔드 서버 연결 실패
        return {
            "success": False,
            "message": "서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요."
        }

    except requests.exceptions.Timeout:
        # 요청 시간 초과
        return {
            "success": False,
            "message": "서버 응답 시간이 초과되었습니다."
        }

    except Exception as e:
        # 기타 오류
        return {
            "success": False,
            "message": f"로그인 중 오류가 발생했습니다: {str(e)}"
        }


def logout() -> None:
    """
    로그아웃 처리

    세션에서 JWT 토큰과 사용자 정보를 삭제합니다.

    사용 예:
        if st.button("로그아웃"):
            logout()
            st.rerun()
    """
    st.session_state.jwt_token = None
    st.session_state.user_info = None
    st.session_state.logged_in = False
    st.session_state.current_page = 'login'


def signup(username: str, password: str, name: str, email: str) -> Dict[str, Any]:
    """
    회원가입 API 호출

    백엔드 서버에 회원가입 요청을 보냅니다.

    Args:
        username: 사용자 아이디
        password: 비밀번호
        name: 사용자 이름
        email: 이메일 주소

    Returns:
        Dict: API 응답
            - success: True/False
            - message: 결과 메시지

    사용 예:
        result = signup("newuser", "password123", "홍길동", "hong@example.com")
        if result['success']:
            st.success(result['message'])
        else:
            st.error(result['message'])
    """
    try:
        # POST 요청으로 회원가입
        response = requests.post(
            SIGNUP_URL,
            json={
                "username": username,
                "password": password,
                "name": name,
                "email": email
            },
            timeout=REQUEST_TIMEOUT
        )

        return response.json()

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요."
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "서버 응답 시간이 초과되었습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"
        }


def validate_token() -> Dict[str, Any]:
    """
    JWT 토큰 유효성 검증

    저장된 JWT 토큰이 아직 유효한지 백엔드에 확인합니다.
    페이지 새로고침 시 세션 유지 여부 확인에 사용됩니다.

    Returns:
        Dict: API 응답
            - success: True/False (토큰 유효 여부)
            - message: 결과 메시지
            - username: 사용자 아이디 (유효한 경우)
            - name: 사용자 이름 (유효한 경우)

    사용 예:
        if get_jwt_token():
            result = validate_token()
            if not result['success']:
                logout()  # 토큰 만료 시 로그아웃
    """
    token = get_jwt_token()

    if not token:
        return {
            "success": False,
            "message": "토큰이 없습니다."
        }

    try:
        response = requests.get(
            VALIDATE_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT
        )

        data = response.json()

        # 토큰이 유효하지 않으면 세션 정리
        if not data.get('success'):
            logout()

        return data

    except Exception as e:
        return {
            "success": False,
            "message": f"토큰 검증 중 오류: {str(e)}"
        }


def check_server_health() -> bool:
    """
    백엔드 서버 상태 확인

    백엔드 서버가 정상 동작 중인지 확인합니다.

    Returns:
        bool: True면 서버 정상, False면 서버 다운

    사용 예:
        if not check_server_health():
            st.error("백엔드 서버에 연결할 수 없습니다.")
    """
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False


# ============================================================
# 페이지 전환 함수
# ============================================================

def go_to_signup() -> None:
    """
    회원가입 페이지로 이동

    사용 예:
        if st.button("회원가입"):
            go_to_signup()
            st.rerun()
    """
    st.session_state.current_page = 'signup'


def go_to_login() -> None:
    """
    로그인 페이지로 이동

    사용 예:
        if st.button("로그인으로 돌아가기"):
            go_to_login()
            st.rerun()
    """
    st.session_state.current_page = 'login'


def get_current_page() -> str:
    """
    현재 페이지 반환

    Returns:
        str: 'login', 'signup', 또는 'diagnosis'
    """
    return st.session_state.get('current_page', 'login')
