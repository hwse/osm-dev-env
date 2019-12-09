#!/usr/bin/env python3
import json
import logging
import os
import socket
import itertools

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_PATH, 'stage_1.json')

STAGE_2_HOST = 'localhost'
STAGE_2_PORT = 6000

LOGGER = logging.getLogger('stage_1')


def server_loop():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    address = 'localhost'
    port = 5000

    LOGGER.info('starting server on %s %s', address, port)

    connection.bind((address, port))
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
    send_to_stage_2(process_data(input_text).encode("utf-8"))
    connection.close()


def process_data(input_text):
    """Count the words in input_text and return string with result in json format"""
    sorted_words = sorted(input_text.split())
    result = {key: sum(1 for _ in grouped_words) for key, grouped_words in itertools.groupby(sorted_words)}
    return json.dumps(result)


def send_to_stage_2(json_text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((STAGE_2_HOST, STAGE_2_PORT))
        s.sendall(json_text)
        LOGGER.info('sent results to %s %s', STAGE_2_HOST, STAGE_2_PORT)


def main():
    server_loop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
