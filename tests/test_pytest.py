import pytest
from mock import Mock, patch

from scoring import ScoreStore


@pytest.fixture(scope="module")
def unavailable_store(request):
    mocked_redis = Mock()
    mocked_redis.get.side_effect = ConnectionError
    mocked_redis.set.side_effect = ConnectionError
    with patch('scoring.ScoreStore.create_store', return_value=mocked_redis):
        print('create unavailablestore')
        yield ScoreStore()


@pytest.fixture(scope="module")
def store(request):
    mocked_redis = Mock()
    mocked_redis.get.return_value = 1
    with patch('scoring.ScoreStore.create_store', return_value=mocked_redis):
        print('create normal store')
        yield ScoreStore()


def test_get_raise_exception(unavailable_store):
    with pytest.raises(ConnectionError):
        unavailable_store.get('key')


def test_cached_get_raise_exception(unavailable_store):
    assert unavailable_store.cache_get('key') is None


def test_cached_set_raise_exception(unavailable_store):
    unavailable_store.cache_set('key', 1, 60 * 60)


def test_store_ok(store):
    assert(store.get('key') == 1)


def test_cached_store_ok(store):
    store.cache_set('key', 1, 60 * 60)
    assert(store.cache_get('key') == 1)


if __name__ == "__main__":
    pytest.main()