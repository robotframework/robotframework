import subprocess
import sys
import time


def countdown(path):
    with open(path, 'w') as f:
        for i in range(10, 0, -1):
            f.write('%d\n' % i)
            f.flush()
            time.sleep(0.1)
        f.write('BLASTOFF')


if __name__ == '__main__':
    path = sys.argv[1]
    children = int(sys.argv[2]) if len(sys.argv) == 3 else 0

    if children:
        subprocess.Popen([sys.executable, __file__, path, str(children-1)]).wait()
    else:
        countdown(path)
