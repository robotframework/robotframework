from robot.output.jsonlogger import JsonLogger


class JsonOutputWriter(JsonLogger):

    def __init__(self, output, rpa=False):
        JsonLogger.__init__(self, output, rpa=rpa, generator='Rebot')

    def start_message(self, msg):
        self._write_message(msg)

    def end_result(self, result):
        self.close()


class JsonWriter(object):

    def __init__(self, execution_result):
        self._execution_result = execution_result

    def write(self, output):
        writer = JsonOutputWriter(output)
        self._execution_result.visit(writer)
