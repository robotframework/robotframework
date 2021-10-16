KWS = {
    'Only tags in documentation': ('Tags: tag1, tag2', None),
    'Tags in addition to normal documentation': ('Normal doc\n\n...\n\nTags: tag', None),
    'Tags from get_keyword_tags': (None, ['t1', 't2', 't3']),
    'Tags both from doc and get_keyword_tags': ('Tags: 1, 2', ['4', '2', '3'])
}


class DynamicLibraryTags:
    get_keyword_tags_called = False

    def get_keyword_names(self):
        return list(KWS)

    def run_keyword(self, name, args, kwags):
        pass

    def get_keyword_documentation(self, name):
        if not self.get_keyword_tags_called:
            raise AssertionError("'get_keyword_tags' should be called before "
                                 "'get_keyword_documentation'")
        return KWS[name][0]

    def get_keyword_tags(self, name):
        self.get_keyword_tags_called = True
        return KWS[name][1]
