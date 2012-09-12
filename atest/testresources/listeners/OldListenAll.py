import os


class OldListenAll:

    def __init__(self, *path):
        if not path:
            path = os.path.join(os.getenv('TEMPDIR'), 'listen_all.txt')
        else:
            path = ':'.join(path)
        self.outfile = open(path, 'w')

    def start_suite(self, name, doc):
        self.outfile.write("SUITE START: %s '%s'\n" % (name, doc))

    def start_test(self, name, doc, tags):
        tags = [str(tag) for tag in tags]
        self.outfile.write("TEST START: %s '%s' %s\n" % (name, doc, tags))

    def start_keyword(self, name, args):
        args = [str(arg) for arg in args]
        self.outfile.write("KW START: %s %s\n" % (name, args))

    def end_keyword(self, status):
        self.outfile.write("KW END: %s\n" % (status))

    def end_test(self, status, message):
        if status == 'PASS':
            self.outfile.write('TEST END: PASS\n')
        else:
            self.outfile.write("TEST END: %s %s\n" % (status, message))

    def end_suite(self, status, message):
        self.outfile.write('SUITE END: %s %s\n' % (status, message))

    def output_file(self, path):
        self._out_file('Output', path)

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
