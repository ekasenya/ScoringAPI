import pytest
import redis

from datetime import datetime

from scoring import get_score, get_interests
from tests.fixtures import unavailable_store, store


def get_bdate():
    return datetime.strptime("01.01.2000", "%d.%m.%Y")


def test_get_score_from_unavailable_store(unavailable_store):
    assert get_score(unavailable_store, "79175002040", "test@otus.ru", get_bdate()) - 3.0 < 0.00001


@pytest.mark.parametrize("args, score", [
    (("79175002040", "", None), 1.5),
    (("", "test@otus.ru", None), 1.5),
    (("79175002040", "test@otus.ru", get_bdate()), 3),
    (("79175002040", "test@otus.ru", get_bdate(), 1), 4.5),
    (("79175002040", "test@otus.ru", get_bdate(), 1, "John"), 4.5),
    (("79175002040", "test@otus.ru", get_bdate(), 1, "John", "Smith"), 5)
])
def test_get_score_from_store(store, args, score):
    assert get_score(store, *args) - score < 0.00001


def test_get_score_equals(store):
    bdate = get_bdate()
    v1 = get_score(store, "79175002040", "test@otus.ru", bdate)
    v2 = get_score(store, "79175002040", "test@otus.ru", bdate)
    assert v1 - v2 < 0.00001


def test_get_interests_from_unavailable_store(unavailable_store):
    with pytest.raises(redis.exceptions.ConnectionError):
        get_interests(unavailable_store, 1)


def test_get_interests_from_store(store):
    assert get_interests(store, 1) == []
