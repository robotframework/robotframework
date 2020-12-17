import sys

from remoteserver import RemoteServer, keyword


class BulkLoadRemoteServer(RemoteServer):

    def _register_functions(self):
        """
        Individual get_keyword_* methods are not registered.
        This removes the fall back scenario should get_library_information fail.
        """
        self.register_function(self.get_library_information)
        self.register_function(self.run_keyword)

    def get_library_information(self):
        info_dict = dict()
        for kw in self.get_keyword_names():
            kw_dict = dict()
            kw_dict['args'] = self.get_keyword_arguments(kw)
            kw_dict['tags'] = self.get_keyword_tags(kw)
            kw_dict['doc'] = self.get_keyword_documentation(kw)
            info_dict[kw] = kw_dict
        return info_dict

class The10001KeywordsLibrary(object):

    def __init__(self):
        def count(n): return lambda: "%d"%n
        for i in range(10000):
            setattr(self, "keyword_%d"%i, count(i))

    def some_keyword(self):
        return "some"


if __name__ == '__main__':
    BulkLoadRemoteServer(The10001KeywordsLibrary(), *sys.argv[1:])
