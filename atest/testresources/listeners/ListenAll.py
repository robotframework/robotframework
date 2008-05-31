import os
import tempfile


class ListenAll:
    
    def __init__(self):
        outpath = os.path.join(tempfile.gettempdir(), 'listen_all.txt')
        self.outfile = open(outpath, 'w')
        
    def start_suite(self, name, doc):
        self.outfile.write("%s '%s'\n" % (name, doc))
        
    def start_test(self, name, doc, tags):
        self.outfile.write("- %s '%s' %s :: " % (name, doc, '[ %s ]' % ' | '.join(tags)))
        
    def end_test(self, status, message):
        if status == 'PASS':
            self.outfile.write('PASS\n')
        else:
            self.outfile.write('%s: %s\n' % (status, message))
            
    def end_suite(self, status, message):
        self.outfile.write('%s: %s\n' % (status, message))

    def output_file(self, path):
        self._out_file('Output', path)
            
    def summary_file(self, path):
        self._out_file('Summary', path)
                    
    def report_file(self, path):
        self._out_file('Report', path)
                    
    def log_file(self, path):
        self._out_file('Log', path)
                    
    def debug_file(self, path):
        self._out_file('Debug', path)
        
    def _out_file(self, name, path):
        assert os.path.isabs(path)
        self.outfile.write('%s: %s\n' % (name, os.path.basename(path)))
            
    def close(self):
        self.outfile.write('Closing...\n')
        self.outfile.close()