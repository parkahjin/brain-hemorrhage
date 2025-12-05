# AWS Lightsail 배포 가이드 - 뇌출혈 진단 시스템 v3.0

> **프로젝트**: 뇌출혈 조기 진단 시스템 (Spring Boot + Streamlit + MySQL)
> **작성일**: 2025년 12월
> **목적**: AWS Lightsail에서 백엔드(Spring Boot) + 프론트엔드(Streamlit) + DB(MySQL) 통합 배포

---

## 목차
1. [배포 아키텍처](#1-배포-아키텍처)
2. [버전 호환성 체크](#2-버전-호환성-체크)
3. [AWS Lightsail 인스턴스 생성](#3-aws-lightsail-인스턴스-생성)
4. [서버 초기 설정](#4-서버-초기-설정)
5. [MySQL 데이터베이스 설정](#5-mysql-데이터베이스-설정)
6. [프로젝트 배포](#6-프로젝트-배포)
7. [Spring Boot 백엔드 설정](#7-spring-boot-백엔드-설정)
8. [Streamlit 프론트엔드 설정](#8-streamlit-프론트엔드-설정)
9. [Nginx 리버스 프록시 설정](#9-nginx-리버스-프록시-설정)
10. [도메인 및 SSL 설정](#10-도메인-및-ssl-설정)
11. [systemd 서비스 등록](#11-systemd-서비스-등록)
12. [배포 후 설정 변경](#12-배포-후-설정-변경)
13. [문제 해결 가이드](#13-문제-해결-가이드)
14. [유지보수 명령어](#14-유지보수-명령어)
15. [배포 체크리스트](#15-배포-체크리스트)

---

## 1. 배포 아키텍처

### 1.1 전체 구조
```
사용자 브라우저
    ↓ HTTPS (443)
DuckDNS 도메인 (예: brain-hemorrhage.duckdns.org)
    ↓
AWS Lightsail (Ubuntu 24.04 LTS, 4GB RAM)
    ↓
Nginx (리버스 프록시, 포트 80/443)
    │
    ├── /api/* 요청 → Spring Boot (localhost:8080)
    │                      ↓
    │                  MySQL (localhost:3306)
    │
    └── /* 요청 → Streamlit (localhost:8501)
                     ↓
                 Spring Boot API 호출
```

### 1.2 포트 사용
| 서비스 | 포트 | 설명 |
|--------|------|------|
| Nginx | 80, 443 | 외부 접속 (HTTP/HTTPS) |
| Spring Boot | 8080 | 백엔드 API |
| Streamlit | 8501 | 프론트엔드 |
| MySQL | 3306 | 데이터베이스 |

---

## 2. 버전 호환성 체크

### 2.1 로컬 환경 vs 서버 환경
| 기술 | 로컬 (Windows) | 서버 (Ubuntu 24.04) | 호환성 |
|------|----------------|---------------------|--------|
| **Java** | 17.0.16 (Temurin) | openjdk-17-jdk | ✅ 동일 |
| **MySQL** | 8.0.42 | 8.0.x | ✅ 동일 |
| **Python** | 3.13.5 | 3.12.x (기본) | ✅ 호환됨 |
| **Streamlit** | 1.51.0 | 1.51.0 (pip) | ✅ 동일 |
| **TensorFlow** | 2.20.0 | 2.20.0 (pip) | ✅ 동일 |
| **Spring Boot** | 3.2.0 | 3.2.0 (JAR) | ✅ 동일 |

### 2.2 중요 사항
- **Java 17 필수**: Spring Boot 3.x는 Java 17 이상 필요
- **Python 3.12 사용**: TensorFlow 2.20.0은 Python 3.9~3.12 공식 지원
- **4GB RAM 권장**: TensorFlow + Spring Boot 동시 실행 시 메모리 필요

---

## 3. AWS Lightsail 인스턴스 생성

### 3.1 인스턴스 설정
```
플랫폼: Linux/Unix
운영체제: Ubuntu 24.04 LTS
플랜: $24/월
  - RAM: 4GB
  - CPU: 2 vCPU
  - SSD: 80GB
  - 전송량: 4TB
위치: 서울 (ap-northeast-2)
```

### 3.2 방화벽 설정 (Networking 탭)
```
SSH: 22 포트 (기본)
HTTP: 80 포트
HTTPS: 443 포트
Custom: 8080 포트 (Spring Boot, 테스트용)
Custom: 8501 포트 (Streamlit, 테스트용)
```

### 3.3 고정 IP 할당
1. Lightsail 콘솔 → Networking 탭
2. "Create static IP" 클릭
3. 인스턴스에 연결
4. IP 주소 기록 (예: `3.37.xxx.xxx`)

---

## 4. 서버 초기 설정

### 4.1 SSH 접속
```bash
# Lightsail 콘솔에서 "Connect using SSH" 클릭
# 또는 로컬에서
ssh ubuntu@[고정IP주소]
```

### 4.2 시스템 업데이트
```bash
sudo apt update
sudo apt upgrade -y
```

### 4.3 Java 17 설치
```bash
# OpenJDK 17 설치
sudo apt install openjdk-17-jdk -y

# 버전 확인 (반드시 17.x 확인)
java -version
# 출력: openjdk version "17.0.x" ...

# JAVA_HOME 설정
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc
```

### 4.4 MySQL 8.0 설치
```bash
# MySQL 서버 설치
sudo apt install mysql-server -y

# 버전 확인
mysql --version
# 출력: mysql Ver 8.0.x ...

# MySQL 서비스 시작 및 자동 시작 설정
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 4.5 Python 및 pip 설치
```bash
# Python 버전 확인 (Ubuntu 24.04는 3.12 기본 탑재)
python3 --version
# 출력: Python 3.12.x

# pip 및 venv 설치
sudo apt install python3-pip python3-venv -y
```

### 4.6 기타 필수 패키지 설치
```bash
# Nginx (웹서버)
sudo apt install nginx -y

# Git
sudo apt install git -y

# Maven (Spring Boot 빌드용)
sudo apt install maven -y

# 기타 유틸리티
sudo apt install curl wget unzip -y
```

### 4.7 설치 확인
```bash
# 모든 버전 한번에 확인
echo "=== 설치된 버전 확인 ==="
java -version 2>&1 | head -1
mysql --version
python3 --version
mvn -version | head -1
nginx -v 2>&1
git --version
```

---

## 5. MySQL 데이터베이스 설정

### 5.1 MySQL 보안 설정
```bash
sudo mysql_secure_installation
```

설정 항목:
```
- VALIDATE PASSWORD component: No (또는 Yes 후 LOW 선택)
- root 비밀번호 설정: [강력한 비밀번호 입력]
- Remove anonymous users: Yes
- Disallow root login remotely: Yes
- Remove test database: Yes
- Reload privilege tables: Yes
```

### 5.2 데이터베이스 및 사용자 생성
```bash
# MySQL 접속
sudo mysql -u root -p
```

```sql
-- 데이터베이스 생성
CREATE DATABASE brain_hemorrhage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 전용 사용자 생성 (보안상 root 대신 사용)
CREATE USER 'brainuser'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';

-- 권한 부여
GRANT ALL PRIVILEGES ON brain_hemorrhage.* TO 'brainuser'@'localhost';
FLUSH PRIVILEGES;

-- 확인
SHOW DATABASES;
SELECT user, host FROM mysql.user;

-- 종료
EXIT;
```

### 5.3 연결 테스트
```bash
mysql -u brainuser -p brain_hemorrhage
# 비밀번호 입력 후 접속되면 성공
```

---

## 6. 프로젝트 배포

### 6.1 GitHub에서 프로젝트 클론
```bash
cd ~

# 프로젝트 클론 (본인 GitHub 주소로 변경)
git clone https://github.com/your-username/brain-hemorrhage.git brain_project

# 폴더 구조 확인
ls -la ~/brain_project/
# backend/     - Spring Boot
# Streamlit/   - 프론트엔드
# model_files/ - 학습된 모델
# Dataset/     - 데이터셋 (선택)
```

### 6.2 모델 파일 확인
```bash
# 모델 파일이 있는지 확인 (용량이 커서 Git LFS 사용 권장)
ls -lh ~/brain_project/model_files/
# resnet_transfer_fast_brain_ct.h5 등
```

---

## 7. Spring Boot 백엔드 설정

### 7.1 application.yml 수정
```bash
nano ~/brain_project/backend/src/main/resources/application.yml
```

```yaml
# 서버 설정
server:
  port: 8080

spring:
  application:
    name: brain-hemorrhage-backend

  # MySQL 연결 설정 (서버 환경에 맞게 수정)
  datasource:
    url: jdbc:mysql://localhost:3306/brain_hemorrhage?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Seoul&characterEncoding=UTF-8
    username: brainuser                    # 위에서 생성한 사용자
    password: YourSecurePassword123!       # 위에서 설정한 비밀번호
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false                        # 운영 환경에서는 false 권장
    properties:
      hibernate:
        format_sql: false
        dialect: org.hibernate.dialect.MySQLDialect
    open-in-view: false

# JWT 설정 (운영 환경에서는 비밀키 변경 필수!)
jwt:
  secret: ProductionSecretKeyMustBeChangedToSomethingVeryLongAndSecure2025!@#$%
  expiration: 3600000

# 로깅 설정 (운영 환경)
logging:
  level:
    org.springframework.security: WARN
    org.hibernate: WARN
    com.brain.hemorrhage: INFO
```

### 7.2 JAR 파일 빌드
```bash
cd ~/brain_project/backend

# Maven 빌드 (테스트 스킵)
mvn clean package -DskipTests

# 빌드된 JAR 파일 확인
ls -lh target/*.jar
# hemorrhage-1.0.0.jar (약 40~50MB)
```

### 7.3 JAR 실행 테스트
```bash
# 테스트 실행
java -jar target/hemorrhage-1.0.0.jar

# 다른 터미널에서 API 테스트
curl http://localhost:8080/api/auth/health
# {"success":true,"message":"서버 정상 동작 중"}

# Ctrl+C로 종료
```

---

## 8. Streamlit 프론트엔드 설정

### 8.1 Python 가상환경 생성
```bash
# 가상환경 생성
python3 -m venv ~/streamlit_env

# 가상환경 활성화
source ~/streamlit_env/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

### 8.2 의존성 설치
```bash
cd ~/brain_project/Streamlit

# requirements.txt가 있는 경우
pip install -r requirements.txt

# 또는 직접 설치 (버전 명시)
pip install streamlit==1.51.0
pip install tensorflow==2.20.0
pip install opencv-python-headless==4.10.0.84
pip install numpy==1.26.4
pip install pandas==2.2.2
pip install requests==2.32.3
pip install Pillow==10.4.0
```

### 8.3 auth_utils.py API 주소 수정
```bash
nano ~/brain_project/Streamlit/auth_utils.py
```

```python
# localhost 대신 실제 서버 주소 사용
# 방법 1: 같은 서버면 localhost 유지 (권장)
API_BASE_URL = "http://localhost:8080"

# 방법 2: 도메인 사용 시
# API_BASE_URL = "https://brain-hemorrhage.duckdns.org"
```

### 8.4 Streamlit 실행 테스트
```bash
source ~/streamlit_env/bin/activate
cd ~/brain_project/Streamlit

streamlit run brain_ct_improved.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 `http://[서버IP]:8501` 접속하여 확인

---

## 9. Nginx 리버스 프록시 설정

### 9.1 Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/brain-hemorrhage
```

```nginx
server {
    listen 80;
    server_name brain-hemorrhage.duckdns.org;  # 본인 도메인으로 변경

    # Spring Boot API 요청 처리
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Streamlit 요청 처리 (기본)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Streamlit WebSocket 지원
    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

### 9.2 설정 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/brain-hemorrhage /etc/nginx/sites-enabled/

# 기본 사이트 비활성화
sudo rm -f /etc/nginx/sites-enabled/default

# 설정 문법 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 9.3 Apache2 충돌 해결 (필요시)
```bash
# Apache2가 80포트 사용 중이면
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl restart nginx
```

---

## 10. 도메인 및 SSL 설정

### 10.1 DuckDNS 설정
1. https://www.duckdns.org/ 접속
2. GitHub/Google 계정으로 로그인
3. 도메인 생성: `brain-hemorrhage` (원하는 이름)
4. IP 주소 입력: Lightsail 고정 IP

### 10.2 SSL 인증서 설치 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 발급 (도메인 본인 것으로 변경)
sudo certbot --nginx -d brain-hemorrhage.duckdns.org

# 이메일 입력
# 약관 동의 (Y)
# 뉴스레터 (N)
# HTTP → HTTPS 리다이렉트 (2번 선택)
```

### 10.3 자동 갱신 테스트
```bash
# 인증서는 90일마다 갱신 필요 (자동 설정됨)
sudo certbot renew --dry-run
```

---

## 11. systemd 서비스 등록

### 11.1 Spring Boot 서비스 생성
```bash
sudo nano /etc/systemd/system/springboot.service
```

```ini
[Unit]
Description=Spring Boot Brain Hemorrhage Backend
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/brain_project/backend
ExecStart=/usr/bin/java -jar /home/ubuntu/brain_project/backend/target/hemorrhage-1.0.0.jar
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# 환경 변수 (필요시)
Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"

[Install]
WantedBy=multi-user.target
```

### 11.2 Streamlit 서비스 생성
```bash
sudo nano /etc/systemd/system/streamlit.service
```

```ini
[Unit]
Description=Streamlit Brain Hemorrhage Frontend
After=network.target springboot.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/brain_project/Streamlit
Environment="PATH=/home/ubuntu/streamlit_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/streamlit_env/bin/streamlit run brain_ct_improved.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 11.3 서비스 등록 및 시작
```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start springboot
sudo systemctl start streamlit

# 부팅 시 자동 시작
sudo systemctl enable springboot
sudo systemctl enable streamlit

# 상태 확인
sudo systemctl status springboot
sudo systemctl status streamlit
```

---

## 12. 배포 후 설정 변경

### 12.1 Streamlit API 주소 변경
배포 후 Streamlit이 백엔드 API를 호출할 때 `localhost`가 아닌 도메인을 사용하도록 변경해야 할 수 있습니다.

```bash
nano ~/brain_project/Streamlit/auth_utils.py
```

```python
# 서버 내부 통신이므로 localhost 유지 (권장)
API_BASE_URL = "http://localhost:8080"

# 또는 Nginx를 통한 접근 (HTTPS 필요시)
# API_BASE_URL = "https://brain-hemorrhage.duckdns.org"
```

### 12.2 Spring Boot CORS 설정 확인
```bash
nano ~/brain_project/backend/src/main/java/com/brain/hemorrhage/config/CorsConfig.java
```

도메인 추가 확인:
```java
configuration.setAllowedOrigins(Arrays.asList(
    "http://localhost:8501",
    "http://localhost:8502",
    "https://brain-hemorrhage.duckdns.org"  // 실제 도메인 추가
));
```

변경 후 재빌드:
```bash
cd ~/brain_project/backend
mvn clean package -DskipTests
sudo systemctl restart springboot
```

---

## 13. 문제 해결 가이드

### 13.1 502 Bad Gateway
```bash
# Spring Boot 상태 확인
sudo systemctl status springboot
sudo journalctl -u springboot -n 50

# Streamlit 상태 확인
sudo systemctl status streamlit
sudo journalctl -u streamlit -n 50

# 재시작
sudo systemctl restart springboot
sudo systemctl restart streamlit
sudo systemctl restart nginx
```

### 13.2 MySQL 연결 실패
```bash
# MySQL 상태 확인
sudo systemctl status mysql

# 연결 테스트
mysql -u brainuser -p brain_hemorrhage

# 로그 확인
sudo tail -50 /var/log/mysql/error.log
```

### 13.3 Java 버전 오류
```bash
# 버전 확인
java -version

# Java 17이 아니면 설치
sudo apt install openjdk-17-jdk -y

# 기본 Java 변경
sudo update-alternatives --config java
```

### 13.4 메모리 부족
```bash
# 메모리 확인
free -h

# 스왑 메모리 추가 (필요시)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 13.5 TensorFlow 설치 오류
```bash
# 가상환경 활성화 확인
source ~/streamlit_env/bin/activate

# pip 업그레이드
pip install --upgrade pip

# TensorFlow 재설치
pip uninstall tensorflow -y
pip install tensorflow==2.20.0
```

### 13.6 포트 충돌 확인
```bash
# 포트 사용 현황
sudo netstat -tulpn | grep -E '80|443|8080|8501|3306'

# 특정 포트 사용 프로세스 확인
sudo lsof -i :8080
```

---

## 14. 유지보수 명령어

### 14.1 서비스 관리
```bash
# Spring Boot
sudo systemctl status springboot
sudo systemctl start springboot
sudo systemctl stop springboot
sudo systemctl restart springboot

# Streamlit
sudo systemctl status streamlit
sudo systemctl start streamlit
sudo systemctl stop streamlit
sudo systemctl restart streamlit

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx

# MySQL
sudo systemctl status mysql
sudo systemctl restart mysql
```

### 14.2 로그 확인
```bash
# Spring Boot 로그 (실시간)
sudo journalctl -u springboot -f

# Streamlit 로그 (실시간)
sudo journalctl -u streamlit -f

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# Nginx 접속 로그
sudo tail -f /var/log/nginx/access.log
```

### 14.3 코드 업데이트
```bash
cd ~/brain_project

# Git에서 최신 코드 받기
git pull origin main

# Spring Boot 재빌드
cd backend
mvn clean package -DskipTests

# 서비스 재시작
sudo systemctl restart springboot
sudo systemctl restart streamlit
```

### 14.4 시스템 모니터링
```bash
# 메모리 사용량
free -h

# CPU 사용량
top
# 또는
htop  # sudo apt install htop

# 디스크 사용량
df -h

# 프로세스 확인
ps aux | grep -E 'java|streamlit|mysql|nginx'
```

---

## 15. 배포 체크리스트

### 초기 배포
- [ ] Lightsail 인스턴스 생성 ($24/월, 4GB)
- [ ] 고정 IP 할당
- [ ] 방화벽 설정 (22, 80, 443, 8080, 8501)
- [ ] SSH 접속 확인
- [ ] 시스템 업데이트
- [ ] Java 17 설치 및 버전 확인
- [ ] MySQL 8.0 설치 및 보안 설정
- [ ] Python 3.12 확인
- [ ] Nginx 설치
- [ ] Git, Maven 설치
- [ ] 프로젝트 클론
- [ ] MySQL 데이터베이스 및 사용자 생성
- [ ] application.yml 수정 (DB 정보)
- [ ] Spring Boot JAR 빌드
- [ ] Python 가상환경 및 패키지 설치
- [ ] Nginx 리버스 프록시 설정
- [ ] DuckDNS 도메인 연결
- [ ] SSL 인증서 설치
- [ ] systemd 서비스 등록
- [ ] 브라우저 테스트 (HTTPS)

### 정기 점검 (주 1회)
- [ ] 서비스 상태 확인
- [ ] 로그 확인 (에러 여부)
- [ ] 디스크 용량 확인
- [ ] 메모리 사용량 확인
- [ ] SSL 인증서 만료일 확인 (90일)

### 문제 발생 시
1. `sudo systemctl status springboot streamlit nginx mysql`
2. `sudo journalctl -u [서비스명] -n 100`
3. 서비스 재시작
4. 로그 분석

---

## 핵심 요약

### 3줄 요약
1. **서버 사양**: $24/월, 4GB RAM, Ubuntu 24.04
2. **서비스 구성**: Nginx → Spring Boot (8080) + Streamlit (8501) → MySQL (3306)
3. **자동화**: systemd로 서비스 등록하면 서버 재부팅 시 자동 시작

### 필수 버전
```
Java: 17.x (필수)
MySQL: 8.0.x
Python: 3.12.x
TensorFlow: 2.20.0
Streamlit: 1.51.0
Spring Boot: 3.2.0
```

### 접속 URL
```
프론트엔드: https://brain-hemorrhage.duckdns.org/
백엔드 API: https://brain-hemorrhage.duckdns.org/api/
```

---

**작성자**: 뇌출혈 진단 프로젝트 팀
**최종 수정**: 2025년 12월
**참고**: lightsail_deployment_guide.md (호텔 예측 프로젝트)
