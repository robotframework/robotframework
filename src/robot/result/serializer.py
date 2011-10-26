class ResultSerializer(object):

    def __init__(self, output):
        self._output = output

    def to_xml(self, suite):
        self._output.write('''<?xml version="1.0" encoding="UTF-8"?>
<robot>
<suite name="name">
</suite>
</robot>
''')
