package com.brain.hemorrhage.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

/**
 * ============================================================
 * JWT 인증 필터 클래스
 * ============================================================
 *
 * 모든 HTTP 요청에서 JWT 토큰을 검증하는 필터입니다.
 * Spring Security의 필터 체인에 등록되어 자동으로 실행됩니다.
 *
 * 필터 실행 순서:
 * ┌─────────┐   ┌───────────────┐   ┌─────────────┐   ┌────────────┐
 * │ Request │ → │ JwtAuthFilter │ → │ 다른 필터들 │ → │ Controller │
 * └─────────┘   └───────────────┘   └─────────────┘   └────────────┘
 *
 * 동작 과정:
 * 1. 요청 헤더에서 "Authorization: Bearer {토큰}" 추출
 * 2. 토큰이 있으면 유효성 검증
 * 3. 유효하면 SecurityContext에 인증 정보 저장
 * 4. 유효하지 않거나 없으면 인증 없이 다음 필터로 진행
 *
 * OncePerRequestFilter:
 * - 한 요청당 한 번만 실행되는 것을 보장하는 필터
 * - 리다이렉트 등으로 같은 요청이 여러 번 처리되어도 필터는 1회만 실행
 *
 * @RequiredArgsConstructor : final 필드에 대한 생성자 자동 생성 (의존성 주입)
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    /**
     * JWT 토큰 처리를 위한 Provider 주입
     */
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * Authorization 헤더 이름
     */
    private static final String AUTHORIZATION_HEADER = "Authorization";

    /**
     * Bearer 토큰 접두사
     *
     * JWT 토큰은 일반적으로 "Bearer " 접두사와 함께 전송됨
     * 예: "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
     */
    private static final String BEARER_PREFIX = "Bearer ";

    /**
     * 필터 핵심 로직 - 모든 요청에서 실행
     *
     * @param request HTTP 요청 객체
     * @param response HTTP 응답 객체
     * @param filterChain 다음 필터로 요청을 전달하기 위한 체인
     * @throws ServletException 서블릿 예외
     * @throws IOException IO 예외
     */
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        try {
            // 1. 요청 헤더에서 JWT 토큰 추출
            String jwt = extractTokenFromRequest(request);

            // 2. 토큰이 존재하고 유효한 경우
            if (StringUtils.hasText(jwt) && jwtTokenProvider.validateToken(jwt)) {

                // 3. 토큰에서 사용자 아이디 추출
                String username = jwtTokenProvider.getUsername(jwt);

                // 4. 인증 객체 생성
                //    - principal: 사용자 아이디 (인증 주체)
                //    - credentials: null (비밀번호는 저장 안 함)
                //    - authorities: 빈 리스트 (역할/권한, 현재는 미사용)
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                username,               // principal (사용자 식별자)
                                null,                   // credentials (이미 인증됨)
                                Collections.emptyList() // authorities (권한 목록)
                        );

                // 5. 요청 정보를 인증 객체에 추가 (IP 주소, 세션 ID 등)
                authentication.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request)
                );

                // 6. SecurityContext에 인증 정보 저장
                //    이후 컨트롤러에서 @AuthenticationPrincipal 등으로 사용자 정보 접근 가능
                SecurityContextHolder.getContext().setAuthentication(authentication);

                log.debug("JWT 인증 성공 - 사용자: {}", username);
            }

        } catch (Exception e) {
            // 토큰 처리 중 예외 발생 시 로그만 남기고 계속 진행
            // (인증 실패로 처리되어 보호된 리소스 접근 시 403 응답)
            log.error("JWT 인증 처리 중 오류 발생: {}", e.getMessage());
        }

        // 7. 다음 필터로 요청 전달
        //    인증 성공/실패 여부와 관계없이 항상 호출해야 함
        filterChain.doFilter(request, response);
    }

    /**
     * 요청 헤더에서 JWT 토큰 추출
     *
     * Authorization 헤더에서 "Bearer " 접두사를 제거하고 토큰만 반환
     *
     * @param request HTTP 요청 객체
     * @return JWT 토큰 문자열 (없으면 null)
     *
     * 예시:
     * - 헤더: "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
     * - 반환: "eyJhbGciOiJIUzI1NiIs..."
     */
    private String extractTokenFromRequest(HttpServletRequest request) {
        // Authorization 헤더 값 가져오기
        String bearerToken = request.getHeader(AUTHORIZATION_HEADER);

        // "Bearer "로 시작하면 토큰 부분만 추출
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());  // "Bearer " 이후 문자열
        }

        return null;
    }
}
