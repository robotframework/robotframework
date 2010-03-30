from robot import run as run_robot
import cProfile
import pstats


filename = 'robot.profile'
cProfile.run('run_robot("/home/husa/workspace/robotframework/atest/testdata/misc/")', filename)
p = pstats.Stats(filename)
p.strip_dirs().sort_stats(-1).print_stats()

