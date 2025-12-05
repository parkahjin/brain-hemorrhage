package com.brain.hemorrhage.controller;

import com.brain.hemorrhage.dto.AuthResponse;
import com.brain.hemorrhage.dto.LoginRequest;
import com.brain.hemorrhage.dto.SignupRequest;
import com.brain.hemorrhage.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * ============================================================
 * 인증 API 컨트롤러
 * ============================================================
 *
 * 로그인, 회원가입 등 인증 관련 REST API를 제공합니다.
 *
 * API 목록:
 * ┌────────┬─────────────────────┬───────────────────────┐
 * │ Method │ Endpoint            │ 설명                  │
 * ├────────┼─────────────────────┼───────────────────────┤
 * │ POST   │ /api/auth/signup    │ 회원가입              │
 * │ POST   │ /api/auth/login     │ 로그인 (토큰 발급)    │
 * │ GET    │ /api/auth/validate  │ 토큰 유효성 검증      │
 * │ GET    │ /api/auth/health    │ 서버 상태 확인        │
 * └────────┴─────────────────────┴───────────────────────┘
 *
 * @RestController : @Controller + @ResponseBody
 *                   모든 메서드의 반환값을 JSON으로 변환
 * @RequestMapping : 이 컨트롤러의 기본 URL 경로 지정
 * @RequiredArgsConstructor : final 필드에 대한 생성자 자동 생성
 */
@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    /**
     * 인증 서비스 (비즈니스 로직 처리)
     */
    private final AuthService authService;

    /**
     * 회원가입 API
     *
     * 새 사용자를 등록합니다.
     *
     * @param request 회원가입 요청 데이터 (JSON)
     * @return 회원가입 결과
     *
     * 요청 예시:
     * POST /api/auth/signup
     * Content-Type: application/json
     * {
     *     "username": "testuser",
     *     "password": "password123",
     *     "name": "홍길동",
     *     "email": "hong@example.com"
     * }
     *
     * 성공 응답:
     * {
     *     "success": true,
     *     "message": "회원가입이 완료되었습니다. 로그인해주세요."
     * }
     *
     * 실패 응답:
     * {
     *     "success": false,
     *     "message": "이미 사용 중인 아이디입니다."
     * }
     *
     * @Valid : SignupRequest의 유효성 검증 어노테이션(@NotBlank 등) 활성화
     * @RequestBody : HTTP 요청 본문(JSON)을 SignupRequest 객체로 변환
     */
    @PostMapping("/signup")
    public ResponseEntity<AuthResponse> signup(@Valid @RequestBody SignupRequest request) {
        log.info("[API] 회원가입 요청 - 아이디: {}", request.getUsername());

        // 서비스 호출하여 회원가입 처리
        AuthResponse response = authService.signup(request);

        // 결과에 따라 HTTP 상태 코드 결정
        if (response.isSuccess()) {
            // 성공: 201 Created
            return ResponseEntity.status(201).body(response);
        } else {
            // 실패: 400 Bad Request
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 로그인 API
     *
     * 사용자 인증 후 JWT 토큰을 발급합니다.
     *
     * @param request 로그인 요청 데이터 (JSON)
     * @return 로그인 결과 (성공 시 JWT 토큰 포함)
     *
     * 요청 예시:
     * POST /api/auth/login
     * Content-Type: application/json
     * {
     *     "username": "testuser",
     *     "password": "password123"
     * }
     *
     * 성공 응답:
     * {
     *     "success": true,
     *     "message": "로그인 성공",
     *     "token": "eyJhbGciOiJIUzI1NiIs...",
     *     "username": "testuser",
     *     "name": "홍길동"
     * }
     *
     * 실패 응답:
     * {
     *     "success": false,
     *     "message": "아이디 또는 비밀번호가 올바르지 않습니다."
     * }
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        log.info("[API] 로그인 요청 - 아이디: {}", request.getUsername());

        // 서비스 호출하여 로그인 처리
        AuthResponse response = authService.login(request);

        // 결과에 따라 HTTP 상태 코드 결정
        if (response.isSuccess()) {
            // 성공: 200 OK
            return ResponseEntity.ok(response);
        } else {
            // 실패: 401 Unauthorized
            return ResponseEntity.status(401).body(response);
        }
    }

    /**
     * 토큰 유효성 검증 API
     *
     * JWT 토큰이 아직 유효한지 확인합니다.
     * Streamlit에서 페이지 새로고침 시 세션 유지 여부 확인에 사용됩니다.
     *
     * @param authHeader Authorization 헤더 값 (Bearer {token})
     * @return 검증 결과
     *
     * 요청 예시:
     * GET /api/auth/validate
     * Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
     *
     * 성공 응답 (토큰 유효):
     * {
     *     "success": true,
     *     "message": "토큰 유효",
     *     "username": "testuser",
     *     "name": "홍길동"
     * }
     *
     * 실패 응답 (토큰 만료/무효):
     * {
     *     "success": false,
     *     "message": "토큰이 유효하지 않습니다."
     * }
     *
     * @RequestHeader : HTTP 요청 헤더 값 추출
     * required = false : 헤더가 없어도 에러 발생하지 않음
     */
    @GetMapping("/validate")
    public ResponseEntity<AuthResponse> validateToken(
            @RequestHeader(value = "Authorization", required = false) String authHeader
    ) {
        log.info("[API] 토큰 검증 요청");

        // Authorization 헤더가 없거나 Bearer 형식이 아닌 경우
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(401).body(
                    AuthResponse.builder()
                            .success(false)
                            .message("토큰이 없습니다.")
                            .build()
            );
        }

        // "Bearer " 접두사 제거하여 토큰만 추출
        String token = authHeader.substring(7);

        // 서비스 호출하여 토큰 검증
        AuthResponse response = authService.validateToken(token);

        if (response.isSuccess()) {
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.status(401).body(response);
        }
    }

    /**
     * 서버 상태 확인 API (Health Check)
     *
     * 백엔드 서버가 정상 동작 중인지 확인합니다.
     * Streamlit에서 서버 연결 상태 확인에 사용할 수 있습니다.
     *
     * @return 서버 상태 메시지
     *
     * 요청 예시:
     * GET /api/auth/health
     *
     * 응답:
     * {
     *     "success": true,
     *     "message": "서버 정상 동작 중"
     * }
     */
    @GetMapping("/health")
    public ResponseEntity<AuthResponse> healthCheck() {
        log.debug("[API] 헬스 체크 요청");

        return ResponseEntity.ok(
                AuthResponse.builder()
                        .success(true)
                        .message("서버 정상 동작 중")
                        .build()
        );
    }
}
