package com.brain.hemorrhage.repository;

import com.brain.hemorrhage.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * ============================================================
 * 사용자 Repository 인터페이스
 * ============================================================
 *
 * 데이터베이스의 users 테이블에 접근하는 인터페이스입니다.
 * JpaRepository를 상속받으면 기본적인 CRUD 메서드가 자동으로 제공됩니다.
 *
 * JpaRepository<User, Long> 의미:
 * - User : 다루는 엔티티 타입
 * - Long : 엔티티의 기본키(ID) 타입
 *
 * 자동 제공되는 메서드 (직접 구현 불필요):
 * - save(User user) : 저장 또는 수정
 * - findById(Long id) : ID로 조회
 * - findAll() : 전체 조회
 * - delete(User user) : 삭제
 * - count() : 전체 개수
 *
 * 쿼리 메서드 자동 생성:
 * Spring Data JPA는 메서드 이름을 분석하여 자동으로 SQL을 생성합니다.
 *
 * 예시:
 * - findByUsername(String username)
 *   → SELECT * FROM users WHERE username = ?
 *
 * - findByEmail(String email)
 *   → SELECT * FROM users WHERE email = ?
 *
 * - existsByUsername(String username)
 *   → SELECT COUNT(*) > 0 FROM users WHERE username = ?
 *
 * @Repository : 이 인터페이스가 데이터 접근 계층임을 표시
 *               (생략 가능하지만 명시적으로 표시)
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * 아이디(username)로 사용자 조회
     *
     * 로그인 시 사용자 존재 여부 확인에 사용됩니다.
     *
     * Optional을 반환하는 이유:
     * - 사용자가 없을 수도 있으므로 null 대신 Optional 사용
     * - NullPointerException 방지
     * - 호출하는 쪽에서 .isPresent(), .orElse() 등으로 안전하게 처리
     *
     * @param username 찾을 사용자 아이디
     * @return 사용자 Optional (없으면 Optional.empty())
     *
     * 생성되는 SQL:
     * SELECT * FROM users WHERE username = ?
     */
    Optional<User> findByUsername(String username);

    /**
     * 이메일로 사용자 조회
     *
     * 비밀번호 찾기 등 확장 기능에 사용할 수 있습니다.
     *
     * @param email 찾을 이메일 주소
     * @return 사용자 Optional (없으면 Optional.empty())
     *
     * 생성되는 SQL:
     * SELECT * FROM users WHERE email = ?
     */
    Optional<User> findByEmail(String email);

    /**
     * 아이디(username) 중복 확인
     *
     * 회원가입 시 이미 사용 중인 아이디인지 확인합니다.
     *
     * @param username 확인할 아이디
     * @return true: 이미 존재함, false: 사용 가능
     *
     * 생성되는 SQL:
     * SELECT COUNT(*) > 0 FROM users WHERE username = ?
     */
    boolean existsByUsername(String username);

    /**
     * 이메일 중복 확인
     *
     * 회원가입 시 이미 사용 중인 이메일인지 확인합니다.
     *
     * @param email 확인할 이메일
     * @return true: 이미 존재함, false: 사용 가능
     *
     * 생성되는 SQL:
     * SELECT COUNT(*) > 0 FROM users WHERE email = ?
     */
    boolean existsByEmail(String email);
}
