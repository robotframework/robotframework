import os

class ExampleRemoteLibrary:
    
    def count_files(self, path):
        return len([ f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

    def strings_should_be_equal(self, str1, str2):
        print "Comparing '%s' to '%s'" % (str1, str2)
        if str1 != str2:
            raise AssertionError("Given strings are not equal")


if __name__ == '__main__':
    import sys
    from robotremoteserver import RobotRemoteServer

    RobotRemoteServer(ExampleRemoteLibrary(), *sys.argv[1:])
