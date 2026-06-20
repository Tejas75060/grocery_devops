"""Prometheus metrics definitions and FastAPI middleware."""
import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter(
    "grocery_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "grocery_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)
ORDERS_PLACED = Counter(
    "grocery_orders_placed_total", "Total orders placed"
)
ORDERS_DELIVERED = Counter(
    "grocery_orders_delivered_total", "Total orders delivered"
)
ACTIVE_ORDERS = Gauge(
    "grocery_active_orders", "Orders not yet delivered or cancelled"
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        # Use the route template (not the raw path) to keep label cardinality low.
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response
