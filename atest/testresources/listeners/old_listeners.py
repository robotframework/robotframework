import os


class ListenSome:
    ROBOT_LISTENER_API_VERSION = 1

    def __init__(self):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listen_some.txt')
        self.outfile = open(outpath, 'w')

    def startTest(self, name, doc, tags):
        self.outfile.write(name + '\n')

    def endSuite(self, stat, msg):
        self.outfile.write(msg + '\n')

    def close(self):
        self.outfile.close()


class WithArgs(object):

    def __init__(self, arg1, arg2='default'):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listener_with_args.txt')
        outfile = open(outpath, 'a')
        outfile.write("I got arguments '%s' and '%s'\n" % (arg1, arg2))
        outfile.close()


class InvalidMethods:

    def start_suite(self, wrong, number, of, args, here):
        pass

    def end_suite(self, *args):
        raise RuntimeError("Here comes an exception!")
