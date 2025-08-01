# Copyright 2025 Tom Rothamel
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import http.server
import pathlib
import os
import webbrowser

class Handler(http.server.SimpleHTTPRequestHandler):

    extensions_map = {
        '': 'application/octet-stream', # Default
        '.gz': 'application/gzip',
        '.htm': 'text/html',
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.wasm': 'application/wasm',
        '.avi': 'video/x-msvideo',
        '.m1v': 'video/mpeg',
        '.m2v': 'video/mpeg',
        '.m4v': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.mp4': 'video/mp4',
        '.mpe': 'video/mpeg',
        '.mpeg': 'video/mpeg',
        '.mpg': 'video/mpeg',
        '.mpg4': 'video/mp4',
        '.mpv': 'video/x-matroska',
        '.ogv': 'video/ogg',
        '.webm': 'video/webm',
        '.wmv': 'video/x-ms-wmv',
        }


def start(path: str | pathlib.Path) -> None:

    """
    Runs the HTTP server on a random port starting from 8052.
    """

    path = pathlib.Path(path)
    website = path / "_website"

    def handle_request(request, client_address, server):
        return Handler(request, client_address, server, directory=website)

    bind_address = os.environ.get("WEBSERVER_BIND_ADDRESS", "127.0.0.1")

    for port in range(8052, 8062):
        try:
            server = http.server.HTTPServer((bind_address, port), handle_request)
            break
        except OSError:
            continue

    else:
        raise SystemExit("Could not find an available port for the web server (tried 8052-8061).")

    print(f"Serving {path} on http://{bind_address}:{port}/")
    print("Press Ctrl+C to stop the server.")
    print()
    print("Opening in web browser...")

    webbrowser.open(f"http://{bind_address}:{port}/", new=2)

    server.serve_forever()
