import os

from redis import Redis


CACHE_LIFESPAN = int(os.getenv('CACHE_LIFESPAN', '3600'))
REDIS_HOST = os.getenv('REDIS_HOST')


class MockCacheClient:
    """Fake Redis client used if there is no cache implemented."""

    @staticmethod
    def get(*args, **kwargs):  # noqa
        return None

    @staticmethod
    def set(*args, **kwargs):  # noqa
        return None


class RedisExpireClient(Redis):
    """Redis client that automatically sets cache expirations."""

    def set(self, *args, **kwargs):
        kwargs.pop('ex', None)
        return super().set(*args, **kwargs)


redis_client = MockCacheClient()

if REDIS_HOST:
    redis_client = RedisExpireClient(host=REDIS_HOST, port=6379, db=0)
