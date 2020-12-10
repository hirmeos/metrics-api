import json
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


class RedisMetricsClient(Redis):
    """Redis client that converts values to JSON and sets cache expirations."""

    def set(self, *args, **kwargs):
        raise NotImplementedError(
            f'Please use {self.__class__.__name__}.set_as_json().'
        )

    def get(self, *args, **kwargs):
        raise NotImplementedError(
            f'Please use {self.__class__.__name__}.get_from_json().'
        )

    def set_as_json(self, name, value, *args, **kwargs):
        """Convert value to json before caching."""
        kwargs.update(ex=kwargs.get('ex', CACHE_LIFESPAN))
        return super().set(name, json.dumps(value), *args, **kwargs)

    def get_from_json(self, *args, **kwargs):
        """Load values that have been converted to json before caching."""
        value = super().get(*args, **kwargs)

        if value:
            value = json.loads(value)

        return value


redis_client = MockCacheClient()

if REDIS_HOST:
    redis_client = RedisMetricsClient(host=REDIS_HOST, port=6379, db=0)
