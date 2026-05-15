from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/orders")
def get_orders():
    # 의도적 버그: None을 반환해서 직렬화 에러 유발
    orders = fetch_orders_from_db()
    return {"orders": orders, "count": len(orders)}

def fetch_orders_from_db():
    """DB 연결 실패를 시뮬레이션"""
    raise ConnectionError("Failed to connect to database: timeout after 30s")
