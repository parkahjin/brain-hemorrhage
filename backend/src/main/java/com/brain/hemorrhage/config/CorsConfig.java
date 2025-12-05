package com.brain.hemorrhage.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.Arrays;
import java.util.List;

/**
 * ============================================================
 * CORS (Cross-Origin Resource Sharing) 설정 클래스
 * ============================================================
 *
 * CORS란?
 * 브라우저 보안 정책으로, 다른 도메인/포트에서 오는 요청을 차단합니다.
 * Streamlit(8501)과 Spring Boot(8080)는 다른 포트를 사용하므로
 * CORS 설정 없이는 API 호출이 차단됩니다.
 *
 * 시나리오:
 * ┌─────────────────┐         ┌─────────────────┐
 * │ Streamlit       │  CORS   │ Spring Boot     │
 * │ localhost:8501  │ ──────→ │ localhost:8080  │
 * └─────────────────┘ 허용필요 └─────────────────┘
 *
 * CORS 요청 흐름:
 * 1. 브라우저가 Preflight 요청 (OPTIONS) 전송
 * 2. 서버가 허용된 Origin인지 확인 후 응답
 * 3. 브라우저가 실제 요청 (GET, POST 등) 전송
 *
 * 설정 항목:
 * - allowedOrigins: 허용할 출처 (도메인:포트)
 * - allowedMethods: 허용할 HTTP 메서드
 * - allowedHeaders: 허용할 요청 헤더
 * - allowCredentials: 쿠키 포함 여부
 * - maxAge: Preflight 결과 캐시 시간
 *
 * @Configuration : 이 클래스가 설정 클래스임을 표시
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    /**
     * 허용할 Origin 목록
     *
     * Streamlit 기본 포트: 8501
     * 개발 시 다른 포트 사용 가능성을 고려하여 여러 개 등록
     */
    private static final List<String> ALLOWED_ORIGINS = Arrays.asList(
            "http://localhost:8501",        // Streamlit 기본 포트
            "http://127.0.0.1:8501",        // localhost 대체 표현
            "http://localhost:8502",        // Streamlit 대체 포트
            "http://localhost:3000"         // 프론트엔드 개발 서버 (필요 시)
    );

    /**
     * 허용할 HTTP 메서드 목록
     */
    private static final List<String> ALLOWED_METHODS = Arrays.asList(
            "GET",      // 조회
            "POST",     // 생성
            "PUT",      // 전체 수정
            "PATCH",    // 부분 수정
            "DELETE",   // 삭제
            "OPTIONS"   // Preflight 요청
    );

    /**
     * 허용할 HTTP 헤더 목록
     */
    private static final List<String> ALLOWED_HEADERS = Arrays.asList(
            "Authorization",    // JWT 토큰
            "Content-Type",     // 요청 본문 타입 (application/json 등)
            "X-Requested-With", // AJAX 요청 표시
            "Accept",           // 응답 타입 지정
            "Origin",           // 요청 출처
            "Access-Control-Request-Method",   // Preflight 메서드 요청
            "Access-Control-Request-Headers"   // Preflight 헤더 요청
    );

    /**
     * Spring MVC CORS 설정
     *
     * 모든 API 경로에 대해 CORS 허용 규칙을 적용합니다.
     *
     * @param registry CORS 레지스트리
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry
                // 모든 경로에 CORS 적용
                .addMapping("/**")

                // 허용할 Origin 설정
                // Streamlit이 실행되는 주소들
                .allowedOrigins(ALLOWED_ORIGINS.toArray(new String[0]))

                // 허용할 HTTP 메서드
                .allowedMethods(ALLOWED_METHODS.toArray(new String[0]))

                // 허용할 요청 헤더
                .allowedHeaders("*")  // 모든 헤더 허용

                // 노출할 응답 헤더
                // 브라우저에서 접근 가능한 응답 헤더 지정
                .exposedHeaders("Authorization")

                // 자격 증명(쿠키, Authorization 헤더) 허용
                .allowCredentials(true)

                // Preflight 요청 결과 캐시 시간 (초)
                // 이 시간 동안 브라우저는 Preflight 요청을 다시 보내지 않음
                .maxAge(3600);  // 1시간
    }

    /**
     * CORS 설정 소스 Bean 등록
     *
     * Spring Security와 함께 사용하기 위한 설정입니다.
     * SecurityConfig의 필터 체인에서 이 설정을 사용합니다.
     *
     * @return CORS 설정 소스
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // 허용할 Origin
        configuration.setAllowedOrigins(ALLOWED_ORIGINS);

        // 허용할 HTTP 메서드
        configuration.setAllowedMethods(ALLOWED_METHODS);

        // 허용할 요청 헤더
        configuration.setAllowedHeaders(ALLOWED_HEADERS);

        // 노출할 응답 헤더
        configuration.setExposedHeaders(List.of("Authorization"));

        // 자격 증명 허용
        configuration.setAllowCredentials(true);

        // Preflight 캐시 시간
        configuration.setMaxAge(3600L);

        // 모든 경로에 이 설정 적용
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        return source;
    }
}
