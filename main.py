import logging
import socket
import json
import datetime
import urllib.parse
from threading import Thread
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class OurHandler(BaseHTTPRequestHandler):
    def send_file(self, filename):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, filename):
        self.send_response(200)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-type", mime_type)
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        path = route.path.lstrip('/')
        if path == '':
            self.send_file('front-init/index.html')
        elif path == 'message':
            self.send_file('front-init/message.html')
        else:
            static_path = os.path.join('front-init', path)
            if os.path.exists(static_path):
                if os.path.isdir(static_path):
                    self.send_file('front-init/error.html')
                else:
                    self.send_static(static_path)
            else:
                self.send_file('front-init/error.html')

    def do_POST(self):
        size = int(self.headers.get('Content-Length'))
        data = self.rfile.read(size).decode('UTF-8')
        print(f"Received data: {data}")
        Thread(target=send_to_socket_server, args=(data,)).start()
        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

def send_to_socket_server(data):
    host = '0.0.0.0'
    port = 5000

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(data.encode('utf-8'), (host, port))
    except ConnectionRefusedError:
        logging.error("Can't connect to socket")

def run_socket_server():
    host = '0.0.0.0'
    port = 5000

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"Socket is listening on the {host}:{port}")

        while True:
            data, address = server_socket.recvfrom(1024)
            parse_data = urllib.parse.unquote_plus(data.decode('utf-8'))
            print(f"Received data from {address}: {parse_data}")
            try:
                parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
                dict_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                data_dict = {dict_name: parse_dict}

                if os.path.exists('front-init/storage/data.json'):
                    with open('front-init/storage/data.json', 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                else:
                    existing_data = {}

                existing_data.update(data_dict)

                with open('front-init/storage/data.json', 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=4)
            except ValueError as err:
                logging.error(err)

if __name__ == '__main__':
    socket_thread = Thread(target=run_socket_server, daemon=True)
    socket_thread.start()

    with HTTPServer(('0.0.0.0', 3000), OurHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            socket_thread.join()
            server.server_close()
