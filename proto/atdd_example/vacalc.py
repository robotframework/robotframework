from __future__ import with_statement
import os
import sys
import csv
import datetime


class VacalcError(Exception): pass


class EmployeeStore(object):

    def __init__(self, db_file='db.csv'):
        self._db_file = db_file
        if db_file and os.path.isfile(db_file):
            self._employees = self._read_employees(db_file)
        else:
            self._employees = {}

    def _read_employees(self, path):
        employees = {}
        with open(path) as db:
            for row in csv.reader(db):
                employee = Employee(row[0], row[1])
                employees[employee.name] = employee
        return employees

    def get_employee(self, name):
        for row in csv.reader(open(self._db_file)):
            if row[0] == name:
                return Employee(row[0], row[1])

    def add_employee(self, name, startdate):
        if name in self._employees:
            raise VacalcError("Employee '%s' already exists in the system" % name)
        employee = Employee(name, startdate)
        self._employees[employee.name] = employee
        self._serialize(employee)
        return employee

    def _serialize(self, employee):
        if not self._db_file:
            return
        with open(self._db_file, 'a') as db:
            writer = csv.writer(db, lineterminator='\n')
            writer.writerow([employee.name, employee.startdate.isoformat()])


class VacationCalculator(object):

    def __init__(self, employeestore):
        self._employeestore = employeestore

    def vacation(self, name, year):
        employee = self._employeestore.get_employee(name, year)
        return employee.count_vacation(year)

    def add_employee(self, name, startdate):
        employee = self._employeestore.add_employee(name, startdate)
        return "Successfully added employee '%s'." % employee.name

    def get_employee(self, name):
        employee = self._employeestore.get_employee(name)
        return '%s: start date %s' % (employee.name, employee.startdate.isoformat())


class Employee(object):

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = self._parse_date(startdate)

    def _parse_date(self, datestring):
        year, month, day = datestring.split('-')
        return datetime.date(int(year), int(month), int(day))

    def count_vacation(self, year):
        fail


def main(args):
    try:
        return getattr(VacationCalculator(EmployeeStore()), args[0])(*args[1:])
    except (AttributeError, TypeError):
        raise VacalcError('invalid command or arguments')


if __name__ == '__main__':
    try:
        print main(sys.argv[1:])
        sys.exit(0)
    except VacalcError, err:
        print err
        sys.exit(1)
