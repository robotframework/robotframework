import os

DICT_FROM_VAR_FILE = dict(a='1', b=2, c='3')
ESCAPED_FROM_VAR_FILE = {'${a}': 'c:\\temp',
                         'b': '${2}',
                         os.sep: '\n' if os.sep == '/' else '\r\n',
                         '4=5\\=6': 'value'}


class ClassFromVarFile:
    attribute = DICT_FROM_VAR_FILE

    def get_escaped(self):
        return ESCAPED_FROM_VAR_FILE


OBJECT_FROM_VAR_FILE = ClassFromVarFile()
