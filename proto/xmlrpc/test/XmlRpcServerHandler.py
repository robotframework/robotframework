import sys
import xmlrpclib
import time
import socket
import os.path

        
def stop_xmlrpc_server(port):
    url = 'http://localhost:%s' % port
    server = xmlrpclib.ServerProxy(url)
    server.stop()  #.robotframework.stop()
    print "Stopped server at %s" % url
    
def test_xmlrpc_server(port, attempts=1):
    url = 'http://localhost:%s' % port
    for i in range(int(attempts)):
        try:
            server = xmlrpclib.ServerProxy(url)
            if not server.robotframework.get_keyword_names():
                raise AssertionError("Server at %s returned no keyword names"
                                     % url)
        except socket.error:
            if i+1 >= attempts:
                break
            print "Attempt %d failed. Will try again shortly." % (i+1)
            time.sleep(1)
        else:
            print "Server at %s seems to work ok" % url
            return
    raise AssertionError("Failed to connect to server at %s" % url)
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage:  %s stop|test port" % os.path.basename(sys.argv[0])
        sys.exit(1)
    mode, port = sys.argv[1:3]
    if mode.upper() == 'STOP':
        stop_xmlrpc_server(port)
    else:
        test_xmlrpc_server(port)
