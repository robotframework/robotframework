#!/usr/bin/env python

import os
import sys


class ExampleRemoteLibrary:

    def count_items_in_directory(self, path):
        return len([i for i in os.listdir(path) if not i.startswith('.')])

    def strings_should_be_equal(self, str1, str2):
        print "Comparing '%s' to '%s'" % (str1, str2)
        if str1 != str2:
            raise AssertionError("Given strings are not equal")


if __name__ == '__main__':
    from robotremoteserver import RobotRemoteServer
    RobotRemoteServer(ExampleRemoteLibrary(), *sys.argv[1:])
