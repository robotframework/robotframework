# coding=utf-8


class NonAsciiKeywordNames(object):

    def __init__(self, include_latin1=False):
        self.names = [u'Unicode nön-äscïï',
                      u'\u2603',  # snowman
                      bytes(u'UTF-8 nön-äscïï'.encode('UTF-8'))]
        if include_latin1:
            self.names.append(bytes(u'Latin1 nön-äscïï'.encode('latin1')))

    def get_keyword_names(self):
        return self.names

    def run_keyword(self, name, args):
        return name
