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
