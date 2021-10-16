import sys

from remoteserver import RemoteServer, keyword


class KeywordTags:

    def no_tags(self):
        pass

    def doc_contains_tags_only(self):
        """Tags: foo, bar"""

    def doc_contains_tags_after_doc(self):
        """This is by doc.

        My doc has multiple lines.

        Tags: these, are, my, tags
        """

    @keyword
    def empty_robot_tags_means_no_tags(self):
        pass

    @keyword(tags=['foo', 'bar', 'FOO', '42'])
    def robot_tags(self):
        pass

    @keyword(tags=['foo', 'bar'])
    def robot_tags_and_doc_tags(self):
        """Tags: bar, zap"""


if __name__ == '__main__':
    RemoteServer(KeywordTags(), *sys.argv[1:])
