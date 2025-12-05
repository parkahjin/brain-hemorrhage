package com.brain.hemorrhage.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * ============================================================
 * 사용자(User) 엔티티 클래스
 * ============================================================
 *
 * 데이터베이스의 'users' 테이블과 매핑되는 엔티티 클래스입니다.
 * JPA(Java Persistence API)를 사용하여 객체와 테이블을 자동 매핑합니다.
 *
 * 테이블 구조:
 * +-------------+---------------+-------------------------------+
 * | 컬럼명      | 타입          | 설명                          |
 * +-------------+---------------+-------------------------------+
 * | id          | BIGINT        | 기본키 (자동 증가)            |
 * | username    | VARCHAR(50)   | 로그인 아이디 (유니크)        |
 * | password    | VARCHAR(255)  | 암호화된 비밀번호             |
 * | name        | VARCHAR(100)  | 사용자 이름                   |
 * | email       | VARCHAR(100)  | 이메일 (유니크)               |
 * | created_at  | TIMESTAMP     | 생성 시간 (자동)              |
 * | updated_at  | TIMESTAMP     | 수정 시간 (자동)              |
 * +-------------+---------------+-------------------------------+
 *
 * Lombok 어노테이션 설명:
 * - @Data : Getter, Setter, toString, equals, hashCode 자동 생성
 * - @Builder : 빌더 패턴 자동 생성 (User.builder().username("...").build())
 * - @NoArgsConstructor : 기본 생성자 자동 생성 (JPA 필수)
 * - @AllArgsConstructor : 모든 필드를 받는 생성자 자동 생성
 */
@Entity                          // JPA 엔티티임을 표시
@Table(name = "users")           // 매핑할 테이블 이름 지정
@Data                            // Lombok: Getter/Setter 자동 생성
@Builder                         // Lombok: 빌더 패턴 지원
@NoArgsConstructor               // Lombok: 기본 생성자
@AllArgsConstructor              // Lombok: 전체 필드 생성자
public class User {

    /**
     * 사용자 고유 ID (Primary Key)
     *
     * @Id : 이 필드가 기본키(PK)임을 표시
     * @GeneratedValue : 값 자동 생성 전략 설정
     *   - IDENTITY : MySQL의 AUTO_INCREMENT 사용
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 로그인 아이디
     *
     * @Column 속성:
     * - nullable = false : NULL 불가 (필수 입력)
     * - unique = true : 중복 불가 (유니크 제약조건)
     * - length = 50 : 최대 50자
     */
    @Column(nullable = false, unique = true, length = 50)
    private String username;

    /**
     * 비밀번호 (BCrypt로 암호화되어 저장)
     *
     * BCrypt 해시는 약 60자이므로 255자 할당
     * 예: $2a$10$N9qo8uLOickgx2ZMRZoMy...
     */
    @Column(nullable = false, length = 255)
    private String password;

    /**
     * 사용자 실명
     */
    @Column(nullable = false, length = 100)
    private String name;

    /**
     * 이메일 주소
     *
     * 비밀번호 찾기 등 확장 기능에 사용 가능
     */
    @Column(nullable = false, unique = true, length = 100)
    private String email;

    /**
     * 계정 생성 시간
     *
     * @CreationTimestamp : 엔티티가 처음 저장될 때 자동으로 현재 시간 설정
     * updatable = false : 이후 수정 시에도 변경되지 않음
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    /**
     * 마지막 수정 시간
     *
     * @UpdateTimestamp : 엔티티가 수정될 때마다 자동으로 현재 시간으로 갱신
     */
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
