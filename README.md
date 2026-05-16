# DevOps Agent CI/CD Test — Spring Boot ToDo App

AWS DevOps Agent Webhook 연동 테스트용 레포입니다.
CI/CD 파이프라인이 실패하면 자동으로 DevOps Agent에게 조사를 요청합니다.

## 구조

```
├── src/
│   ├── main/java/com/example/todo/
│   │   ├── TodoApplication.java          # Spring Boot 메인
│   │   ├── controller/
│   │   │   ├── TodoController.java       # REST API 엔드포인트
│   │   │   └── HealthController.java     # 헬스체크
│   │   ├── service/
│   │   │   └── TodoService.java          # 비즈니스 로직
│   │   ├── repository/
│   │   │   ├── TodoRepository.java       # Repository 인터페이스
│   │   │   └── InMemoryTodoRepository.java  # 인메모리 모의 구현
│   │   └── model/
│   │       └── Todo.java                 # 도메인 모델
│   ├── main/resources/
│   │   └── application.yml
│   └── test/java/com/example/todo/
│       ├── TodoApplicationTests.java
│       ├── controller/TodoControllerTest.java
│       └── service/TodoServiceTest.java
├── pom.xml
├── Dockerfile
└── .github/workflows/ci.yml
```

## API 엔드포인트

| Method | Path            | 설명           |
|--------|-----------------|----------------|
| GET    | /health         | 헬스체크       |
| GET    | /api/todos      | 전체 조회      |
| GET    | /api/todos/{id} | 단건 조회      |
| POST   | /api/todos      | 생성           |
| PUT    | /api/todos/{id} | 수정           |
| DELETE | /api/todos/{id} | 삭제           |

## 빌드 & 테스트

```bash
mvn clean package
mvn test
```

## Docker

```bash
docker build -t devops-agent-test-app .
docker run -p 8080:8080 devops-agent-test-app
```

## Secrets 설정 필요

GitHub 레포 Settings → Secrets and variables → Actions에 추가:
- `DEVOPS_AGENT_WEBHOOK_URL`
- `DEVOPS_AGENT_WEBHOOK_SECRET`
