import pytest
import redis
from sys import float_info
from datetime import datetime

from scoring import get_score, get_interests
from tests.fixtures import unavailable_store, store, birth_date


def test_get_score_from_unavailable_store(unavailable_store, birth_date):
    assert get_score(unavailable_store, "79175002040", "test@otus.ru", birth_date) - 3.0 < float_info.epsilon


def bdate():
    return datetime.strptime("01.01.2000", "%d.%m.%Y")


@pytest.mark.parametrize("args, score", [
    (("79175002040", "", None), 1.5),
    (("", "test@otus.ru", None), 1.5),
    (("79175002040", "test@otus.ru", bdate), 3),
    (("79175002040", "test@otus.ru", bdate, 1), 4.5),
    (("79175002040", "test@otus.ru", bdate, 1, "John"), 4.5),
    (("79175002040", "test@otus.ru", bdate, 1, "John", "Smith"), 5)
])
def test_get_score_from_store(store, args, score):
    assert get_score(store, *args) - score < float_info.epsilon


def test_get_score_equals(store, birth_date):
    v1 = get_score(store, "79175002040", "test@otus.ru", birth_date)
    v2 = get_score(store, "79175002040", "test@otus.ru", birth_date)
    assert v1 - v2 < float_info.epsilon


def test_get_interests_from_unavailable_store(unavailable_store):
    with pytest.raises(redis.exceptions.ConnectionError):
        get_interests(unavailable_store, 1)


def test_get_interests_from_store(store):
    assert get_interests(store, 1) == []
