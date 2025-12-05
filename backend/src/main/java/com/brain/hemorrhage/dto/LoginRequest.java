package com.brain.hemorrhage.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * ============================================================
 * 로그인 요청 DTO (Data Transfer Object)
 * ============================================================
 *
 * 클라이언트(Streamlit)에서 로그인 시 전송하는 데이터를 담는 클래스입니다.
 *
 * DTO를 사용하는 이유:
 * 1. 엔티티(User)를 직접 노출하지 않아 보안성 향상
 * 2. 필요한 필드만 전송하여 네트워크 효율성 향상
 * 3. 입력값 검증(@Valid)을 DTO 레벨에서 처리
 *
 * 요청 JSON 예시:
 * {
 *     "username": "testuser",
 *     "password": "mypassword123"
 * }
 *
 * @NotBlank : null, 빈 문자열(""), 공백만 있는 문자열(" ") 모두 거부
 */
@Data                   // Lombok: Getter/Setter/toString 자동 생성
@NoArgsConstructor      // Lombok: 기본 생성자 (JSON 역직렬화에 필요)
@AllArgsConstructor     // Lombok: 전체 필드 생성자
public class LoginRequest {

    /**
     * 로그인 아이디
     *
     * @NotBlank : 빈 값이면 유효성 검사 실패
     * message : 검증 실패 시 반환할 오류 메시지
     */
    @NotBlank(message = "아이디를 입력해주세요.")
    private String username;

    /**
     * 비밀번호 (평문으로 전송, 서버에서 암호화된 값과 비교)
     */
    @NotBlank(message = "비밀번호를 입력해주세요.")
    private String password;
}
