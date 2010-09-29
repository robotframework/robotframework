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
                date = self._convert_date(row[1])
                employee = Employee(row[0], date)
                employees[employee.name] = employee
        return employees

    def _convert_date(self, isodate):
        year, month, day = isodate.split('-')
        return '%s.%s.%s' % (day, month, year)

    def get_employee(self, name):
        try:
            return self._employees[name]
        except KeyError:
            raise VacalcError("Employee '%s' not found" % name)

    def get_all_employees(self):
        return self._employees.values()

    def add_employee(self, employee):
        if employee.name in self._employees:
            raise VacalcError("Employee '%s' already exists in the system" %
                              employee.name)
        self._employees[employee.name] = employee
        self._serialize(employee)

    def _serialize(self, employee):
        if not self._db_file:
            return
        with open(self._db_file, 'a') as db:
            writer = csv.writer(db, lineterminator='\n')
            writer.writerow([employee.name, employee.startdate])


class Employee(object):

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = self._parse_date(startdate)

    def _parse_date(self, datestring):
        day, month, year = datestring.split('.')
        return datetime.date(int(year), int(month), int(day))
