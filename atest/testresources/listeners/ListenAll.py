import os
import tempfile
import time


class ListenAll:

    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, *path):
        if not path:
            path = os.path.join(tempfile.gettempdir(), 'listen_all.txt')
        else:
            path = ':'.join(path)
        self.outfile = open(path, 'w')

    def start_suite(self, name, attrs):
        metastr = ' '.join(['%s: %s' % (k, v) for k, v
                            in attrs['metadata'].items()])
        self.outfile.write("SUITE START: %s '%s' [%s]\n"
                           % (name, attrs['doc'], metastr))

    def start_test(self, name, attrs):
        tags = [ str(tag) for tag in attrs['tags'] ]
        self.outfile.write("TEST START: %s '%s' %s\n" % (name, attrs['doc'], tags))

    def start_keyword(self, name, attrs):
        args = [ str(arg) for arg in attrs['args'] ]
        self.outfile.write("KW START: %s %s\n" % (name, args))

    def log_message(self, message):
        msg, level = self._check_message_validity(message)
        if level != 'TRACE' and 'Traceback' not in msg:
            self.outfile.write('LOG MESSAGE: [%s] %s\n' % (level, msg))

    def message(self, message):
        msg, level = self._check_message_validity(message)
        if 'Settings' in msg:
            self.outfile.write('Got settings on level: %s\n' % level)

    def _check_message_validity(self, message):
        if message['html'] not in ['yes', 'no']:
            self.outfile.write('Log message has invalid `html` attribute %s' %
                               message['html'])
        if not message['timestamp'].startswith(str(time.localtime()[0])):
            self.outfile.write('Log message has invalid timestamp %s' %
                               message['timestamp'])
        return message['message'], message['level']

    def end_keyword(self, name, attrs):
        self.outfile.write("KW END: %s\n" % (attrs['status']))

    def end_test(self, name, attrs):
        if attrs['status'] == 'PASS':
            self.outfile.write('TEST END: PASS\n')
        else:
            self.outfile.write("TEST END: %s %s\n"
                               % (attrs['status'], attrs['message']))

    def end_suite(self, name, attrs):
        self.outfile.write('SUITE END: %s %s\n'
                            % (attrs['status'], attrs['statistics']))

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
