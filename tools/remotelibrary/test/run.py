#!/usr/bin/env python
"""Script for running the remote library tests against different servers.

Usage 1: run.py language[:runner] [[options] datasources]

Valid languages are 'python', 'jython' or 'ruby', and runner can
either by 'pybot' (default) or 'jybot'. By default, all tests under
'test/data' directory are run, but this can be changed by providing
options, which can be any Robot Framework command line options.

Usage 2: run.py stop [port]

Stops remote server in specified port. Default port is 8270.
"""
import sys
import xmlrpclib
import time
import os
import subprocess
import shutil
import socket

REMOTEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTDIR = os.path.join(REMOTEDIR, 'test', 'logs')
if os.path.exists(OUTPUTDIR):
    shutil.rmtree(OUTPUTDIR)
os.mkdir(OUTPUTDIR)


class Library:

    def __init__(self, language=None):
        if language:
            self._start_library(language)
            if not self.test(attempts=7):
                raise RuntimeError("Starting %s library failed" % language)

    def _start_library(self, lang):
        opts = self._environment_setup(lang)
        ext = {'python': 'py', 'jython': 'py', 'ruby': 'rb'}[lang]
        lib = os.path.join(REMOTEDIR, 'test', 'libs', 'examplelib.%s' % ext)
        stdout = os.path.join(OUTPUTDIR, 'stdout.txt')
        stderr = os.path.join(OUTPUTDIR, 'stderr.txt')
        cmd = '%s%s%s 1> %s 2> %s' % (lang, opts, lib, stdout, stderr)
        print 'Starting %s remote library with command:\n%s' % (lang, cmd)
        stdin, stdouterr = os.popen4(cmd) 
        stdin.close()
        stdouterr.close()

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
        if self.test(port):
            server = xmlrpclib.ServerProxy('http://localhost:%s' % port)
            server.stop_remote_server()
            print "Remote library on port %s stopped" % port


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    mode = sys.argv[1]
    if mode == 'stop':
        Library().stop(*sys.argv[2:])
        sys.exit()

    if ':' in mode:
        lang, runner = mode.split(':')
    else:
        lang, runner = mode, 'pybot'
    lib = Library(lang)
    include = lang if lang != 'jython' else 'python'
    output = os.path.join(OUTPUTDIR, 'output.xml')
    args = [runner, '--log', 'NONE', '--report', 'NONE', '--output', output,
            '--name', mode, '--include', include, '--noncritical', 'non-critical']
    if len(sys.argv) == 2:
        args.append(os.path.join(REMOTEDIR, 'test', 'atest'))
    else:
        args.extend(sys.argv[2:])
    print 'Running tests with command:\n%s' % ' '.join(args) 
    subprocess.call(args)
    lib.stop()
    print
    checker = os.path.join(REMOTEDIR, '..', 'statuschecker', 'statuschecker.py')
    subprocess.call(['python', checker, output])
    rc = subprocess.call(['rebot', '--noncritical', 'non-critical',
                          '--outputdir', OUTPUTDIR, output])
    if rc == 0:
        print 'All tests passed'
    else:
        print '%d test%s failed' % (rc, 's' if rc != 1 else '')
