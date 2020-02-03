#!/usr/bin/env python3

import logging
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor

from common import RestSync, CfgProperty, S1Instance, JsonFileSync, DefaultPorts

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.environ.get('RUN_DIR', SCRIPT_PATH)

LOGGER = logging.getLogger('load_balancer')


class LoadBalancerConfig(JsonFileSync):
    DEFAULT_CONFIG_PATH = os.path.join(RUN_DIR, 'load_balancer.json')

    service_registry = CfgProperty('SERVICE_REGISTRY_HOST',
                                   default='http://localhost:{}'.format(DefaultPorts.SERVICE_REGISTRY))
    host = CfgProperty('LOAD_BALANCER_HOST', default='localhost')
    port = CfgProperty('LOAD_BALANCER_PORT', default=DefaultPorts.LOAD_BALANCER, mapper=int)

    def __init__(self):
        super().__init__(self.DEFAULT_CONFIG_PATH)


class ServiceRegistrySync(RestSync):
    stage_1_instances = CfgProperty('stage_1', default=[], mapper=lambda l: [S1Instance(**o) for o in l])

    def __init__(self, host):
        super().__init__(host, ['stage_1'])
        self.next_instance = 0

    def next_stage_1(self):
        while not self.stage_1_instances:
            LOGGER.info('No stage_1 instances registered')
            time.sleep(0.5)

        instance = self.stage_1_instances[self.next_instance]
        self.next_instance = (self.next_instance + 1) % len(self.stage_1_instances)
        return instance


def server_loop(config, service_registry):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    LOGGER.info('starting server on %s %s', config.host, config.port)

    connection.bind((config.host, config.port))
    connection.listen(10)

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            current_connection, address = connection.accept()
            executor.submit(handle_connection, current_connection, address, service_registry.next_stage_1())


def handle_connection(connection, address, s1_instance):
    LOGGER.debug('connection from %s', address)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((s1_instance.host, s1_instance.port))
        while True:
            data = connection.recv(4096)
            if data:
                s.send(data)
            else:
                break
        s.close()
        connection.close()
        LOGGER.debug('sent results to %s %s', s1_instance.host, s1_instance.port)


def main():
    with LoadBalancerConfig() as cfg:
        with ServiceRegistrySync(lambda: cfg.service_registry) as service_registry:
            server_loop(cfg, service_registry)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
