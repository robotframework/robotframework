import subprocess
import os
import signal

class JavaStarter(object):

    def __init__(self):
        self._jython_home = os.getenv('JYTHON_HOME')
        if not self._jython_home:
            return
        jython_jar = os.path.join(self._jython_home, 'jython.jar')
        self._classpath = jython_jar + os.pathsep + os.getenv('CLASSPATH','')
        java_home = os.getenv('JAVA_HOME')
        self._java = os.path.join(java_home, 'java') if java_home else 'java'

    def get_jython_path(self):
        if not self._jython_home:
            raise RuntimeError('This test requires JYTHON_HOME environment variable to be set.')
        return '%s -Dpython.home=%s -classpath %s org.python.util.jython' % (self._java,self._jython_home,self._classpath)


# CP="/home/peke/Prog/jython2.2/jython.jar"
# if [ ! -z "$CLASSPATH" ]
# then
#   CP=$CP:$CLASSPATH
# fi
# "/usr/bin/java" -Dpython.home="/home/peke/Prog/jython2.2" -classpath
# "$CP" org.python.util.jython "$@" 
