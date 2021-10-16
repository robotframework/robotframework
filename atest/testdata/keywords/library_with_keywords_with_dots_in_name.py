class library_with_keywords_with_dots_in_name:

    def get_keyword_names(self):
        return ['Dots.in.name.in.a.library',
                'Multiple...dots . . in . a............row.in.a.library',
                'Ending with a dot. In a library.']

    def run_keyword(self, name, args):
        return '-'.join(args)
