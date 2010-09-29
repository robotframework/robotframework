from __future__ import with_statement
import os
import csv
import datetime


class VacalcError(RuntimeError): pass



class EmployeeStore(object):

    def __init__(self, db_file):
        self._db_file = db_file
        if self._db_file and os.path.isfile(self._db_file):
            self._employees = self._read_employees(self._db_file)
        else:
            self._employees = {}

    def _read_employees(self, path):
        employees = {}
        with open(path) as db:
            for row in csv.reader(db):
                employee = Employee(row[0], self._parse_date(row[1]))
                employees[employee.name] = employee
        return employees

    def refresh(self):
        self.__init__(self._db_file)

    def get_employee(self, name):
        try:
            return self._employees[name]
        except KeyError:
            raise VacalcError("Employee '%s' not found." % name)

    def get_all_employees(self):
        return self._employees.values()

    def add_employee(self, name, startdate):
        if name in self._employees:
            raise VacalcError("Employee '%s' already exists in the system."
                              % name)
        employee = Employee(name, self._parse_date(startdate))
        self._employees[employee.name] = employee
        self._serialize(employee)
        return employee

    def _serialize(self, employee):
        if not self._db_file:
            return
        with open(self._db_file, 'a') as db:
            writer = csv.writer(db, lineterminator='\n')
            writer.writerow([employee.name, employee.startdate])

    def _parse_date(self, datestring):
        try:
            year, month, day = (int(item) for item in datestring.split('-'))
        except ValueError:
            raise VacalcError("Invalid time string '%s'." % datestring)
        try:
            return datetime.date(year, month, day)
        except ValueError, err:
            raise VacalcError(err.args[0].capitalize() + '.')


class Employee(object):

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = startdate
