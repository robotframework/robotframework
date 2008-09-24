import sys
import xmlrpclib
import time
import socket
import os


class Library:

    def __init__(self, lang):
        ext = {'python': 'py', 'jython': 'py', 'ruby': 'rb', 'perl': 'pl'}[lang]
        cmd = '%s %s/examplelibrary.%s' % (lang, lang, ext)
        stdin, self._stdout, self._stderr = os.popen3(cmd)
        stdin.close()
        time.sleep(1)  # TODO: Test server is available instead of sleeping

    def stop(self, port=8270):
        server = xmlrpclib.ServerProxy('http://localhost:%s' % port)
        server.stop_remote_server()
        self._stdout.close()
        self._stderr.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Will get an usage here..."
    lang = sys.argv[1]
    include = lang if lang != 'jython' else 'python'
    args = 'test' if len(sys.argv) == 2 else ' '.join(sys.argv[2:])
    lib = Library(lang)
    os.system('pybot --log none --report none --output logs/output.xml '
              '--name %s --include %s %s' % (lang, include, args))
    lib.stop()
    os.system('../../tools/statuschecker/statuschecker.py logs/output.xml')
    rc = os.system('rebot --outputdir logs logs/output.xml') >> 8
    if rc == 0:
        print 'All tests passed'
    else:
        print '%d test%s failed' % (rc, 's' if rc != 1 else '')
