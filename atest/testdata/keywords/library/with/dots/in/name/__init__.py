class name:

    def get_keyword_names(self):
        return ['No dots in keyword name in library with dots in name',
                'Dots.in.name.in.a.library.with.dots.in.name',
                'Multiple...dots . . in . a............row.in.a.library.with.dots.in.name',
                'Ending with a dot. In a library with dots in name.',
                'Conflict']

    def run_keyword(self, name, args):
        print("Running keyword '%s'." % name)
        return '-'.join(args)
