import hashlib
import logging
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from .cache_utils import CACHE_ERRORS


logger = logging.getLogger(__name__)


def limit_posts(*, scope, limit, window):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method != "POST":
                return view(request, *args, **kwargs)

            address = request.META.get("REMOTE_ADDR", "unknown")
            digest = hashlib.sha256(address.encode("utf-8")).hexdigest()
            key = f"rate-limit:{scope}:{digest}"

            try:
                if cache.add(key, 1, timeout=window):
                    count = 1
                else:
                    count = cache.incr(key)
            except CACHE_ERRORS:
                logger.exception("Хранилище лимитов недоступно.")
                return JsonResponse({"detail": "Сервис временно недоступен."}, status=503)
            except ValueError:
                return JsonResponse({"detail": "Повторите запрос через несколько секунд."}, status=503)

            if count > limit:
                response = JsonResponse({"detail": "Слишком много попыток. Повторите позже."}, status=429)
                response["Retry-After"] = str(window)
                return response

            return view(request, *args, **kwargs)

        return wrapped

    return decorator