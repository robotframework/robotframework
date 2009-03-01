import tempfile
import os

from docutils.core import publish_cmdline, default_description

from htmlreader import HtmlReader


class RestReader(HtmlReader):

    def read(self, rstfile, rawdata):
        filedesc, htmlfilename = tempfile.mkstemp('.html')
        os.close(filedesc)
        self.publish(rstfile.name, htmlfilename)
        suiteData = HtmlReader.read(self, file(htmlfilename), rawdata)
        os.remove(htmlfilename)
        return suiteData 

    def publish(self, rstFilename, htmlFilename):
        description = ('Generates (X)HTML documents from standalone reStructuredText sources.  ' + default_description)
        publish_cmdline(writer_name='html', argv=[rstFilename, htmlFilename], description=description)
    
        

