class EmbeddedArgs:

    def get_keyword_names(self):
        return ['Add ${count} Copies Of ${item} To Cart']

    def run_keyword(self, name, args):
        assert name == 'Add ${count} Copies Of ${item} To Cart'
        return args
