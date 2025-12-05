package com.brain.hemorrhage.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * ============================================================
 * JWT 토큰 생성 및 검증 클래스
 * ============================================================
 *
 * JWT(JSON Web Token)를 생성하고 검증하는 핵심 클래스입니다.
 *
 * JWT 구조:
 * ┌─────────────┬─────────────┬─────────────┐
 * │   Header    │   Payload   │  Signature  │
 * │ (알고리즘)  │ (사용자정보)│   (서명)    │
 * └─────────────┴─────────────┴─────────────┘
 *       ↓             ↓             ↓
 * eyJhbGciOiJI.eyJzdWIiOiJ0ZXN0.SflKxwRJSMeKKF2QT4fwpM
 *
 * 토큰 생성 과정:
 * 1. Header: 알고리즘(HS256), 타입(JWT) 지정
 * 2. Payload: 사용자 정보(username), 만료시간 등 포함
 * 3. Signature: Header + Payload를 비밀키로 서명
 *
 * 토큰 검증 과정:
 * 1. 서명 확인: 비밀키로 서명이 유효한지 확인
 * 2. 만료 확인: 현재 시간이 만료 시간 이전인지 확인
 * 3. 형식 확인: JWT 형식이 올바른지 확인
 *
 * @Slf4j : Lombok에서 제공하는 로깅 기능 (log.info(), log.error() 등)
 * @Component : Spring Bean으로 등록 (다른 클래스에서 주입받아 사용 가능)
 */
@Slf4j
@Component
public class JwtTokenProvider {

    /**
     * JWT 서명에 사용할 비밀키 (application.yml에서 읽어옴)
     *
     * @Value : application.yml의 jwt.secret 값을 주입
     * 보안 주의: 이 값은 절대 외부에 노출되면 안 됨!
     */
    @Value("${jwt.secret}")
    private String secretKeyString;

    /**
     * 토큰 유효 시간 (밀리초, application.yml에서 읽어옴)
     *
     * 기본값: 3600000ms = 1시간
     */
    @Value("${jwt.expiration}")
    private long validityInMilliseconds;

    /**
     * 실제 서명에 사용할 SecretKey 객체
     *
     * 문자열 비밀키를 SecretKey 객체로 변환하여 사용
     */
    private SecretKey secretKey;

    /**
     * 초기화 메서드 - Bean 생성 후 자동 호출
     *
     * @PostConstruct : 의존성 주입이 완료된 후 자동 실행
     * 비밀키 문자열을 SecretKey 객체로 변환
     */
    @PostConstruct
    protected void init() {
        // 문자열 비밀키를 바이트 배열로 변환 후 SecretKey 생성
        // HS256 알고리즘에는 최소 256비트(32바이트) 키 필요
        this.secretKey = Keys.hmacShaKeyFor(
                secretKeyString.getBytes(StandardCharsets.UTF_8)
        );
        log.info("JWT SecretKey 초기화 완료");
    }

    /**
     * JWT 토큰 생성
     *
     * 로그인 성공 시 호출되어 사용자에게 반환할 토큰을 생성합니다.
     *
     * @param username 토큰에 포함할 사용자 아이디
     * @return 생성된 JWT 토큰 문자열
     *
     * 토큰 구성:
     * - subject: 사용자 아이디 (토큰의 주체)
     * - issuedAt: 토큰 발급 시간
     * - expiration: 토큰 만료 시간
     * - signWith: 비밀키로 서명
     */
    public String createToken(String username) {
        // 현재 시간
        Date now = new Date();
        // 만료 시간 (현재 + 유효기간)
        Date validity = new Date(now.getTime() + validityInMilliseconds);

        // JWT 토큰 생성
        String token = Jwts.builder()
                .subject(username)          // 토큰 주체 (사용자 아이디)
                .issuedAt(now)              // 발급 시간
                .expiration(validity)        // 만료 시간
                .signWith(secretKey)         // 비밀키로 서명
                .compact();                  // 문자열로 압축

        log.info("JWT 토큰 생성 완료 - 사용자: {}", username);
        return token;
    }

    /**
     * 토큰에서 사용자 아이디 추출
     *
     * JWT 토큰을 파싱하여 저장된 사용자 아이디를 꺼냅니다.
     *
     * @param token JWT 토큰 문자열
     * @return 토큰에 저장된 사용자 아이디
     */
    public String getUsername(String token) {
        // 토큰 파싱 및 payload에서 subject(username) 추출
        return Jwts.parser()
                .verifyWith(secretKey)       // 비밀키로 서명 검증
                .build()
                .parseSignedClaims(token)    // 토큰 파싱
                .getPayload()                // payload 추출
                .getSubject();               // subject(username) 반환
    }

    /**
     * 토큰 유효성 검증
     *
     * 토큰이 유효한지 (서명 일치, 만료되지 않음, 형식 올바름) 확인합니다.
     *
     * @param token 검증할 JWT 토큰
     * @return true: 유효함, false: 유효하지 않음
     *
     * 검증 실패 케이스:
     * 1. 만료된 토큰 (ExpiredJwtException)
     * 2. 잘못된 서명 (SignatureException)
     * 3. 잘못된 형식 (MalformedJwtException)
     * 4. 지원하지 않는 토큰 (UnsupportedJwtException)
     * 5. 빈 토큰 (IllegalArgumentException)
     */
    public boolean validateToken(String token) {
        try {
            // 토큰 파싱 시도 (실패하면 예외 발생)
            Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token);

            log.debug("JWT 토큰 검증 성공");
            return true;

        } catch (ExpiredJwtException e) {
            // 토큰 만료
            log.warn("JWT 토큰 만료됨: {}", e.getMessage());
        } catch (SecurityException | MalformedJwtException e) {
            // 잘못된 서명 또는 형식
            log.warn("잘못된 JWT 토큰: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            // 지원하지 않는 토큰
            log.warn("지원하지 않는 JWT 토큰: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            // 빈 토큰
            log.warn("JWT 토큰이 비어있음: {}", e.getMessage());
        }

        return false;
    }

    /**
     * 토큰 만료 여부 확인
     *
     * @param token 확인할 JWT 토큰
     * @return true: 만료됨, false: 유효함
     */
    public boolean isTokenExpired(String token) {
        try {
            Date expiration = Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .getExpiration();

            return expiration.before(new Date());
        } catch (Exception e) {
            return true;  // 파싱 실패 시 만료된 것으로 처리
        }
    }
}
