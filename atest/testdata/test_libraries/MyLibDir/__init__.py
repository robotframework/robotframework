from robot.utils import seq2str2


class MyLibDir:

    def get_keyword_names(self):
        return ["Keyword In My Lib Dir"]

    def run_keyword(self, name, args):
        return f"Executed keyword '{name}' with args {seq2str2(args)}"
