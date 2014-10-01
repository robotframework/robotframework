# coding=utf-8

class NonAsciiKeywordNames(object):

    def get_keyword_names(self):
        return [u'Unicode nön-äscïï',
                u'\u2603',  # snowman
                u'UTF-8 nön-äscïï'.encode('UTF-8'),
                u'Latin1 nön-äscïï'.encode('latin1')]

    def run_keyword(self, name, args):
        return name
