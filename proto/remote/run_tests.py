#!/usr/bin/env python
"""Script for running the remote library tests against different servers.

Usage 1: run_tests.py lang [[options] datasources]

Valid languages are 'python', 'jython' or 'ruby'. By default, all
tests under 'test' directory are run, but this can be changed by
providing options, which can be any Robot Framework command line
options.

Usage 2: run_tests.py stop [port]

Stops remote server in specified port. Default port is 8270..
"""
import sys
import xmlrpclib
import time
import os
import socket


class Library:

    def __init__(self, lang=None):
        if lang is None:
            self._stdout = self._stderr = None
            return
        ext = {'python': 'py', 'jython': 'py', 'ruby': 'rb', 'perl': 'pl'}[lang]
        dirname = lang if lang != 'jython' else 'python'
        cmd = '%s %s/examplelibrary.%s' % (lang, dirname, ext)
        stdin, self._stdout, self._stderr = os.popen3(cmd)
        stdin.close()
        self.test(attempts=10)
        
    def test(self, port=8270, attempts=1):
        url = 'http://localhost:%s' % port
        for i in range(attempts):
            try:
                xmlrpclib.ServerProxy(url).get_keyword_names()
            except socket.error, (errno, errmsg):
                time.sleep(1)
            except xmlrpclib.Error, err:
                errmsg = err.faultString
                break
            else:
                print "Server is running on port %s." % port
                return True
        print "Failed to connect to server on port %s: %s" % (port, errmsg)
        return False

    def stop(self, port=8270):
        if not self.test(port):
            return
        xmlrpclib.ServerProxy('http://localhost:%s' % port).stop_remote_server()
        if self._stdout:
            self._stdout.close()
            self._stderr.close()
        print "Server on port %s stopped." % port


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    lang = sys.argv[1]
    if lang == 'stop':
        Library().stop(*sys.argv[2:])
        sys.exit()
    
    include = lang if lang != 'jython' else 'python'
    args = 'test' if len(sys.argv) == 2 else ' '.join(sys.argv[2:])
    lib = Library(lang)
    os.system('pybot --log none --report none --output logs/output.xml '
              '--name %s --include %s %s' % (lang, include, args))
    lib.stop()
    print
    os.system('../../tools/statuschecker/statuschecker.py logs/output.xml')
    rc = os.system('rebot --outputdir logs logs/output.xml') >> 8
    if rc == 0:
        print 'All tests passed'
    else:
        print '%d test%s failed' % (rc, 's' if rc != 1 else '')
