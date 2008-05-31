import os
import tempfile


class ListenSome:
    
    def __init__(self):
        outpath = os.path.join(tempfile.gettempdir(), 'listen_some.txt')
        self.outfile = open(outpath, 'w')
        
    def startTest(self, name, doc, tags):
        self.outfile.write(name + '\n')

    def endSuite(self, stat, msg):
        self.outfile.write(msg + '\n')
        
    def close(self):
        self.outfile.close()
        
        
class InvalidInit:
    
    def __init__(self, args, arenot, allowed, here):
        pass


class InvalidMethods:
    
    def start_suite(self, wrong, number, of, args, here):
        pass
    
    def end_suite(self, *args):
        raise RuntimeError("Here comes an exception!")
