import sys
import xmlrpclib
import time
import socket
import os.path

        
def stop_xmlrpc_server(port=8270):
    url = 'http://localhost:%s' % port
    server = xmlrpclib.ServerProxy(url)
    server.stop()  #.robotframework.stop()
    print "Stopped server at %s" % url
    
def test_xmlrpc_server(port=8072, attempts=1):
    url = 'http://localhost:%s' % port
    attempts = int(attempts)
    for i in range(attempts):
        try:
            server = xmlrpclib.ServerProxy(url)
            if not server.robotframework.get_keyword_names():
                print "Server at %s returned no keyword names" % url
                return
        except socket.error:
            if attempts == 1:
                break
            print "Attempt %d/%d failed." % (i+1, int(attempts))
            time.sleep(1)
        else:
            print "Server at %s seems to work ok" % url
            return
    print "Failed to connect to server at %s" % url
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage:  %s stop|test [port]" % os.path.basename(sys.argv[0])
        sys.exit(1)
    if sys.argv[1].upper() == 'STOP':
        stop_xmlrpc_server(*sys.argv[2:])
    else:
        test_xmlrpc_server(*sys.argv[2:])
