import hashlib
import json
import time

import redis


class ScoreStore:
    @classmethod
    def create_store(cls, host='localhost', port=6379,
                     socket_timeout=5,
                     socket_connect_timeout=5):
        return redis.Redis(host=host, port=port, socket_timeout=socket_timeout,
                           socket_connect_timeout=socket_connect_timeout)

    def __init__(self, host='localhost', port=6379,
                 socket_timeout=5,
                 socket_connect_timeout=5, max_retry_attempt_count=5):
        self.redis_store = self.create_store(host, port, socket_timeout, socket_connect_timeout)
        self.max_retry_attempt_count = max_retry_attempt_count

    class RetryConnectionDecorator:
        @staticmethod
        def retry_connect(decorated):
            def wrapper(*args, **kwargs):
                obj = args[0]

                if not isinstance(obj, ScoreStore):
                    return decorated(*args, **kwargs)

                for attempt_num in range(obj.max_retry_attempt_count):
                    try:
                        return decorated(*args, **kwargs)
                    except (redis.ConnectionError, redis.TimeoutError):
                        if attempt_num == obj.max_retry_attempt_count - 1:
                            raise
                        else:
                            time.sleep(1)

            return wrapper

    @RetryConnectionDecorator.retry_connect
    def cache_set(self, key, value, cache_time):
        try:
            self.redis_store.psetex(key, cache_time * 1000, value)
        except Exception:
            pass

    @RetryConnectionDecorator.retry_connect
    def cache_get(self, key):
        try:
            return self.get(key)
        except Exception:
            return None

    @RetryConnectionDecorator.retry_connect
    def get(self, key):
        return self.redis_store.get(key)


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday.strftime("%Y%m%d") if birthday is not None else "",
    ]
    key = "uid:" + hashlib.md5("".join(key_parts).encode('UTF-8')).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        return float(score)
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    return json.loads(r) if r else []
