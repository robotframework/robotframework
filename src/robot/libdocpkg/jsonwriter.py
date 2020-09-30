from robot.utils import file_writer
import json


class LibdocJsonWriter(object):

    def __init__(self, force_html_doc=False):
        self._force_html_doc = force_html_doc

    def write(self, libdoc, output):
        if self._force_html_doc:
            libdoc.convert_doc_to_html()
        with file_writer(output) as f:
            f.write(json.dumps(libdoc.to_dictionary(), indent=2))
