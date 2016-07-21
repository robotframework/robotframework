import sys
# based on a recipe from http://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
def get_os_platform():
    """return platform name, but for Jython it uses os.name Java property"""
    ver = sys.platform.lower()
    if ver.startswith('java'):
        import java.lang
        ver = java.lang.System.getProperty("os.name").lower()
    print('platform: %s' % (ver))
    return ver
