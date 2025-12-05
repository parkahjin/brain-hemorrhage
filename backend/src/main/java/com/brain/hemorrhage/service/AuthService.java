package com.brain.hemorrhage.service;

import com.brain.hemorrhage.dto.AuthResponse;
import com.brain.hemorrhage.dto.LoginRequest;
import com.brain.hemorrhage.dto.SignupRequest;
import com.brain.hemorrhage.entity.User;
import com.brain.hemorrhage.repository.UserRepository;
import com.brain.hemorrhage.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * ============================================================
 * 인증 서비스 클래스
 * ============================================================
 *
 * 로그인, 회원가입 등 인증 관련 비즈니스 로직을 처리하는 서비스입니다.
 *
 * 서비스 계층의 역할:
 * 1. 비즈니스 로직 처리 (Controller는 요청/응답만 담당)
 * 2. 트랜잭션 관리 (@Transactional)
 * 3. 여러 Repository 조합하여 복잡한 작업 수행
 *
 * 계층 구조:
 * ┌────────────┐
 * │ Controller │ → 요청 수신, 응답 반환
 * └─────┬──────┘
 *       ↓
 * ┌────────────┐
 * │  Service   │ → 비즈니스 로직 (여기!)
 * └─────┬──────┘
 *       ↓
 * ┌────────────┐
 * │ Repository │ → 데이터베이스 접근
 * └────────────┘
 *
 * @Service : 이 클래스가 서비스 계층임을 표시 (Spring Bean 등록)
 * @RequiredArgsConstructor : final 필드에 대한 생성자 자동 생성
 * @Transactional : 모든 메서드에 트랜잭션 적용
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)  // 기본적으로 읽기 전용 (쓰기 작업은 별도 지정)
public class AuthService {

    /**
     * 사용자 Repository (데이터베이스 접근)
     */
    private final UserRepository userRepository;

    /**
     * JWT 토큰 생성/검증
     */
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * 비밀번호 암호화 (BCrypt)
     *
     * SecurityConfig에서 Bean으로 등록된 PasswordEncoder 주입
     */
    private final PasswordEncoder passwordEncoder;

    /**
     * 회원가입 처리
     *
     * 새 사용자를 등록하고 데이터베이스에 저장합니다.
     *
     * @param request 회원가입 요청 DTO (username, password, name, email)
     * @return 회원가입 결과 응답
     *
     * 처리 과정:
     * 1. 아이디 중복 확인
     * 2. 이메일 중복 확인
     * 3. 비밀번호 암호화 (BCrypt)
     * 4. 사용자 정보 저장
     */
    @Transactional  // 쓰기 작업이므로 읽기 전용 해제
    public AuthResponse signup(SignupRequest request) {
        log.info("회원가입 시도 - 아이디: {}, 이메일: {}", request.getUsername(), request.getEmail());

        // 1. 아이디 중복 확인
        if (userRepository.existsByUsername(request.getUsername())) {
            log.warn("회원가입 실패 - 아이디 중복: {}", request.getUsername());
            return AuthResponse.signupFail("이미 사용 중인 아이디입니다.");
        }

        // 2. 이메일 중복 확인
        if (userRepository.existsByEmail(request.getEmail())) {
            log.warn("회원가입 실패 - 이메일 중복: {}", request.getEmail());
            return AuthResponse.signupFail("이미 사용 중인 이메일입니다.");
        }

        // 3. 비밀번호 암호화
        //    BCrypt 알고리즘으로 단방향 암호화 (복호화 불가)
        //    같은 비밀번호도 매번 다른 해시값 생성 (salt 포함)
        String encodedPassword = passwordEncoder.encode(request.getPassword());

        // 4. 사용자 엔티티 생성
        //    @Builder 패턴 사용으로 가독성 향상
        User user = User.builder()
                .username(request.getUsername())
                .password(encodedPassword)      // 암호화된 비밀번호 저장
                .name(request.getName())
                .email(request.getEmail())
                .build();

        // 5. 데이터베이스에 저장
        userRepository.save(user);

        log.info("회원가입 성공 - 아이디: {}", request.getUsername());
        return AuthResponse.signupSuccess();
    }

    /**
     * 로그인 처리
     *
     * 사용자 인증 후 JWT 토큰을 발급합니다.
     *
     * @param request 로그인 요청 DTO (username, password)
     * @return 로그인 결과 응답 (성공 시 JWT 토큰 포함)
     *
     * 처리 과정:
     * 1. 아이디로 사용자 조회
     * 2. 비밀번호 일치 여부 확인
     * 3. JWT 토큰 생성
     * 4. 응답 반환
     */
    public AuthResponse login(LoginRequest request) {
        log.info("로그인 시도 - 아이디: {}", request.getUsername());

        // 1. 아이디로 사용자 조회
        //    Optional을 사용하여 null 안전하게 처리
        User user = userRepository.findByUsername(request.getUsername())
                .orElse(null);

        // 2. 사용자가 없는 경우
        if (user == null) {
            log.warn("로그인 실패 - 존재하지 않는 아이디: {}", request.getUsername());
            // 보안: "아이디가 없습니다"라고 하면 아이디 존재 여부를 알려주게 되므로
            //       일반적인 메시지 사용
            return AuthResponse.loginFail("아이디 또는 비밀번호가 올바르지 않습니다.");
        }

        // 3. 비밀번호 일치 여부 확인
        //    passwordEncoder.matches(평문, 암호화된값)
        //    BCrypt는 salt를 포함하고 있어서 같은 비밀번호도 매번 다른 해시값을 가지지만
        //    matches() 메서드가 내부적으로 처리
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            log.warn("로그인 실패 - 비밀번호 불일치: {}", request.getUsername());
            return AuthResponse.loginFail("아이디 또는 비밀번호가 올바르지 않습니다.");
        }

        // 4. JWT 토큰 생성
        String token = jwtTokenProvider.createToken(user.getUsername());

        // 5. 성공 응답 반환
        log.info("로그인 성공 - 아이디: {}", request.getUsername());
        return AuthResponse.loginSuccess(token, user.getUsername(), user.getName());
    }

    /**
     * 토큰 유효성 검증
     *
     * Streamlit에서 페이지 새로고침 시 토큰이 여전히 유효한지 확인합니다.
     *
     * @param token 검증할 JWT 토큰
     * @return 검증 결과 응답
     */
    public AuthResponse validateToken(String token) {
        // 토큰 유효성 검증
        if (jwtTokenProvider.validateToken(token)) {
            String username = jwtTokenProvider.getUsername(token);

            // 사용자 정보 조회 (토큰은 유효하지만 DB에 사용자가 없는 경우 대비)
            User user = userRepository.findByUsername(username).orElse(null);

            if (user != null) {
                return AuthResponse.builder()
                        .success(true)
                        .message("토큰 유효")
                        .username(user.getUsername())
                        .name(user.getName())
                        .build();
            }
        }

        return AuthResponse.builder()
                .success(false)
                .message("토큰이 유효하지 않습니다.")
                .build();
    }
}
