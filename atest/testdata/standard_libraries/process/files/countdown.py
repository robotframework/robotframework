import subprocess
import sys
import time


def countdown(path):
    for i in range(10, 0, -1):
        with open(path, 'w') as f:
            f.write('%d\n' % i)
        time.sleep(0.2)
    with open(path, 'w') as f:
        f.write('BLASTOFF')


if __name__ == '__main__':
    path = sys.argv[1]
    children = int(sys.argv[2]) if len(sys.argv) == 3 else 0

    if children:
        subprocess.Popen([sys.executable, __file__, path, str(children-1)]).wait()
    else:
        countdown(path)
