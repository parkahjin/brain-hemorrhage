package com.brain.hemorrhage.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * ============================================================
 * 회원가입 요청 DTO (Data Transfer Object)
 * ============================================================
 *
 * 클라이언트(Streamlit)에서 회원가입 시 전송하는 데이터를 담는 클래스입니다.
 *
 * 요청 JSON 예시:
 * {
 *     "username": "newuser",
 *     "password": "securePassword123!",
 *     "name": "홍길동",
 *     "email": "hong@example.com"
 * }
 *
 * 유효성 검증 어노테이션:
 * - @NotBlank : 빈 값 불가
 * - @Size : 문자열 길이 제한
 * - @Email : 이메일 형식 검증
 */
@Data                   // Lombok: Getter/Setter/toString 자동 생성
@NoArgsConstructor      // Lombok: 기본 생성자 (JSON 역직렬화에 필요)
@AllArgsConstructor     // Lombok: 전체 필드 생성자
public class SignupRequest {

    /**
     * 로그인 아이디
     *
     * 제약조건:
     * - 필수 입력
     * - 4자 이상 20자 이하
     */
    @NotBlank(message = "아이디를 입력해주세요.")
    @Size(min = 4, max = 20, message = "아이디는 4자 이상 20자 이하로 입력해주세요.")
    private String username;

    /**
     * 비밀번호
     *
     * 제약조건:
     * - 필수 입력
     * - 6자 이상 (보안을 위해)
     *
     * 참고: 실제 운영에서는 더 복잡한 규칙 적용 권장
     * (대문자, 소문자, 숫자, 특수문자 조합 등)
     */
    @NotBlank(message = "비밀번호를 입력해주세요.")
    @Size(min = 6, message = "비밀번호는 6자 이상 입력해주세요.")
    private String password;

    /**
     * 사용자 이름 (실명)
     *
     * 제약조건:
     * - 필수 입력
     * - 2자 이상 50자 이하
     */
    @NotBlank(message = "이름을 입력해주세요.")
    @Size(min = 2, max = 50, message = "이름은 2자 이상 50자 이하로 입력해주세요.")
    private String name;

    /**
     * 이메일 주소
     *
     * 제약조건:
     * - 필수 입력
     * - 이메일 형식 (xxx@xxx.xxx)
     */
    @NotBlank(message = "이메일을 입력해주세요.")
    @Email(message = "올바른 이메일 형식이 아닙니다.")
    private String email;
}
