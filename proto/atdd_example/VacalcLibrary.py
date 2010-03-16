import os
import sys
import subprocess
import datetime

from vacalc import Employee, EmployeeStore, Vacation


class VacalcLibrary(object):

    def __init__(self, db_file='db.csv'):
        self._db_file = db_file

    def count_vacation(self, startdate, year):
        resource = Employee('Test Resource', startdate)
        return Vacation(resource._startdate, int(year)).days

    def clear_database(self):
        if os.path.isfile(self._db_file):
            os.remove(self._db_file)

    def add_employee(self, name, startdate):
        self._run('add_employee', name, startdate)

    def get_employee(self, name):
        self._run('get_employee', name)

    def _run(self, command, *args):
        cmd = [sys.executable, 'vacalc.py', command] + list(args)
        print subprocess.list2cmdline(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self._status = proc.stdout.read().strip()
        print self._status

    def status_should_be(self, status):
        if self._status != status:
            raise AssertionError("Expected status to be '%s' but it was '%s'"
                                % (status, self._status))


