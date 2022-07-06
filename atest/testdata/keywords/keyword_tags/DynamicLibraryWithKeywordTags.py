class DynamicLibraryWithKeywordTags:

    def get_keyword_names(self):
        return ['dynamic_library_keyword_with_tags']

    def run_keyword(self, name, *args):
        return None

    def get_keyword_documentation(self, name):
        return 'Summary line\nTags: foo, bar'
