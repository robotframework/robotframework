#!/usr/bin/env python

import sys

stdout = sys.argv[1] if len(sys.argv) > 1 else 'stdout'
stderr = sys.argv[2] if len(sys.argv) > 2 else 'stderr'
rc = int(sys.argv[3]) if len(sys.argv) > 3 else 0

sys.stdout.write(stdout + '\n')
sys.stderr.write(stderr + '\n')
sys.exit(rc)
