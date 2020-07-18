import pytest
import time
import redis
import json

from tests.fixtures import unavailable_store, store


def test_get_raise_exception(unavailable_store):
    with pytest.raises(redis.exceptions.ConnectionError):
        unavailable_store.get('key')


def test_cached_get_raise_exception(unavailable_store):
    assert unavailable_store.cache_get('key') is None


def test_cached_set_raise_exception(unavailable_store):
    unavailable_store.cache_set('key', 1, 60 * 60)


def test_store_ok(store):
    assert (store.get('key') is None)


def test_cached_store_int_ok(store):
    value = 10
    store.cache_set('int', value, 10)
    cached_value = type(value)(store.cache_get('int'))
    assert (cached_value == value)


def test_cached_store_str_ok(store):
    value = 'test string'
    store.cache_set('str', value, 10)
    cached_value = store.cache_get('str').decode('UTF-8')
    assert (cached_value == value)


def test_cached_store_list_as_str_ok(store):
    value = '["cars", "cats"]'
    store.cache_set('list', value, 10)
    v = store.cache_get('list').decode('UTF-8')
    cached_value = json.dumps(json.loads(v))
    assert (cached_value == value)


def test_cached_store_invalid_cache(store):
    store.cache_set('key', 10, 1)
    time.sleep(2)
    assert (store.cache_get('key') is None)
