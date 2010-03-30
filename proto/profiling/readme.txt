===================
Pycon Presentation:

http://us.pycon.org/2009/conference/schedule/event/15/


========================
Example cProfile Script:

from robot import run as run_robot
import cProfile
import pstats


filename = 'robot.profile'
cProfile.run('run_robot("/home/husa/workspace/robotframework/atest/testdata/misc/")', filename)
p = pstats.Stats(filename)
p.strip_dirs().sort_stats(-1).print_stats()


==============================
Viewers for the profile files:

1. Run Snake Run (http://www.vrplumber.com/programming/runsnakerun/)

installing: sudo easy_install RunSnakeRun
Examining the report after running cProfile: runsnake robot.profile

2. KCachegrind (http://kcachegrind.sourceforge.net/html/Home.html)

haven't tried this one yet

=================
Memory Profilers:

http://guppy-pe.sourceforge.net/#Heapy

http://pysizer.8325.org/

