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
    JAVA_SRC = join(ROOT, 'src', 'java')
    JAVA_TARGET = join(BUILD_DIR, '_static', 'javadoc')

    def __init__(self):
        try:
            import sphinx as _
        except ImportError:
            exit('Generating API docs requires Sphinx')
        self.options = GeneratorOptions()

    def run(self):
        self.create_autodoc()
        if self.options.javadoc:
            self.create_javadoc()
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

    def create_javadoc(self):
        print('Generating javadoc')
        self._clean_directory(self.JAVA_TARGET)
        command = ['javadoc',
                   '-locale', 'en_US',
                   '-sourcepath', self.JAVA_SRC,
                   '-d', self.JAVA_TARGET,
                   '-notimestamp',
                   'org.robotframework']
        print(' '.join(command))
        call(command)

    def _clean_directory(self, dirname):
        if os.path.exists(dirname):
            print('Cleaning', dirname)
            shutil.rmtree(dirname)


class GeneratorOptions:
    usage = '''
    generate.py [options]

    This script creates API documentation from both Python and Java source code
    included in `src/python and `src/java`, respectively. Python autodocs are
    created in `doc/api/autodoc` and Javadocs in `doc/api/_static/javadoc`.

    API documentation entry point is create using Sphinx's `make html`.

    Sphinx, sphinx-apidoc and javadoc commands need to be in $PATH.
    '''

    def __init__(self):
        self._parser = OptionParser(self.usage)
        self._add_options()
        self._options, _ = self._parser.parse_args()
        if not self._options.javadoc:
            self._prompt_for_generation('javadoc')

    @property
    def javadoc(self):
        return self._options.javadoc

    def _add_options(self):
        self._parser.add_option('-j', '--javadoc',
            action='store_true',
            dest='javadoc',
            help='Generates Javadoc'
        )

    def _prompt_for_generation(self, attr_name):
        selection = input('Generate also %s? '
                          '[Y/N] (N by default) > ' % attr_name.title())
        if selection and selection[0].lower() == 'y':
            setattr(self._options, attr_name, True)


if __name__ == '__main__':
    GenerateApiDocs().run()
