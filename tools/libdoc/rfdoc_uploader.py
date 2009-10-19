"""Robot Framework Library Uploader

Usage:  python rfdoc_uploader.py host file_name [--o]
options:
    --o    Overwrites the library in the server, if it already exists.

Example: python rfdoc_uploader.py ExampleLibrary_version_1.xml localhost:8000
"""

import sys
import re
from httplib import HTTPConnection
from htmllib import HTMLParser


class RFDocUploader(object):

    def upload(self, file_path, host, override=True):
        resp = self._post_multipart(host, file_path, override)
        return self._validate_success(resp)

    def _post_multipart(self, host, file_path, override):
        content_type, body = self._encode_multipart_formdata(file_path, override)
        conn = HTTPConnection(host)
        conn.connect()
        headers = {'User-Agent': 'Python post', 'Content-Type': content_type}
        conn.request('POST', '/upload/', body, headers)
        resp = conn.getresponse()
        conn.close()
        return resp

    def _encode_multipart_formdata(self, file_path, override):
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        if override:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="override"')
            L.append('')
            L.append('on')

        file = open(file_path, 'rb')
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="file"; filename="%s"' % file.name)
        L.append('Content-Type: %s' % 'Content-Type: text/xml') 
        L.append('')
        L.append(file.read())
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def _validate_success(self, resp):
        status = resp.status
        html = resp.read()
        if status is 200 and re.search('Successfully uploaded library', html):
            return None
        errors = self._parse_errors(html)
        return errors

    def _parse_errors(self, html):
        parser = _ErrorParser()
        parser.parse(html)
        parser.close()
        return parser.errors


class _ErrorParser(HTMLParser):
    _inside_errors = False
    _is_error_line = False

    def __init__(self, verbose=0):
        HTMLParser.__init__(self, verbose)
        self.errors = []

    def parse(self, html):
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, method, attributes):
        for attr in attributes:
            if attr[1] == 'errorlist':
                self._inside_errors = True
        if self._inside_errors and tag == 'li':
            self._is_error_line = True

    def handle_endtag(self, tag, method):
        if tag == 'ul' and self._inside_errors:
            self._inside_errors = False

    def handle_data(self, data):
        if self._is_error_line:
            self.errors.append(data)
            self._is_error_line = False


def main(args):
    if len(args) < 2 or len(args) > 3:
        print __doc__
        sys.exit()
    file_path = args[0]
    host = args[1]
    override = False
    if len(args) == 3:
        if args[2] == '--o':
            override = True
        else:
            print __doc__
            sys.exit()
    errors = RFDocUploader().upload(file_path, host, override)
    if not errors:
        print 'Library successfully uploaded!'
    else:
        print 'Failed to upload library! Errors:'
        for err in errors:
            print '    -', err

if __name__ == '__main__':
    main(sys.argv[1:])