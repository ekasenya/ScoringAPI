import hashlib
import json
import redis


class ScoreStore:

    def __init__(self, host='localhost', port=6379,
                 db=0, socket_timeout=5,
                 socket_connect_timeout=5, max_retry_attempt_count=5):
        self.redis_store = redis.Redis(host=host, port=port, db=db, socket_timeout=socket_timeout,
                                       socket_connect_timeout=socket_connect_timeout)
        self.max_retry_attempt_count = max_retry_attempt_count

    def retry_connect_decorator(func):
        def wrapper(*args, **kwargs):
            for attempt_num in range(args[0].max_retry_attempt_count):
                try:
                    return func(*args, **kwargs)
                except (redis.ConnectionError, redis.TimeoutError) as e:
                    if attempt_num == args[0].max_retry_attempt_count - 1:
                        raise
                    else:
                        time.sleep(1)

        return wrapper

    @retry_connect_decorator
    def cache_set(self, key, value, cache_time):
        try:
            self.redis_store.psetex(key, cache_time * 1000, value)
        except Exception:
            pass

    @retry_connect_decorator
    def cache_get(self, key):
        try:
            return self.get(key)
        except Exception:
            return None

    @retry_connect_decorator
    def set(self, key, value):
        self.redis_store.set(key, value)

    @retry_connect_decorator
    def get(self, key):
        return self.redis_store.get(key)

def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday.strftime("%Y%m%d") if birthday is not None else "",
    ]
    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        return score
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
