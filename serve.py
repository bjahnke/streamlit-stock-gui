# https_server.py

import http.server
import ssl
from os.path import expanduser

CERT_FILE = expanduser("~/certs/cert.pem")
KEY_FILE = expanduser("~/certs/key.pem")

PORT = 8443
DIRECTORY = "home/brian/tmpweb"

handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(('localhost', PORT), handler)

httpd.socket = ssl.wrap_socket(
    httpd.socket,
    server_side=True,
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
    ssl_version=ssl.PROTOCOL_TLS
)

print(f"Serving HTTPS on https://localhost:{PORT}")
httpd.serve_forever()
