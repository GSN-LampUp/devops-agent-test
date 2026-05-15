# DevOps Agent CI/CD Test

AWS DevOps Agent Webhook 연동 테스트용 레포입니다.
CI/CD 파이프라인이 실패하면 자동으로 DevOps Agent에게 조사를 요청합니다.

## 구조

```
├── app.py                    # 간단한 FastAPI 앱
├── tests/
│   └── test_app.py           # 의도적으로 실패하는 테스트
├── Dockerfile
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml            # CI 파이프라인 (실패 시 Webhook 전송)
```

## 테스트 방법

1. `tests/test_app.py`에 실패하는 테스트가 포함되어 있음
2. push하면 GitHub Actions가 실행됨
3. 테스트 실패 → Webhook이 DevOps Agent에게 전송됨
4. Agent가 자동으로 조사 시작

## Secrets 설정 필요

GitHub 레포 Settings → Secrets and variables → Actions에 추가:
- `DEVOPS_AGENT_WEBHOOK_URL`
- `DEVOPS_AGENT_WEBHOOK_SECRET`
