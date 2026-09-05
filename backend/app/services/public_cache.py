from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import cast

from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class TaggedPublicCache:
    """Redis response cache with bounded, explicit invalidation tag sets.

    Payloads are addressed by a deterministic caller-supplied key.  Tag sets contain
    only VOLUMA cache keys and are iterated with SCAN, never Redis KEYS.
    """

    key_prefix = "voluma:cache:"
    tag_prefix = "voluma:cache:tag:"

    def __init__(self, client: Redis, *, ttl_seconds: int = 300) -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds

    def get_or_set(self, key: str, *, tags: set[str], factory: Callable[[], object]) -> object:
        cache_key = self._cache_key(key)
        try:
            cached = cast(str | None, self.client.get(cache_key))
            if cached is not None:
                return json.loads(cached)
        except RedisError, ValueError, TypeError:
            logger.warning("public_cache_read_failed", extra={"cache_key": cache_key})

        payload = factory()
        try:
            encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            pipeline = self.client.pipeline(transaction=False)
            pipeline.set(cache_key, encoded, ex=self.ttl_seconds)
            for tag in tags:
                tag_key = self._tag_key(tag)
                pipeline.sadd(tag_key, cache_key)
                pipeline.expire(tag_key, self.ttl_seconds)
            pipeline.execute()
        except RedisError, TypeError, ValueError:
            logger.warning("public_cache_write_failed", extra={"cache_key": cache_key})

        return payload

    def invalidate(self, tags: set[str]) -> None:
        """Clear exactly the keys associated with the supplied public cache tags."""

        try:
            for tag in tags:
                tag_key = self._tag_key(tag)
                pipeline = self.client.pipeline(transaction=False)
                for cache_key in self.client.sscan_iter(tag_key, count=100):
                    pipeline.delete(cache_key)
                pipeline.delete(tag_key)
                pipeline.execute()
        except RedisError:
            logger.exception("public_cache_invalidation_failed", extra={"tags": sorted(tags)})
            raise

    def _cache_key(self, key: str) -> str:
        return f"{self.key_prefix}{key}"

    def _tag_key(self, tag: str) -> str:
        return f"{self.tag_prefix}{tag}"
