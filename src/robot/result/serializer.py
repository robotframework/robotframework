from robot.output.xmllogger import XmlLogger

class ResultWriter(XmlLogger):

    def close(self):
        self._writer.end('robot')

class ResultSerializer(object):

    def __init__(self, output):
        self._output = output

    def to_xml(self, suite):
        logger = ResultWriter(self._output)
        suite.visit(logger)
        logger.close()
