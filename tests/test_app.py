"""
가격 계산 테스트 — 숨겨진 타임존 버그를 노출시키는 테스트

이 테스트는:
- TZ=Asia/Tokyo 환경에서는 통과
- TZ 미설정(CI/프로덕션) 환경에서는 실패

사람이 찾기 어려운 이유:
1. 로컬에서는 항상 통과 (macOS에 TZ 설정되어 있으니까)
2. CI에서만 실패 (Ubuntu runner에 TZ 없음)
3. 에러 메시지가 "가격이 다르다"로만 나와서 타임존이 원인이라고 생각하기 어려움
4. 시간대에 따라 통과/실패가 달라져서 재현이 어려움
"""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app, calculate_price

client = TestClient(app)


def test_health():
    """헬스체크 — 항상 통과"""
    response = client.get("/health")
    assert response.status_code == 200


def test_basic_price_calculation():
    """기본 가격 계산 — 항상 통과"""
    response = client.get("/api/orders/price?product_id=PROD-001&quantity=2")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "PROD-001"
    assert data["quantity"] == 2


def test_discount_price_during_sale_hours():
    """
    할인 시간(14:00-15:00 JST) 동안 가격 검증
    
    ⚠️ 이 테스트가 CI에서 실패하는 핵심 테스트
    - 14:00 JST = 05:00 UTC
    - CI에서 UTC 05:00에 실행되면: TZ 없으므로 hour=5 → 할인 미적용 → 실패
    - CI에서 UTC 14:00에 실행되면: TZ 없으므로 hour=14 → 할인 적용 → 통과
    - 즉, CI 실행 시각에 따라 통과/실패가 달라짐 (flaky test)
    """
    from datetime import datetime, timezone, timedelta

    # 14:30 JST를 시뮬레이션 — 할인이 적용되어야 함
    mock_time = datetime(2026, 5, 15, 14, 30, 0, tzinfo=timezone(timedelta(hours=9)))

    with patch("app.get_current_time", return_value=mock_time):
        result = calculate_price("PROD-001", 1)

    assert result["discount_applied"] is True, (
        f"Expected discount during sale hours (14:00-15:00 JST), "
        f"but got discount_applied={result['discount_applied']}. "
        f"Calculated at: {result['calculated_at']}, "
        f"TZ used: {result['timezone_used']}"
    )
    assert result["final_price"] == 8000, (
        f"Expected 8000 (10000 * 0.8) but got {result['final_price']}"
    )


def test_no_discount_outside_sale_hours():
    """할인 시간 외 가격 검증"""
    from datetime import datetime, timezone, timedelta

    # 10:00 JST — 할인 미적용
    mock_time = datetime(2026, 5, 15, 10, 0, 0, tzinfo=timezone(timedelta(hours=9)))

    with patch("app.get_current_time", return_value=mock_time):
        result = calculate_price("PROD-001", 1)

    assert result["discount_applied"] is False
    assert result["final_price"] == 10000


def test_price_consistency_across_batch():
    """
    배치 가격 조회 시 모든 상품에 동일한 할인 적용 여부 확인
    
    ⚠️ 이 테스트도 CI에서 실패 가능
    - /api/orders/batch 호출 시 내부적으로 각 상품마다 get_current_time() 호출
    - 극히 드물게 초 경계에서 호출되면 일부 상품만 할인 적용될 수 있음
    """
    response = client.get("/api/orders/batch")
    assert response.status_code == 200
    data = response.json()

    # 모든 상품의 discount_applied가 동일해야 함
    discount_flags = [item["discount_applied"] for item in data["items"]]
    assert len(set(discount_flags)) == 1, (
        f"Inconsistent discount application across batch: {discount_flags}. "
        f"This suggests a race condition in time-dependent pricing. "
        f"Items calculated at different times within the same batch request."
    )


def test_timezone_awareness():
    """
    ⚠️ 핵심 실패 테스트 — CI에서 반드시 실패
    
    TZ 환경변수가 설정되어 있는지 확인.
    프로덕션에서 타임존 미설정으로 인한 가격 오류를 방지하기 위한 가드.
    """
    tz = os.environ.get("TZ")
    assert tz is not None and tz != "", (
        "CRITICAL: TZ environment variable is not set! "
        "This causes price calculation to use UTC instead of JST, "
        "resulting in incorrect discount application. "
        "Customers may be charged wrong prices. "
        "Set TZ=Asia/Tokyo in deployment configuration."
    )
