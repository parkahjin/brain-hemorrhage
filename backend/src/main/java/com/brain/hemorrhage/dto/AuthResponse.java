package com.brain.hemorrhage.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * ============================================================
 * 인증 응답 DTO (Data Transfer Object)
 * ============================================================
 *
 * 로그인 성공 시 클라이언트(Streamlit)에게 반환하는 데이터를 담는 클래스입니다.
 *
 * 응답 JSON 예시 (로그인 성공):
 * {
 *     "success": true,
 *     "message": "로그인 성공",
 *     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
 *     "username": "testuser",
 *     "name": "홍길동"
 * }
 *
 * 응답 JSON 예시 (로그인 실패):
 * {
 *     "success": false,
 *     "message": "아이디 또는 비밀번호가 올바르지 않습니다.",
 *     "token": null,
 *     "username": null,
 *     "name": null
 * }
 *
 * @Builder : 빌더 패턴을 사용하여 객체 생성
 *            AuthResponse.builder().success(true).message("...").build()
 */
@Data                   // Lombok: Getter/Setter/toString 자동 생성
@Builder                // Lombok: 빌더 패턴 지원
@NoArgsConstructor      // Lombok: 기본 생성자
@AllArgsConstructor     // Lombok: 전체 필드 생성자
public class AuthResponse {

    /**
     * 요청 성공 여부
     *
     * true: 로그인/회원가입 성공
     * false: 실패 (오류 메시지 참조)
     */
    private boolean success;

    /**
     * 응답 메시지
     *
     * 성공: "로그인 성공", "회원가입 성공"
     * 실패: "아이디 또는 비밀번호가 올바르지 않습니다." 등
     */
    private String message;

    /**
     * JWT 액세스 토큰
     *
     * 로그인 성공 시에만 값이 있음
     * 이 토큰을 요청 헤더에 포함하여 인증이 필요한 API 호출
     *
     * 사용 방법:
     * Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     */
    private String token;

    /**
     * 로그인한 사용자 아이디
     *
     * 로그인 성공 시에만 값이 있음
     */
    private String username;

    /**
     * 로그인한 사용자 이름 (실명)
     *
     * 로그인 성공 시에만 값이 있음
     * UI에서 "OOO님 환영합니다" 같은 표시에 사용
     */
    private String name;

    /**
     * 로그인한 사용자 이메일
     *
     * 로그인 성공 시에만 값이 있음
     */
    private String email;

    /**
     * 계정 생성일 (가입일)
     *
     * 로그인 성공 시에만 값이 있음
     * 형식: "yyyy-MM-dd"
     */
    private String createdAt;

    // ============================================================
    // 편의 메서드: 자주 사용하는 응답 생성 헬퍼
    // ============================================================

    /**
     * 로그인 성공 응답 생성
     *
     * @param token JWT 토큰
     * @param username 사용자 아이디
     * @param name 사용자 이름
     * @param email 사용자 이메일
     * @param createdAt 가입일
     * @return 성공 응답 객체
     */
    public static AuthResponse loginSuccess(String token, String username, String name, String email, String createdAt) {
        return AuthResponse.builder()
                .success(true)
                .message("로그인 성공")
                .token(token)
                .username(username)
                .name(name)
                .email(email)
                .createdAt(createdAt)
                .build();
    }

    /**
     * 로그인 실패 응답 생성
     *
     * @param message 실패 사유
     * @return 실패 응답 객체
     */
    public static AuthResponse loginFail(String message) {
        return AuthResponse.builder()
                .success(false)
                .message(message)
                .build();
    }

    /**
     * 회원가입 성공 응답 생성
     *
     * @return 성공 응답 객체
     */
    public static AuthResponse signupSuccess() {
        return AuthResponse.builder()
                .success(true)
                .message("회원가입이 완료되었습니다. 로그인해주세요.")
                .build();
    }

    /**
     * 회원가입 실패 응답 생성
     *
     * @param message 실패 사유
     * @return 실패 응답 객체
     */
    public static AuthResponse signupFail(String message) {
        return AuthResponse.builder()
                .success(false)
                .message(message)
                .build();
    }
}
