#!/usr/bin/env python3

import os
import shutil
from optparse import OptionParser
from os.path import abspath, dirname, join, normpath
from subprocess import call
from sys import exit


class GenerateApiDocs:
    BUILD_DIR = abspath(dirname(__file__))
    AUTODOC_DIR = join(BUILD_DIR, 'autodoc')
    ROOT = normpath(join(BUILD_DIR, '..', '..'))
    ROBOT_DIR = join(ROOT, 'src', 'robot')

    def __init__(self):
        try:
            import sphinx as _
        except ImportError:
            exit('Generating API docs requires Sphinx')
        self.options = GeneratorOptions()

    def run(self):
        self.create_autodoc()
        orig_dir = abspath(os.curdir)
        os.chdir(self.BUILD_DIR)
        rc = call(['make', 'html'], shell=os.name == 'nt')
        os.chdir(orig_dir)
        print(abspath(join(self.BUILD_DIR, '_build', 'html', 'index.html')))
        exit(rc)

    def create_autodoc(self):
        print('Generating autodoc')
        self._clean_directory(self.AUTODOC_DIR)
        command = ['sphinx-apidoc',
                   '--output-dir', self.AUTODOC_DIR,
                   '--force',
                   '--no-toc',
                   '--maxdepth', '2',
                   '--module-first',
                   self.ROBOT_DIR]
        print(' '.join(command))
        call(command)

    def _clean_directory(self, dirname):
        if os.path.exists(dirname):
            print('Cleaning', dirname)
            shutil.rmtree(dirname)


class GeneratorOptions:
    usage = '''
    generate.py [options]

    This script creates API documentation from Python source code
    included in `src/python. Python autodocs are
    created in `doc/api/autodoc`.

    API documentation entry point is create using Sphinx's `make html`.

    Sphinx and sphinx-apidoc commands need to be in $PATH.
    '''

    def __init__(self):
        self._parser = OptionParser(self.usage)
        self._options, _ = self._parser.parse_args()


if __name__ == '__main__':
    GenerateApiDocs().run()
