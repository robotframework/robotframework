"""Robot Framework Library Uploader

Usage:  python rfdoc_uploader.py host file_name

Example: python rfdoc_uploader.py ExampleLibrary_version_1.xml localhost:8000
"""

import sys
import re
from httplib import HTTPConnection
from HTMLParser import HTMLParser


class RFDocUploader(object):

    def upload(self, file_path, host):
        xml_file = open(file_path, 'rb')
        conn = HTTPConnection(host)
        try:
            return self._upload(conn, xml_file)
        finally:
            xml_file.close()
            conn.close()

    def _upload(self, host, xml_file):
        resp = self._post_multipart(host, xml_file)
        return self._validate_success(resp)

    def _post_multipart(self, conn, xml_file):
        conn.connect()
        content_type, body = self._encode_multipart_formdata(xml_file)
        headers = {'User-Agent': 'libdoc.py', 'Content-Type': content_type}
        conn.request('POST', '/upload/', body, headers)
        return conn.getresponse()

    def _encode_multipart_formdata(self, xml_file):
        boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
        body = """--%(boundary)s
Content-Disposition: form-data; name="override"

on
--%(boundary)s
Content-Disposition: form-data; name="file"; filename="%(filename)s"
Content-Type: text/xml

%(content)s
--%(boundary)s--
""" % {'boundary': boundary, 'filename': xml_file.name, 'content': xml_file.read()}
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body.replace('\n', '\r\n')

    def _validate_success(self, resp):
        html = resp.read()
        if resp.status != 200:
            return [resp.reason.strip()]
        if 'Successfully uploaded library' in html:
            return None
        return _ErrorParser(html).errors


class _ErrorParser(HTMLParser):

    def __init__(self, html):
        HTMLParser.__init__(self)
        self._inside_errors = False
        self.errors = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attributes):
        if ('class', 'errorlist') in attributes:
            self._inside_errors = True

    def handle_endtag(self, tag):
        if tag == 'ul':
            self._inside_errors = False

    def handle_data(self, data):
        if self._inside_errors and data.strip():
            self.errors.append(data)


if __name__ == '__main__':
    try:
        errors = RFDocUploader().upload(*sys.argv[1:])
    except TypeError:
        print __doc__
        sys.exit(-1)
    except Exception, err:
        errors = [str(err)]
    else:
        print 'Library successfully uploaded'
        sys.exit(0)
    print 'Failed to upload library:\n%s' % '\n'.join(errors)
    sys.exit(1)

