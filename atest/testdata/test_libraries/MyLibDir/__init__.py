from robot import utils

class MyLibDir:
    
    def get_keyword_names(self):
        return ['Keyword In My Lib Dir']
    
    def run_keyword(self, name, args):
        return "Executed keyword '%s' with args %s" % (name, utils.seq2str2(args))
