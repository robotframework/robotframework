# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/336012

import SimpleHTTPServer
import BaseHTTPServer
import httplib


class _StoppableHttpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """http request handler with QUIT stopping the server"""

    def do_QUIT(self):
        """send 200 OK response, and set server.stop to True"""
        self.send_response(200)
        self.end_headers()
        self.server.stop = True


class _StoppableHttpServer(BaseHTTPServer.HTTPServer):
    """http server that reacts to self.stop flag"""

    def serve_forever(self):
        """Handle one request at a time until stopped."""
        self.stop = False
        while not self.stop:
            self.handle_request()


def start_server(port=7272):
    server = _StoppableHttpServer(('', port), _StoppableHttpRequestHandler)
    server.serve_forever()

    
def stop_server(port=7272):
    """send QUIT request to http server running on localhost:<port>"""
    conn = httplib.HTTPConnection("localhost:%d" % port)
    conn.request("QUIT", "/")
    conn.getresponse()

    
if __name__ == '__main__':
    import sys
    import os
    
    if len(sys.argv) != 2 or sys.argv[1] not in [ 'start', 'stop' ]:
        print 'usage: %s start|stop' % sys.argv[0]
        sys.exit(1)
    if sys.argv[1] == 'start':
        basedir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(basedir)
        start_server()
    else:
        stop_server()


