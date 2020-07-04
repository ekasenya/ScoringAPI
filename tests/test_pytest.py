import pytest
import datetime

from tests.fixtures import unavailable_store, store, fields_set
from api import ValidationError, GENDERS, ClientsInterestsRequest, OnlineScoreRequest


def test_get_raise_exception(unavailable_store):
    with pytest.raises(ConnectionError):
        unavailable_store.get('key')


def test_cached_get_raise_exception(unavailable_store):
    assert unavailable_store.cache_get('key') is None


def test_cached_set_raise_exception(unavailable_store):
    unavailable_store.cache_set('key', 1, 60 * 60)


def test_store_ok(store):
    assert (store.get('key') is None)


def test_cached_store_ok(store):
    assert (store.cache_get('key') is None)


@pytest.mark.parametrize('value', [
    ({'test'}),
    datetime.date.today()
])
def test_set_invalid_arguments_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.arguments_field = value


@pytest.mark.parametrize('value', [
    '',
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав", "last_name": "Ступников", ' \
      '"birthday": "01.01.1990", "gender": 1}
])
def test_set_correct_arguments_field(fields_set, value):
    fields_set.arguments_field = value
    assert (value == fields_set.arguments_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    datetime.date.today()
])
def test_set_invalid_char_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.char_field = value


@pytest.mark.parametrize('value', [
    '',
    'Test string'
])
def test_set_correct_char_field(fields_set, value):
    fields_set.char_field = value
    assert (value == fields_set.char_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    datetime.date.today(),
    'test@gmail',
    '1test@gmail.com',
    'test@@gmail.com'
])
def test_set_invalid_email_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.email_field = value


@pytest.mark.parametrize('value', [
    'test@gmail.com',
    'senenkova.e@yandex.ru'
])
def test_set_correct_email_field(fields_set, value):
    fields_set.email_field = value
    assert (value == fields_set.email_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    datetime.date.today(),
    '89032023032',
    '790320230321'
])
def test_set_invalid_phone_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.phone_field = value


@pytest.mark.parametrize('value', [
    '79032023032'
])
def test_set_correct_phone_field(fields_set, value):
    fields_set.phone_field = value
    assert (value == fields_set.phone_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    '01/01/2020',
    '2020-01-01'
])
def test_set_invalid_date_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.date_field = value


@pytest.mark.parametrize('value', [
    '01.01.2020'
])
def test_set_correct_date_field(fields_set, value):
    fields_set.date_field = value
    assert (datetime.datetime.strptime(value, '%d.%m.%Y') == fields_set.date_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    '01/01/2020',
    '2020-01-01',
    '.'.join(['01', '01', str(datetime.date.today().year - 75)])
])
def test_set_invalid_birthdate_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.birthday_field = value


@pytest.mark.parametrize('value', [
    '.'.join(['01', '01', str(datetime.date.today().year - 20)])
])
def test_set_correct_birthdate_field(fields_set, value):
    fields_set.date_field = value
    assert (datetime.datetime.strptime(value, '%d.%m.%Y') == fields_set.date_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    -1,
    10
])
def test_set_invalid_gender_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.gender_field = value


@pytest.mark.parametrize('value', [key for key in GENDERS.keys()])
def test_set_correct_gender_field(fields_set, value):
    fields_set.gender_field = value
    assert (value == fields_set.gender_field)


@pytest.mark.parametrize('value', [
    123,
    {'key': 1},
    datetime.date.today(),
    'Test string',
    ['test', 1, 1]
])
def test_set_invalid_client_ids_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.client_ids_field = value


@pytest.mark.parametrize('source_dict', [
    {'client_ids': [1, 2, 3]},
    {'client_ids': [1], 'date': None},
    {'client_ids': [1], 'date': datetime.datetime.today().strftime('%d.%m.%Y')},
    {'client_ids': [1, 2, 3], 'date': datetime.datetime.today().strftime('%d.%m.%Y')},
])
def test_correct_client_ids_request(fields_set, source_dict):
    request = ClientsInterestsRequest.from_dict(source_dict)
    request.validate()


@pytest.mark.parametrize('source_dict', [
    {'date': datetime.datetime.today().strftime('%d.%m.%Y')},
    {'client_ids': [], 'date': None},
    {'client_ids': [], 'date': datetime.datetime.today().strftime('%d.%m.%Y')}
])
def test_invalid_client_ids_request(fields_set, source_dict):
    request = ClientsInterestsRequest.from_dict(source_dict)
    with pytest.raises(ValidationError):
        request.validate()


@pytest.mark.parametrize('source_dict', [
    {"phone": "79175002040", "email": "test@gmail.com"},
    {"first_name": "John", "last_name": "Smith"},
    {"gender": 1, "birthday": "01.01.2000"},
    {"phone": "79175002040", "email": "test@gmail.com", "first_name": "John", "last_name": "Smith", "gender": 1,
        "birthday": "01.01.2000"},
])
def test_correct_online_score_request(fields_set, source_dict):
    request = OnlineScoreRequest.from_dict(source_dict)
    request.validate()


@pytest.mark.parametrize('source_dict', [
    {},
    {"phone": "79175002040"},
    {"phone": "79175002040", "email": None},
    {"phone": "79175002040", "email": ""},
    {"phone": "79175002040", "first_name": "John"},
    {"first_name": "John", "last_name": None},
    {"first_name": "John", "last_name": ""},
    {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "John"},
    {"phone": "79175002040", "gender": 1, "first_name": "John"},
    {"phone": "79175002040", "gender": None, "birthday": "01.01.2000", "first_name": "John"},
])
def test_invalid_online_score_request(fields_set, source_dict):
    request = OnlineScoreRequest.from_dict(source_dict)
    with pytest.raises(ValidationError):
        assert not request.validate().success
