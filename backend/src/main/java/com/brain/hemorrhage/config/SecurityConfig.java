package com.brain.hemorrhage.config;

import com.brain.hemorrhage.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * ============================================================
 * Spring Security 설정 클래스
 * ============================================================
 *
 * 애플리케이션의 보안 설정을 담당합니다.
 *
 * 주요 설정:
 * 1. 인증이 필요한 URL과 불필요한 URL 구분
 * 2. CSRF 비활성화 (REST API 특성)
 * 3. 세션 비사용 (JWT 사용)
 * 4. JWT 인증 필터 등록
 * 5. 비밀번호 암호화 방식 설정
 *
 * 보안 필터 체인 순서:
 * ┌─────────┐   ┌──────────────┐   ┌───────────────┐   ┌────────────┐
 * │ Request │ → │ CORS Filter  │ → │ JWT Filter    │ → │ Controller │
 * └─────────┘   └──────────────┘   └───────────────┘   └────────────┘
 *
 * @Configuration : 이 클래스가 설정 클래스임을 표시
 * @EnableWebSecurity : Spring Security 웹 보안 활성화
 */
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    /**
     * JWT 인증 필터 주입
     */
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    /**
     * 보안 필터 체인 설정
     *
     * HTTP 요청에 대한 보안 규칙을 정의합니다.
     *
     * @param http HttpSecurity 설정 객체
     * @return 구성된 SecurityFilterChain
     * @throws Exception 설정 오류 시
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                // ============================================================
                // 1. CSRF(Cross-Site Request Forgery) 비활성화
                // ============================================================
                // REST API는 상태를 저장하지 않고(stateless) 토큰 기반 인증을 사용하므로
                // CSRF 공격에 대한 취약점이 낮아 비활성화합니다.
                // (CSRF는 주로 세션 쿠키 기반 인증에서 문제가 됨)
                .csrf(AbstractHttpConfigurer::disable)

                // ============================================================
                // 2. 세션 관리 - STATELESS (세션 사용 안 함)
                // ============================================================
                // JWT를 사용하므로 서버 측 세션을 생성하지 않습니다.
                // 모든 요청은 JWT 토큰으로 인증 상태를 확인합니다.
                .sessionManagement(session ->
                        session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )

                // ============================================================
                // 3. URL 별 접근 권한 설정
                // ============================================================
                .authorizeHttpRequests(auth -> auth
                        // 인증 없이 접근 가능한 URL들
                        .requestMatchers(
                                "/api/auth/**",    // 로그인, 회원가입, 토큰 검증 API
                                "/error",          // 에러 페이지
                                "/favicon.ico"     // 파비콘
                        ).permitAll()

                        // 그 외 모든 요청은 인증 필요
                        // (현재는 인증 API만 있으므로 사실상 모든 API 허용 상태)
                        .anyRequest().authenticated()
                )

                // ============================================================
                // 4. JWT 인증 필터 등록
                // ============================================================
                // UsernamePasswordAuthenticationFilter 앞에 JWT 필터를 추가
                // 모든 요청에서 JWT 토큰을 먼저 검증
                .addFilterBefore(
                        jwtAuthenticationFilter,
                        UsernamePasswordAuthenticationFilter.class
                );

        return http.build();
    }

    /**
     * 비밀번호 암호화 인코더 Bean 등록
     *
     * BCrypt 알고리즘을 사용하여 비밀번호를 암호화합니다.
     *
     * BCrypt 특징:
     * 1. 단방향 해시 (복호화 불가능)
     * 2. Salt 자동 생성 (같은 비밀번호도 매번 다른 해시값)
     * 3. 연산 비용 조절 가능 (brute force 공격 방어)
     *
     * 사용 예:
     * - 암호화: passwordEncoder.encode("password123")
     *           → "$2a$10$N9qo8uLOickgx2ZMRZoMy..."
     * - 검증: passwordEncoder.matches("password123", encodedPassword)
     *           → true/false
     *
     * @return BCryptPasswordEncoder 인스턴스
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
