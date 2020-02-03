#!/usr/bin/env python3

def server_loop():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    LOGGER.info('starting server on %s %s', STAGE_1_HOST, STAGE_1_PORT)

    connection.bind((STAGE_1_HOST, STAGE_1_PORT))
    connection.listen(10)

    while True:
        current_connection, address = connection.accept()
        handle_client(current_connection, address)



def send_to_stage_1(json_text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((STAGE_2_HOST, STAGE_2_PORT))
        s.sendall(json_text)
        LOGGER.info('sent results to %s %s', STAGE_2_HOST, STAGE_2_PORT)

def main():
    pass


if __name__ == '__main__':
    main()
