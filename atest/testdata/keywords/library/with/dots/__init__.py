class dots(object):

    def get_keyword_names(self):
        return ['In.name.conflict']

    def run_keyword(self, name, args):
        return '-'.join(args)
