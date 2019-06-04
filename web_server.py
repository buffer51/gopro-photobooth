import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def available_slideshow_files(self):
        return os.listdir('./slideshow/')

    def available_pictures(self):
        files = os.listdir('./pictures/processed/')
        return sorted([f for f in files if f.endswith('.JPG')])

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == '/pictures.json':
            self.handle_list()
        else:
            maybe_filename = self.path[1:]
            if self.path == '/':
                maybe_filename = 'index.html'

            if maybe_filename in self.available_slideshow_files():
                return self.handle_slideshow(maybe_filename)
            elif maybe_filename.startswith('pictures/'):
                maybe_filename = maybe_filename.replace('pictures/', '')
                if maybe_filename in self.available_pictures():
                    return self.handle_picture(maybe_filename)

            self.handle_other()

    def handle_list(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str.encode(json.dumps(self.available_pictures())))

    def handle_slideshow(self, filename):
        self.send_response(200)
        self.end_headers()
        with open('./slideshow/{}'.format(filename), 'rb') as f:
            content = f.read()
            self.wfile.write(content)

    def handle_picture(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'image/jpg')
        self.end_headers()
        with open('./pictures/processed/{}'.format(filename), 'rb') as f:
            content = f.read()
            self.wfile.write(content)

    def handle_other(self):
        self.send_response(500)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ('localhost', 80)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
