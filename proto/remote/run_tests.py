import sys
import xmlrpclib
import time
import socket
import os

class Library:

    def __init__(self, lang):
        ext = {'python': 'py', 'ruby': 'rb', 'perl': 'pl'}[lang]
        cmd = '%s %s/examplelibrary.%s' % (lang, lang, ext)
        stdin, self._stdout, self._stderr = os.popen3(cmd)
        stdin.close()
        time.sleep(1)  # TODO: test condition

    def stop(self, port=8270):
        url = 'http://localhost:%s' % port
        server = xmlrpclib.ServerProxy(url)
        server.stop_remote_server()
        self._stdout.close()
        self._stderr.close()


    

if __name__ == '__main__':
    lang, path = sys.argv[1:3]
    lib = Library(lang)
    os.system('ROBOT_SYSLOG_FILE=sys.txt pybot --log none --report none --output logs/output.xml --include %s %s'
              % (lang, path))
    lib.stop()
    os.system('../../tools/statuschecker/statuschecker.py logs/output.xml')
    rc = os.system('rebot --outputdir logs logs/output.xml')
    print '%d tests failed' % (rc >> 8)


