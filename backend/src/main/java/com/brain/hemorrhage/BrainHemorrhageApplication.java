package com.brain.hemorrhage;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * ============================================================
 * 뇌출혈 진단 시스템 - 백엔드 메인 애플리케이션 클래스
 * ============================================================
 *
 * Spring Boot 애플리케이션의 시작점(Entry Point)입니다.
 * 이 클래스를 실행하면 내장 톰캣 서버가 시작되고,
 * 모든 Spring Bean들이 자동으로 초기화됩니다.
 *
 * @SpringBootApplication 어노테이션은 다음 3개를 합친 것입니다:
 * - @Configuration : 이 클래스가 설정 클래스임을 표시
 * - @EnableAutoConfiguration : Spring Boot 자동 설정 활성화
 * - @ComponentScan : 현재 패키지와 하위 패키지의 컴포넌트 스캔
 *
 * 실행 방법:
 * 1. STS에서 이 파일 우클릭 → Run As → Spring Boot App
 * 2. 또는 터미널에서: mvn spring-boot:run
 *
 * @author Brain Hemorrhage Diagnosis System
 * @version 1.0.0
 */
@SpringBootApplication
public class BrainHemorrhageApplication {

    /**
     * 애플리케이션 메인 메서드
     *
     * JVM이 가장 먼저 실행하는 메서드입니다.
     * SpringApplication.run()을 호출하여 Spring Boot를 시작합니다.
     *
     * @param args 커맨드 라인 인수 (사용하지 않음)
     */
    public static void main(String[] args) {
        // Spring Boot 애플리케이션 시작
        // - 내장 톰캣 서버 시작 (포트 8080)
        // - 모든 Bean 초기화
        // - 데이터베이스 연결
        SpringApplication.run(BrainHemorrhageApplication.class, args);

        // 시작 완료 메시지 출력
        System.out.println("============================================================");
        System.out.println("  뇌출혈 진단 시스템 백엔드 서버 시작 완료!");
        System.out.println("  서버 주소: http://localhost:8080");
        System.out.println("  API 테스트: http://localhost:8080/api/auth/...");
        System.out.println("============================================================");
    }
}
