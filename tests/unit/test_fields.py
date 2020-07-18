import pytest
from datetime import datetime, date

from api import ValidationError, GENDERS


@pytest.mark.parametrize('value', [
    ({'test'}),
    date.today()
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
    date.today()
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
    date.today(),
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
    date.today(),
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
    assert (datetime.strptime(value, '%d.%m.%Y') == fields_set.date_field)


@pytest.mark.parametrize('value', [
    123,
    [],
    {'key': 1},
    '01/01/2020',
    '2020-01-01',
    '.'.join(['01', '01', str(date.today().year - 75)])
])
def test_set_invalid_birthdate_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.birthday_field = value


@pytest.mark.parametrize('value', [
    '.'.join(['01', '01', str(date.today().year - 20)])
])
def test_set_correct_birthdate_field(fields_set, value):
    fields_set.date_field = value
    assert (datetime.strptime(value, '%d.%m.%Y') == fields_set.date_field)


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
    date.today(),
    'Test string',
    ['test', 1, 1]
])
def test_set_invalid_client_ids_field(fields_set, value):
    with pytest.raises(ValidationError):
        fields_set.client_ids_field = value
