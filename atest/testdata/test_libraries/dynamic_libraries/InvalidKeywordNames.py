class InvalidKeywordNames:

    def __init__(self, hybrid=False):
        if not hybrid:
            self.run_keyword = lambda *args: None

    def get_keyword_names(self):
        return 1
