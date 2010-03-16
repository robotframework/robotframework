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
    startdate = property(lambda self: self._startdate.isoformat())

    def __init__(self, name, startdate):
        self.name = name
        self._startdate = self._parse_date(startdate)

    def _parse_date(self, datestring):
        year, month, day = datestring.split('-')
        return datetime.date(int(year), int(month), int(day))


class Vacation(object):
    _infininty = 13

    def __init__(self, emp_startdate, vacation_year):
        self.days = self._calculate_vacation(emp_startdate, vacation_year)

    def _calculate_vacation(self, start, year):
        months = self._calc_months(start, year)
        if months == self._infininty:
            return 30
        return months * 2

    def _calc_months(self, start, year):
        if self._has_worked_longer_than_year(start, year):
            return self._infininty
        if self._started_after_holiday_credit_year_ended(start, year):
            return 0
        return self._count_working_months(start)

    def _has_worked_longer_than_year(self, start, year):
        return year-start.year > 1 or (year-start.year == 1 and start.month <= 3)

    def _started_after_holiday_credit_year_ended(self, start, year):
        return year == start.year and start.month > 3

    def _count_working_months(self, start):
        months = 4 - start.month
        if months <= 0:
            months += 12
        if self._first_month_has_too_few_working_days(start):
            months -= 1
        return months

    def _first_month_has_too_few_working_days(self, start):
        days = 0
        date = start
        while date:
            if self._is_working_day(date):
                days += 1
            date = self._next_date(date)
        return days < 14

    def _is_working_day(self, date):
        return date.weekday() < 5

    def _next_date(self, date):
        try:
            return date.replace(day=date.day+1)
        except ValueError:
            return None


class VacationCalculator(object):

    def __init__(self, employeestore):
        self._employeestore = employeestore

    def vacation(self, name, year):
        employee = self._employeestore.get_employee(name, year)
        return employee.count_vacation(year)

    def add_employee(self, name, startdate):
        employee = Employee(name, startdate)
        self._employeestore.add_employee(employee)
        return "Successfully added employee '%s'." % employee.name

    def get_employee(self, name):
        employee = self._employeestore.get_employee(name)
        return '%s: start date %s' % (employee.name, employee.startdate)


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
