import os
import sys
import subprocess
import datetime
import tempfile

from vacalc import Employee, EmployeeStore, Vacation


class VacalcLibrary(object):

    def __init__(self):
        self._db_file = os.path.join(tempfile.gettempdir(),
                                     'vacalc-atestdb.csv')

    def count_vacation(self, startdate, year):
        resource = Employee('Test Resource', startdate)
        return Vacation(resource.startdate, int(year)).days

    def clear_database(self):
        if os.path.isfile(self._db_file):
            print 'Removing %s' % self._db_file
            os.remove(self._db_file)

    def add_employee(self, name, startdate):
        self._run('add_employee', name, startdate)

    def get_employee(self, name):
        self._run('get_employee', name)

    def show_vacation(self, name, year):
        self._run('show_vacation', name, year)

    def _run(self, command, *args):
        cmd = [sys.executable, 'vacalc.py', command] + list(args)
        print subprocess.list2cmdline(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                env={'VACALC_DB': self._db_file})
        self._status = proc.stdout.read().strip()
        print self._status

    def status_should_be(self, status):
        if self._status != status:
            raise AssertionError("Expected status to be '%s' but it was '%s'"
                                % (status, self._status))
