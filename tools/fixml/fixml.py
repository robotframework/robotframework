#!/usr/bin/env python

import sys
from BeautifulSoup import BeautifulStoneSoup


class Fixml(BeautifulStoneSoup):
    close_on_open = None
    NESTABLE_TAGS = {
                     'suite': ['robot','suite', 'statistics'],
                     'doc': ['suite', 'test', 'kw'],
                     'metadata': ['suite'],
                     'item': ['metadata'],
                     'status': ['suite', 'test', 'kw'],
                     'test': ['suite'],
                     'tags': ['test'],
                     'tag': ['tags'],
                     'kw': ['suite', 'test', 'kw'],
                     'msg': ['kw', 'errors'],
                     'arguments': ['kw'],
                     'arg': ['arguments'],
                     'statistics': ['robot'],
                     'errors': ['robot'],
                     }

    def unknown_starttag(self, name, *args):
        if self.close_on_open:
            self._popToTag(self.close_on_open)
            self.close_on_open = None
        BeautifulStoneSoup.unknown_starttag(self, name, *args)

    def unknown_endtag(self, name):
        BeautifulStoneSoup.unknown_endtag(self, name)
        if name == 'status':
            self.close_on_open = self.tagStack[-1].name
        else:
            self.close_on_open = None

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        print __doc__
        sys.exit(1)
    outfile = open(args[1], 'w')
    outfile.write(str(Fixml(open(args[0]))))
    outfile.close()
