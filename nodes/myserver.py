

import udi_interface
import http.server
import json

LOGGER = udi_interface.LOGGER

# start server with self.httpserver = Server(('', self.port), handler)
#
# handler is a class
#   class my_handler(http.server.BaseHTTPRequestHandler):
#
#    with methods: do_GET(self) and do_POST(self) 
#       self.path is the calling path

class VHandler(http.server.BaseHTTPRequestHandler):
    ctlnode = None

    def respond(self):
        message = "<head></head><body>Successful data submission</body>\n"

        self.send_response(200)  # OK
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(message.encode('utf_8'))

    def do_POST(self):
        LOGGER.error('POST: {}'.format(self.path))
        content_length = int(self.headers['content-Length'])
        post_data = json.loads(self.rfile.read(content_length))

        """
        The incoming URL should have the name of the player this is for.

        We get this for changes like new song, play, pause, volume, repeat, shuffle
        so check the post data for changes and propate those back
        """

        LOGGER.debug('{}'.format(post_data))

        if post_data['item'] == 'state':
            info = post_data['data']
            LOGGER.debug('Volume:  {}'.format(info['volume']))
            LOGGER.debug('Random:  {}'.format(info['random']))
            LOGGER.debug('Repeat:  {}'.format(info['repeat']))
            LOGGER.debug('Play  :  {}'.format(info['status']))
            if self.ctlnode is not None:
                LOGGER.debug('Setting control node drivers')
                self.ctlnode.status(info)

        self.respond()

    def do_GET(self):
        LOGGER.error('GET: {}'.format(self.path))
        self.respond()

class Server(http.server.HTTPServer):
    stop = False

    def serve_forever(self, controller):
        LOGGER.error('starting forever loop')
        self.RequestHandlerClass.ctlnode = controller

        while not self.stop:
            http.server.HTTPServer.handle_request(self)

    def stop_server(self):
        self.stop = True
