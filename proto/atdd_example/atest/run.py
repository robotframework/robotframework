from os.path import dirname, join
import subprocess

basedir = dirname(__file__)
cmd = ['pybot', '--outputdir', join(basedir, 'results'), join(basedir, 'vacalc')]
pythonpath = '%s:%s' % (join(basedir, 'lib'), join(basedir, '..', 'src'))

subprocess.call(' '.join(cmd), shell=True, env={'PYTHONPATH': pythonpath})
