#!/usr/bin/env python3
import itertools
import json
import logging
import os
import socket

from common import JsonFileSync, CfgProperty

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

LOGGER = logging.getLogger('stage_1')


class Config(JsonFileSync):
    DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_PATH, 'stage_1.json')

    stage_1_host = CfgProperty('STAGE_1_HOST', default='localhost')
    stage_1_port = CfgProperty('STAGE_1_PORT', default=5000, mapper=int)
    stage_2_host = CfgProperty('STAGE_2_HOST', default='localhost')
    stage_2_port = CfgProperty('STAGE_2_PORT', default=6000, mapper=int)

    def __init__(self):
        super().__init__(self.DEFAULT_CONFIG_PATH)


def server_loop():
    with Config() as cfg:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        LOGGER.info('starting server on %s %s', cfg.stage_1_host, cfg.stage_1_port)
        LOGGER.info('Sending results to %s on port %s', cfg.stage_2_host, cfg.stage_2_port)

        connection.bind((cfg.stage_1_host, cfg.stage_1_port))
        connection.listen(10)

        while True:
            current_connection, address = connection.accept()
            handle_client(current_connection, address, cfg.stage_2_host, cfg.stage_2_port)


def handle_client(connection, address, stage_2_host, stage_2_port):
    input_text = ""
    LOGGER.info('connection from %s', address)
    while True:
        data = connection.recv(4096)
        if data:
            input_text += data.decode("utf-8")
        else:
            break
    send_to_stage_2(process_data(input_text).encode("utf-8"), stage_2_host, stage_2_port)
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
        LOGGER.info('sent results to %s %s', stage_2_host, stage_2_port)


def main():
    server_loop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
