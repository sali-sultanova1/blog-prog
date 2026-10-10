import logging
from django.core.cache import cache
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)
CACHE_ERRORS = (RedisError, OSError)

def delete_cache_safely(*keys):
    try:
        cache.delete_many(keys)
    except CACHE_ERRORS:
        logger.exception("Не удалось удалить записи из кеша.")

def cached_list(key, queryset, timeout=300):
    try:
        value = cache.get(key)
    except CACHE_ERRORS:
        logger.exception("Кеш недоступен при чтении.")
        value = None

    if value is not None:
        return value

    value = list(queryset)

    try:
        cache.set(key, value, timeout=timeout)
    except CACHE_ERRORS:
        logger.exception("Кеш недоступен при записи.")

    return value