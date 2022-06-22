from robot.libraries.BuiltIn import BuiltIn


class ParameterLibrary:

    def __init__(self, host='localhost', port='8080'):
        self.host = host
        self.port = port

    def parameters(self):
        return self.host, self.port

    def parameters_should_be(self, host='localhost', port='8080'):
        should_be_equal = BuiltIn().should_be_equal
        should_be_equal(self.host, host)
        should_be_equal(self.port, port)


class V1(ParameterLibrary): pass
class V2(ParameterLibrary): pass
class V3(ParameterLibrary): pass
class V4(ParameterLibrary): pass
class V5(ParameterLibrary): pass
class V6(ParameterLibrary): pass
