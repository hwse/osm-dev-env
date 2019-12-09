#!/usr/bin/env python3
import collections
import json
import logging
import os
import socket

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_PATH, 'stage_1.json')

STAGE_2_PORT = 6000

LOGGER = logging.getLogger('stage_2')

AGGREGATION_DICT = collections.defaultdict(int)


def server_loop():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    address = 'localhost'

    LOGGER.info('starting server on %s %s', address, STAGE_2_PORT)

    connection.bind((address, STAGE_2_PORT))
    connection.listen(10)

    while True:
        current_connection, address = connection.accept()
        handle_client(current_connection, address)


def handle_client(connection, address):
    input_text = ""
    LOGGER.info('connection from %s', address)
    while True:
        data = connection.recv(4096)
        if data:
            input_text += data.decode("utf-8")
        else:
            break
    process_data(input_text)
    connection.close()


def process_data(input_text):
    """Count the words in input_text and return string with result in json format"""
    d = json.loads(input_text)
    for word, count in d.items():
        AGGREGATION_DICT[word.lower()] += count
    LOGGER.info('aggregated data, new state: %s', AGGREGATION_DICT)


def main():
    server_loop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
