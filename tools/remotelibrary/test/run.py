#!/usr/bin/env python
"""Script for running the remote library tests against different servers.

Usage 1: run.py lang [[options] datasources]

Valid languages are 'python', 'jython' or 'ruby'. By default, all tests
under 'test/data' directory are run, but this can be changed by providing
options, which can be any Robot Framework command line options.

Usage 2: run.py stop [port]

Stops remote server in specified port. Default port is 8270..
"""
import sys
import xmlrpclib
import time
import os
import socket

REMOTEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTDIR = os.path.join(REMOTEDIR, 'test', 'logs')


class Library:

    def __init__(self, language=None):
        self._stdout = self._stderr = None
        self.language = language
        if language:
            self._start_library(language)
            if not self.test(attempts=7):
                raise RuntimeError("Starting %s library failed" % language)

    def _start_library(self, lang):
        opts = self._environment_setup(lang)
        ext = {'python': 'py', 'jython': 'py', 'ruby': 'rb'}[lang]
        cmd = '%s%s%s' % (lang, opts, os.path.join(REMOTEDIR, 'test', 'libs',
                                                   'examplelibrary.%s' % ext))
        print 'Starting %s remote library with command:\n%s' % (lang, cmd)
        stdin, self._stdout, self._stderr = os.popen3(cmd)
        stdin.close()

    def _environment_setup(self, lang):
        if lang == 'jython':
            return ' -Dpython.path=%s ' % REMOTEDIR
        varname = {'python': 'PYTHONPATH', 'ruby': 'LOAD_PATH'}[lang]
        os.environ[varname] = REMOTEDIR
        print '%s: %s' % (varname, REMOTEDIR)
        return ' '

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
                print "Remote library is running on port %s" % port
                return True
        print "Failed to connect to library on port %s: %s" % (port, errmsg)
        return False

    def stop(self, port=8270):
        if not self.test(port):
            return
        xmlrpclib.ServerProxy('http://localhost:%s' % port).stop_remote_server()
        if self._stdout:
            self._stdout.close()
            self._stderr.close()
        print "Remote library on port %s stopped" % port


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    if sys.argv[1] == 'stop':
        Library().stop(*sys.argv[2:])
        sys.exit()
    
    lib = Library(sys.argv[1])
    include = lib.language if lib.language != 'jython' else 'python'
    if len(sys.argv) == 2:
        args = os.path.join(REMOTEDIR, 'test', 'data')
    else:
        args = ' '.join(sys.argv[2:])
    os.system('pybot --log none --report none --output %s/output.xml --name %s '
              '--include %s %s' % (OUTPUTDIR, lib.language, include, args))
    lib.stop()
    print
    os.system('python %s/../statuschecker/statuschecker.py %s/output.xml'
              % (REMOTEDIR, OUTPUTDIR))
    rc = os.system('rebot --outputdir %s %s/output.xml' % (OUTPUTDIR, OUTPUTDIR))
    if os.name != 'nt':
        rc = rc >> 8
    if rc == 0:
        print 'All tests passed'
    else:
        print '%d test%s failed' % (rc, 's' if rc != 1 else '')
