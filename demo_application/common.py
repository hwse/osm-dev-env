import abc
import json
import logging
import os
import socket
import threading
import time

import attr
import requests
from attr.validators import instance_of, is_callable

LOGGER = logging.getLogger(__name__)

IS_PRODUCTION_ENV_FLAG = 'IS_PRODUCTION'
SERVICE_REGISTRY_HOST_ENV_VAR = 'SERVICE_REGISTRY_HOST'


class DefaultPorts:
    SERVICE_REGISTRY = 3000
    LOAD_BALANCER = 4000
    STAGE_1 = 5000
    STAGE_2 = 6000
    WEB_INTERFACE = 7000


class __Environment:

    def __init__(self, env_dict):
        self.is_production = env_dict.get(IS_PRODUCTION_ENV_FLAG, 'false').lower() == 'true'
        self.service_registry_host = env_dict.get(SERVICE_REGISTRY_HOST_ENV_VAR, 'localhost')


ENV_VARS = __Environment(os.environ)


@attr.s(frozen=True)
class S1Instance:
    id = attr.ib(converter=int, validator=instance_of(int))
    host = attr.ib(validator=instance_of(str))
    port = attr.ib(converter=int, validator=instance_of(int))

    @classmethod
    def from_dict(cls, d):
        print(d)
        return cls(d['id'], d['host'], d['port'])


@attr.s(frozen=True)
class S2Instance:
    host = attr.ib(validator=instance_of(str))
    port = attr.ib(converter=int, validator=instance_of(int))

    @classmethod
    def from_dict(cls, d):
        return cls(d['host'], d['port'])


class DataSync(abc.ABC):
    """Poll data from some IO source and save it in a dict."""

    def __init__(self, wait_seconds=5):
        self.wait_seconds = wait_seconds
        self.data = dict()
        self.keep_running = False
        self.thread = threading.Thread(target=self.continuous_read)

    def initialize(self):
        while True:
            try:
                self.data = self.fetch_data()
                return
            except Exception as e:
                LOGGER.exception('Error while initialization, retrying...')
                time.sleep(self.wait_seconds)

    def start(self):
        self.keep_running = True
        self.thread.start()

    def stop(self):
        LOGGER.info('stopping sync thread: %s', self.thread)
        self.keep_running = False
        self.thread.join(timeout=self.wait_seconds * 2)

    def __enter__(self):
        self.initialize()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @abc.abstractmethod
    def fetch_data(self):
        raise NotImplementedError()

    def continuous_read(self):
        while self.keep_running:
            try:
                new_data = self.fetch_data()
                if new_data != self.data:
                    LOGGER.info('Config changed to: %s', new_data)
                self.data = new_data
                time.sleep(self.wait_seconds)
            except Exception as e:
                LOGGER.exception('error in config', e)
                time.sleep(self.wait_seconds)

    def __getitem__(self, item):
        return self.data[item]

    def get(self, item, default):
        return self.data.get(item, default)


class JsonFileSync(DataSync):
    """Poll data from a local json file."""

    def __init__(self, path):
        super().__init__(wait_seconds=1)
        self.path = path

    def fetch_data(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path) as f:
            return json.load(f)


class RestSync(DataSync):
    """Poll data from a rest api"""

    def __init__(self, host, paths):
        super().__init__()
        self.get_host = host if callable(host) else lambda: host
        self.paths = paths

    @property
    def host(self):
        return self.get_host()

    def fetch_data(self):
        def fetch_from_url(path):
            full_url = '{}/{}'.format(self.host, path)
            LOGGER.debug(full_url)
            resp = requests.get(full_url)
            j = resp.json()
            LOGGER.debug('received json: %s', j)
            return j

        return {path: fetch_from_url(path) for path in self.paths}


class CfgProperty:
    """Access the dict in DataSync via a property."""
    NO_DEFAULT = object()

    def __init__(self, key, default=NO_DEFAULT, mapper=None):
        self.key = key
        self.default = default
        self.mapper = mapper

    @property
    def has_default(self):
        return self.default is not self.NO_DEFAULT

    def map_value(self, value):
        if self.mapper is None:
            return value
        else:
            return self.mapper(value)

    def __get__(self, obj, cls):
        json_value = obj.get(self.key, self.default) if self.has_default else obj[self.key]
        return self.map_value(json_value)

    def __set__(self, obj, val):
        raise AttributeError('{} can not be set'.format(self.__class__))


@attr.s
class EntryExitManager:
    enter = attr.ib(validator=is_callable())
    exit = attr.ib(validator=is_callable())

    def __enter__(self):
        return self.enter()

    def __exit__(self, *args, **kwargs):
        return self.exit()


def where_am_i(target_ip):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((target_ip, 80))
        return s.getsockname()[0]


class ServiceRegistration:
    """Instances can use this class to register as services."""

    def __init__(self, host):
        self.get_host = host if callable(host) else lambda: host

    @property
    def host(self):
        return self.get_host()

    @property
    def s1_url(self):
        return '{}/{}'.format(self.host, 'stage_1')

    @property
    def s2_url(self):
        return '{}/{}'.format(self.host, 'stage_2')

    def register_stage_1(self, s1_instance):
        LOGGER.info('Registering stage 1: %s', s1_instance)
        requests.post(self.s1_url, params=attr.asdict(s1_instance))

    def register_stage_2(self, s2_instance):
        LOGGER.info('Registering stage 2: %s', s2_instance)
        requests.post(self.s2_url, params=attr.asdict(s2_instance))

    def unregister_stage_1(self, s1_instance):
        LOGGER.info('Unregistering stage 1: %s', s1_instance)
        requests.delete(self.s1_url, params=attr.asdict(s1_instance))

    def unregister_stage_2(self):
        LOGGER.info('Unregistering stage 2')
        requests.delete(self.s2_url)

    def stage_1_context(self, s1_instance):
        return EntryExitManager(lambda: self.register_stage_1(s1_instance),
                                lambda: self.unregister_stage_1(s1_instance))

    def stage_2_context(self, s2_instance):
        return EntryExitManager(lambda: self.register_stage_2(s2_instance),
                                lambda: self.unregister_stage_2())
