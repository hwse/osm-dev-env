import json
import logging
import os
import threading
import time

LOGGER = logging.getLogger(__name__)


class JsonFileSync:

    def __init__(self, path):
        self.path = path
        self.data = self.parse_file()
        self.keep_running = False
        self.thread = threading.Thread(target=self.continuous_read)

    def start(self):
        LOGGER.info('starting file sync')
        self.keep_running = True
        self.thread.start()

    def stop(self):
        LOGGER.info('stopping file sync...')
        self.keep_running = False
        self.thread.join(timeout=5)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def parse_file(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path) as f:
            return json.load(f)

    def continuous_read(self):
        while self.keep_running:
            try:
                new_data = self.parse_file()
                if new_data != self.data:
                    LOGGER.info('Config changed to: %s', new_data)
                self.data = new_data
                time.sleep(1)
            except Exception as e:
                LOGGER.exception('error in config', e)
                time.sleep(1)

    def __getitem__(self, item):
        return self.data[item]

    def get(self, item, default):
        return self.data.get(item, default)


class CfgProperty:
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
