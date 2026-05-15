"""
의도적으로 실패하는 테스트 — DevOps Agent Webhook 트리거용
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    """이건 통과"""
    response = client.get("/health")
    assert response.status_code == 200


def test_get_orders():
    """이건 실패 — DB 연결 에러 발생"""
    response = client.get("/api/orders")
    assert response.status_code == 200  # 실제로는 500이 나옴


def test_order_count():
    """이것도 실패 — 위 테스트와 같은 이유"""
    response = client.get("/api/orders")
    data = response.json()
    assert data["count"] >= 0
