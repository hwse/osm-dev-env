import logging
import threading
import json
import time
import os

LOGGER = logging.getLogger(__name__)

class JsonFileSync:

    def __init__(self, path):
        self.path = path
        self.data = self.parse_file()
        self.keep_running = False
        self.thread = threading.Thread(target=self.continuous_read)

    def start(self):
        self.keep_running = True
        self.thread.start()

    def stop(self):
        self.keep_running = False
        self.thread.join(timeout=5)

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
        if item not in self.data:
            return default

        return self[item]
