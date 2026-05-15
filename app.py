"""
Order Service — DevOps Agent 검증용
숨겨진 버그: 타임존 의존적 가격 계산 오류
"""
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta
import os

app = FastAPI()

# 가격 데이터 (정상)
PRODUCTS = {
    "PROD-001": {"name": "Widget A", "base_price": 10000},
    "PROD-002": {"name": "Widget B", "base_price": 25000},
    "PROD-003": {"name": "Widget C", "base_price": 50000},
}

# 할인 스케줄: 매일 14:00~15:00 (JST) 동안 20% 할인
DISCOUNT_START_HOUR = 14
DISCOUNT_END_HOUR = 15
DISCOUNT_RATE = 0.20


def get_current_time():
    """
    현재 시각을 반환.
    
    ⚠️ 숨겨진 버그: TZ 환경변수에 의존.
    - 로컬(macOS): TZ=Asia/Tokyo → JST 기준으로 정상 동작
    - CI(Ubuntu): TZ 미설정 → UTC 기준 → 할인 시간 계산 오류
    - 프로덕션(EKS): TZ 미설정 → UTC 기준 → 동일 오류
    
    결과: CI에서 14:00 JST에 테스트하면 통과하지만,
    실제로는 UTC 05:00에 할인이 적용되어 고객이 예상치 못한 가격을 받음
    """
    tz_name = os.environ.get("TZ", "")
    if tz_name == "Asia/Tokyo":
        return datetime.now(timezone(timedelta(hours=9)))
    else:
        # UTC로 동작 — 이게 버그의 원인
        return datetime.now(timezone.utc)


def calculate_price(product_id: str, quantity: int) -> dict:
    """
    가격 계산 — 할인 시간대에는 20% 할인 적용
    
    ⚠️ 숨겨진 버그: get_current_time()이 TZ에 따라 다른 시각을 반환하므로
    같은 시점에 호출해도 환경에 따라 할인 적용 여부가 달라짐
    """
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    product = PRODUCTS[product_id]
    base_price = product["base_price"]
    now = get_current_time()
    current_hour = now.hour

    discount_applied = False
    if DISCOUNT_START_HOUR <= current_hour < DISCOUNT_END_HOUR:
        final_price = int(base_price * (1 - DISCOUNT_RATE))
        discount_applied = True
    else:
        final_price = base_price

    total = final_price * quantity

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "base_price": base_price,
        "final_price": final_price,
        "quantity": quantity,
        "total": total,
        "discount_applied": discount_applied,
        "calculated_at": now.isoformat(),
        "timezone_used": os.environ.get("TZ", "UTC (default)"),
    }


@app.get("/health")
def health():
    return {"status": "ok", "timezone": os.environ.get("TZ", "not set")}


@app.get("/api/orders/price")
def get_price(product_id: str = "PROD-001", quantity: int = 1):
    return calculate_price(product_id, quantity)


@app.get("/api/orders/batch")
def batch_pricing():
    """여러 상품 일괄 가격 조회 — 내부적으로 시간 차이 발생 가능"""
    results = []
    for pid in PRODUCTS:
        results.append(calculate_price(pid, 1))
    return {"items": results, "batch_time": datetime.now(timezone.utc).isoformat()}
