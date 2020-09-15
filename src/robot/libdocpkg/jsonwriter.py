from robot.htmldata.jsonwriter import JsonDumper
from robot.libdocpkg.htmlwriter import DocFormatter, JsonConverter
from robot.utils import file_writer


class LibdocJsonWriter(object):
    def write(self, libdoc, output):
        formatter = DocFormatter(libdoc.keywords, libdoc.doc, libdoc.doc_format)
        libdocJsonData = JsonConverter(formatter).convert(libdoc)
        with file_writer(output) as f:
            JsonDumper(f).dump(libdocJsonData)