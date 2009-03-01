import tempfile
import os

from docutils.core import publish_cmdline

from htmlreader import HtmlReader


class RestReader(HtmlReader):

    def read(self, rstfile, rawdata):
        htmlpath = self._rest_to_html(rstfile.name)
        try:
            htmlfile = open(htmlpath, 'rb')
            return HtmlReader.read(self, htmlfile, rawdata)
        finally:
            os.remove(htmlpath)
            htmlfile.close()

    def _rest_to_html(self, rstpath):
        filedesc, htmlpath = tempfile.mkstemp('.html')
        os.close(filedesc)
        publish_cmdline(writer_name='html', argv=[rstpath, htmlpath])
        return htmlpath
        

