import pytest
from datetime import datetime

from api import ValidationError, ClientsInterestsRequest, OnlineScoreRequest


@pytest.mark.parametrize('source_dict', [
    {'client_ids': [1, 2, 3]},
    {'client_ids': [1], 'date': None},
    {'client_ids': [1], 'date': datetime.today().strftime('%d.%m.%Y')},
    {'client_ids': [1, 2, 3], 'date': datetime.today().strftime('%d.%m.%Y')},
])
def test_correct_client_ids_request(fields_set, source_dict):
    request = ClientsInterestsRequest.from_dict(source_dict)
    request.validate()


@pytest.mark.parametrize('source_dict', [
    {'date': datetime.today().strftime('%d.%m.%Y')},
    {'client_ids': [], 'date': None},
    {'client_ids': [], 'date': datetime.today().strftime('%d.%m.%Y')}
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
