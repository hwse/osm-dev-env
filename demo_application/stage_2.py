#!/usr/bin/env python3
import collections
import json
import logging
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from common import JsonFileSync, CfgProperty, ServiceRegistration, DefaultPorts, S2Instance, ENV_VARS

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

LOGGER = logging.getLogger('stage_2')


class Config(JsonFileSync):
    DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_PATH, 'stage_2.json')

    service_registry = CfgProperty('SERVICE_REGISTRY_HOST',
                                   default='http://{}:{}'.format(ENV_VARS.service_registry_host,
                                                                  DefaultPorts.SERVICE_REGISTRY))

    stage_2_host = CfgProperty('STAGE_2_HOST', default='localhost')
    stage_2_port = CfgProperty('STAGE_2_PORT', default=DefaultPorts.STAGE_2, mapper=int)
    web_host = CfgProperty('WEB_HOST', default='localhost')
    web_port = CfgProperty('WEB_PORT', default=DefaultPorts.WEB_INTERFACE, mapper=int)

    def __init__(self):
        super().__init__(self.DEFAULT_CONFIG_PATH)

    @property
    def stage_2_instance(self):
        return S2Instance(self.stage_2_host, self.stage_2_port)


AGGREGATION_DICT = collections.defaultdict(int)


def server_loop(cfg):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    LOGGER.info('starting server on %s port: %s', cfg.stage_2_host, cfg.stage_2_port)

    connection.bind((cfg.stage_2_host, cfg.stage_2_port))
    connection.listen(10)

    while True:
        current_connection, address = connection.accept()
        handle_client(current_connection, address)


def handle_client(connection, address):
    input_text = ""
    LOGGER.debug('connection from %s', address)
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
    LOGGER.debug('aggregated data, new state: %s', AGGREGATION_DICT)


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


def serve_web_page(cfg):
    web_server = HTTPServer((cfg.web_host, cfg.web_port), MyServer)
    LOGGER.info("Web-Server started http://%s:%s", cfg.web_host, cfg.web_port)

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Server stopped.")

    web_server.server_close()


def main():
    with Config() as cfg:
        with ServiceRegistration(lambda: cfg.service_registry).stage_2_context(cfg.stage_2_instance):
            threads = [
                threading.Thread(target=server_loop, args=[cfg]),
                threading.Thread(target=serve_web_page, args=[cfg])
            ]
            for t in threads:
                t.start()

            for t in threads:
                t.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
