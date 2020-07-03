import pytest
from mock import Mock, patch

from scoring import ScoreStore
import api


@pytest.fixture(scope="module")
def unavailable_store(request):
    mocked_redis = Mock()
    mocked_redis.get.side_effect = ConnectionError
    mocked_redis.set.side_effect = ConnectionError
    with patch('scoring.ScoreStore.create_store', return_value=mocked_redis):
        yield ScoreStore()


@pytest.fixture(scope="module")
def store(request):
    mocked_redis = Mock()
    mocked_redis.get.return_value = None
    with patch('scoring.ScoreStore.create_store', return_value=mocked_redis):
        yield ScoreStore()


class FieldsSet:
    arguments_field = api.ArgumentsField()
    char_field = api.CharField()
    email_field = api.EmailField()
    phone_field = api.PhoneField()
    date_field = api.DateField()
    birthday_field = api.BirthDayField()
    gender_field = api.GenderField()
    client_ids_field = api.ClientIDsField()


@pytest.fixture(scope='module')
def fields_set(request):
    print('create fields_set')
    return FieldsSet()
