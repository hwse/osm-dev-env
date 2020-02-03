#!/usr/bin/env python3
import itertools
import json
import logging
import os
import socket
import time

from common import JsonFileSync, RestSync, CfgProperty, S1Instance, S2Instance, ServiceRegistration, DefaultPorts

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.environ.get('RUN_DIR', SCRIPT_PATH)

LOGGER = logging.getLogger('stage_1')


class Stage1Config(JsonFileSync):
    DEFAULT_CONFIG_PATH = os.path.join(RUN_DIR, 'stage_1.json')

    service_registry = CfgProperty('SERVICE_REGISTRY_HOST',
                                   default='http://localhost:{}'.format(DefaultPorts.SERVICE_REGISTRY))
    stage_1_id = CfgProperty('STAGE_1_ID', default=0, mapper=int)
    stage_1_host = CfgProperty('STAGE_1_HOST', default='localhost')
    stage_1_port = CfgProperty('STAGE_1_PORT', default=DefaultPorts.STAGE_1, mapper=int)

    def __init__(self):
        super().__init__(self.DEFAULT_CONFIG_PATH)

    @property
    def stage_1_instance(self):
        return S1Instance(self.stage_1_id, self.stage_1_host, self.stage_1_port)


class ServiceRegistrySync(RestSync):
    stage_2_instance = CfgProperty('stage_2', default=None, mapper=lambda o: S2Instance(**o) if o else None)

    def __init__(self, host):
        super().__init__(host, ['stage_2'])


def server_loop(cfg, service_registry):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    LOGGER.info('starting server on %s %s', cfg.stage_1_host, cfg.stage_1_port)
    LOGGER.info('Sending results to %s', service_registry.stage_2_instance)

    connection.bind((cfg.stage_1_host, cfg.stage_1_port))
    connection.listen(10)

    while True:
        current_connection, address = connection.accept()

        while not service_registry.stage_2_instance:
            LOGGER.debug('No stage 2 instance registered')
            time.sleep(0.5)

        handle_client(current_connection, address, service_registry.stage_2_instance)


def handle_client(connection, address, stage_2):
    input_text = ""
    LOGGER.debug('connection from %s', address)
    while True:
        data = connection.recv(4096)
        if data:
            input_text += data.decode("utf-8")
        else:
            break
    send_to_stage_2(process_data(input_text).encode("utf-8"), stage_2.host, stage_2.port)
    connection.close()


def process_data(input_text):
    """Count the words in input_text and return string with result in json format"""
    sorted_words = sorted(input_text.split())
    for w in sorted_words:
        if w == 'crash':
            raise Exception('Something bad happened')
    result = {key: sum(1 for _ in grouped_words) for key, grouped_words in itertools.groupby(sorted_words)}
    return json.dumps(result)


def send_to_stage_2(json_text, stage_2_host, stage_2_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((stage_2_host, stage_2_port))
        s.sendall(json_text)
        LOGGER.debug('sent results to %s %s', stage_2_host, stage_2_port)


def main():
    with Stage1Config() as cfg:
        with ServiceRegistrySync(lambda: cfg.service_registry) as service_registry:
            with ServiceRegistration(lambda: cfg.service_registry).stage_1_context(cfg.stage_1_instance):
                server_loop(cfg, service_registry)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
