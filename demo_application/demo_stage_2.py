#!/usr/bin/env python3
import collections
import json
import logging
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from concurrent.futures import ThreadPoolExecutor

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_PATH, 'stage_1.json')

STAGE_2_ADDRESS = 'localhost'
STAGE_2_PORT = 6000

WEB_ADDRESS = 'localhost'
WEB_PORT = 8081

LOGGER = logging.getLogger('stage_2')

AGGREGATION_DICT = collections.defaultdict(int)


def server_loop():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    LOGGER.info('starting server on %s %s', STAGE_2_ADDRESS, STAGE_2_PORT)

    connection.bind((STAGE_2_ADDRESS, STAGE_2_PORT))
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


def aggregation_html():
    data = sorted(AGGREGATION_DICT.items(), key=lambda x: x[1], reverse=True)
    rows = "".join("<tr><td>{}</td><td>{}</td></tr>".format(w.replace('<', '&lt;'), c) for w, c in data)
    return '<table><tr><th scope="col">word</th><th scope="col">count</th></tr>{}</table>'.format(rows)


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Counted Words</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<h1>Words!</h1>", "utf-8"))
        self.wfile.write(bytes(aggregation_html(), "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


def serve_web_page():
    web_server = HTTPServer((WEB_ADDRESS, WEB_PORT), MyServer)
    LOGGER.info("Server started http://%s:%s", WEB_ADDRESS, WEB_PORT)

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Server stopped.")

    web_server.server_close()


def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        server_future = executor.submit(server_loop)
        web_future = executor.submit(serve_web_page)
        server_future.result()
        web_future.result()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
