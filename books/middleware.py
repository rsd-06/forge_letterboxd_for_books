import time
import logging
from .mongo_service import log_request_to_mongo

logger = logging.getLogger('request_logger')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Capture client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        response = self.get_response(request)

        duration_ms = (time.time() - start_time) * 1000

        # Don't log static assets to avoid spamming logs
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            log_line = f"[{response.status_code}] {request.method} {request.path} ({ip}) - {duration_ms:.1f}ms"
            logger.info(log_line)
            # Store in MongoDB
            log_request_to_mongo(request.method, request.path, response.status_code, ip, duration_ms)

        return response
