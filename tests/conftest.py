import http.server
import socketserver
import threading
import time

import pytest


class MockIPTVHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress logs

    def do_GET(self):
        if self.path == "/healthy.m3u8":
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.end_headers()
            self.wfile.write(b"#EXTM3U\n#EXTINF:-1,Channel 1\n/seg1.ts\n")
        elif self.path == "/error.m3u8":
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
        elif self.path == "/not_media":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body>Error Page</body></html>")
        elif self.path == "/slow.m3u8":
            time.sleep(5)
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.end_headers()
            self.wfile.write(b"#EXTM3U\n")
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")


@pytest.fixture(scope="session")
def mock_server():
    # Start a mock server on localhost
    class ThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    server = ThreadingTCPServer(("", 0), MockIPTVHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Wait for server to start
    time.sleep(0.1)

    yield f"http://localhost:{server.server_address[1]}"

    server.shutdown()
