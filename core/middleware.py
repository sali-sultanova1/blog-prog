import logging
import time

logger = logging.getLogger("requests")
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start_time
        log_path = "/verify-email/[redacted]/" if request.path.startswith("/verify-email/") else request.path

        logger.info("%s %s -> %s (%.3fs)", request.method, log_path, response.status_code, duration)

        return response