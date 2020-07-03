#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import collections.abc
import datetime
import hashlib
import json
import logging
import re
import uuid
from collections import namedtuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
from weakref import WeakKeyDictionary

import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

STORE_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'max_retry_attempt_count': 5
}


class ValidationException(Exception):
    pass


class BaseField(object):
    def __init__(self, required=True, nullable=False):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return self.data.get(instance, None)

    def __set__(self, instance, value):
        if value is not None:
            self.check(value)
        self.data[instance] = value

    def check(self, value):
        pass


class ArgumentsField(BaseField):
    def __set__(self, instance, value):
        try:
            json_obj = json.loads(json.dumps(value))
        except ValueError:
            raise ValidationException("{} is not a valid json".format(str(value)))

        super(ArgumentsField, self).__set__(instance, json_obj)


class CharField(BaseField):
    def check(self, value):
        super(CharField, self).check(value)

        if not isinstance(value, str):
            raise ValidationException('{} is not a str'.format(value))


class EmailField(CharField):
    EMAIL_PATTERN = r'^[a-z][\w\-\.]*@([a-z][\w\-]+\.)+[a-z]{2,4}$'

    def check(self, value):
        super(EmailField, self).check(value)

        if not isinstance(value, str) or (value != "" and not re.match(self.EMAIL_PATTERN, value)):
            raise ValidationException('{} is not a valid email'.format(value))


class PhoneField(BaseField):
    PHONE_PATTERN = r'^7\d{10}$'

    def check(self, value):
        super(PhoneField, self).check(value)

        if value != '' and not re.match(self.PHONE_PATTERN, str(value)):
            raise ValidationException('{} is not a valid phone'.format(value))

    def __set__(self, instance, value):
        super(PhoneField, self).__set__(instance, str(value))


class DateField(BaseField):
    DATE_PATTERN = r'^\d{2}\.\d{2}\.\d{4}$'

    def check(self, value):
        super(DateField, self).check(value)

        if not isinstance(value, str) or (value != '' and not re.match(self.DATE_PATTERN, value)):
            raise ValidationException('{} is not a valid date'.format(value))

    def __get__(self, instance, owner):
        result = super(DateField, self).__get__(instance, owner)

        return datetime.datetime.strptime(result, '%d.%m.%Y') if result else None


class BirthDayField(DateField):
    def check(self, value):
        super(BirthDayField, self).check(value)

        if value != '' and int(re.split(r'[.]', value)[2]) < datetime.datetime.now().year - 70:
            raise ValidationException('{} is more than 70 years ago'.format(value))


class GenderField(BaseField):
    def check(self, value):
        super(GenderField, self).check(value)

        if not (isinstance(value, int) and int(value) in [key for key in GENDERS.keys()]):
            raise ValidationException('{} is not a valid gender'.format(value))


class ClientIDsField(BaseField):
    def check(self, value):
        super(ClientIDsField, self).check(value)
        if not isinstance(value, list):
            raise ValidationException('{} is not a list'.format(value))

        if not all(isinstance(item, int) for item in value):
            raise ValidationException('{} should contain only integers'.format(value))


ValidationResult = namedtuple('ValidationResult', 'success error_message')


class BaseRequest(metaclass=abc.ABCMeta):
    @classmethod
    def from_dict(cls, source_dict):
        self = cls()

        error_list = []
        for key, value in source_dict.items():
            try:
                if key in cls.__dict__:
                    setattr(self, key, value)
            except ValidationException as e:
                error_list.append(str(e))

        if len(error_list) > 0:
            raise ValidationException(', '.join(error_list))

        return self

    def attr_is_null(self, attr_name):
        attr_value = self.__getattribute__(attr_name)
        return (attr_value is None) or \
               (isinstance(attr_value, collections.abc.Sized) and (len(attr_value) == 0))

    def validate(self):
        error_list = []
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, BaseField):
                if value.required and (self.__getattribute__(key) is None):
                    error_list.append('{} is required'.format(key))
                elif not value.nullable and self.attr_is_null(key):
                    error_list.append('{} is not nullable'.format(key))

        return ValidationResult(len(error_list) == 0, ', '.join(error_list))

    @abc.abstractmethod
    def process_request(self, ctx, store):
        raise NotImplementedError


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def process_request(self, ctx, store):
        ctx['nclients'] = len(self.client_ids)
        return {str(cid): scoring.get_interests(store, cid) for cid in self.client_ids}, OK


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    is_admin = False

    def validate(self):
        result = super(OnlineScoreRequest, self).validate()

        if not result.success:
            return result

        is_valid = (not (self.attr_is_null('phone') or self.attr_is_null('email'))) or \
                   (not (self.attr_is_null('first_name') or self.attr_is_null('last_name'))) or \
                   (not (self.attr_is_null('birthday') or self.attr_is_null('gender')))

        return ValidationResult(is_valid, '' if is_valid else "Request should contain at least one pair " \
                                                              "phone-email, first name-last name, gender-birthday " \
                                                              "with non-empty values")

    def process_request(self, ctx, store):
        ctx['has'] = [key for key, value in self.__class__.__dict__.items()
                      if isinstance(value, BaseField) and not self.attr_is_null(key)]

        score = 42 if self.is_admin else scoring.get_score(store, self.phone, self.email, self.birthday, self.gender,
                                                           self.first_name, self.last_name)
        return {"score": score}, OK


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def process_request(self, ctx, store):
        try:
            if self.method.upper() == 'ONLINE_SCORE':
                request = OnlineScoreRequest().from_dict(self.arguments)
                request.is_admin = self.is_admin
            elif self.method.upper() == 'CLIENTS_INTERESTS':
                request = ClientsInterestsRequest().from_dict(self.arguments)
            else:
                return ERRORS[INVALID_REQUEST], INVALID_REQUEST
        except ValidationException as e:
            return str(e), INVALID_REQUEST

        validation_result = request.validate()
        if not validation_result.success:
            return validation_result.error_message, INVALID_REQUEST

        return request.process_request(ctx, store)


def check_auth(request):
    sha512 = hashlib.sha512()
    if request.is_admin:
        sha512.update((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('UTF-8'))
    else:
        sha512.update((request.account + request.login + SALT).encode('UTF-8'))

    digest = sha512.hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    try:
        request_dict = json.loads(json.dumps(request['body']))
    except json.decoder.JSONDecodeError:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    try:
        method_request = MethodRequest().from_dict(request_dict)
    except TypeError as e:
        return e, INVALID_REQUEST

    validation_result = method_request.validate()
    if not validation_result.success:
        return validation_result.error_message, INVALID_REQUEST

    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    return method_request.process_request(ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = scoring.ScoreStore(**STORE_CONFIG)

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
