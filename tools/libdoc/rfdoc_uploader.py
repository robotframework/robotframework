"""Robot Framework Library and Resource File Documentation Uploader

Usage:  python rfdoc_uploader.py url file_name [--o]
options:
    --o    Overwrites the documentation in the server, if it already exists.
"""

import sys
import re
from httplib import HTTPConnection


class RFDocUploader(object):
    
    def upload(self, file_path, url, override=True):
        fields = {'override': 'true'}
        resp = self._post_multipart(url, fields, file_path, override)
        success = self._validate_success(resp)
        print 'SUCCESS: ', success

    def _post_multipart(self, host, fields, file_path, override):
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
        reason = resp.reason
        html = resp.read()
        print html
        if status is not '200' and re.search('Successfully uploaded library', html):
            return True
        # TODO parse error messages
        return False

def main(args):
    if len(args) < 2 or len(args) > 3:
        print __doc__
        sys.exit()
    file_path = args[0]
    url = args[1]
    override = False
    if len(args) == 3:
        if args[2] == '--o':
            override = True
        else:
            print __doc__
            sys.exit()
    RFDocUploader().upload(file_path, url, override)   

if __name__ == '__main__':
    main(sys.argv[1:])