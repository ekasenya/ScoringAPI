import pytest
import hashlib

from datetime import datetime

import api


def get_valid_auth(request):
    sha512 = hashlib.sha512()
    if request.get("login") == api.ADMIN_LOGIN:
        sha512.update((datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode('UTF-8'))
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        sha512.update(msg.encode('UTF-8'))
    return sha512.hexdigest()


def get_invalid_auth(request):
    sha512 = hashlib.sha512()
    if request.get("login") == api.ADMIN_LOGIN:
        sha512.update((datetime.now().strftime("%Y%m%d") + api.ADMIN_SALT).encode('UTF-8'))
    else:
        msg = request.get("account", "") + request.get("login", "") + datetime.now().strftime("%Y%m%d") + api.SALT
        sha512.update(msg.encode('UTF-8'))
    return sha512.hexdigest()


@pytest.mark.parametrize('arguments', [
    {"phone": "79175002040", "email": "stupnikov@otus.ru"},
    {"gender": 0, "birthday": "01.01.2000"},
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000"}
])
def test_valid_auth(arguments):
    request_dict = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    request_dict['token'] = get_valid_auth(request_dict)
    request = api.MethodRequest().from_dict(request_dict)
    assert api.check_auth(request)


@pytest.mark.parametrize('arguments', [
    {"phone": "79175002040", "email": "stupnikov@otus.ru"},
    {"gender": 0, "birthday": "01.01.2000"},
    {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000"}
])
def test_invalid_auth(arguments):
    request_dict = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    request_dict['token'] = get_invalid_auth(request_dict)
    request = api.MethodRequest().from_dict(request_dict)
    assert not api.check_auth(request)
