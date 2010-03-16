from __future__ import with_statement
import os
import sys
import csv
import datetime
import tempfile


class VacalcError(Exception): pass


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

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = self._parse_date(startdate)

    def _parse_date(self, datestring):
        year, month, day = datestring.split('-')
        return datetime.date(int(year), int(month), int(day))


class Vacation(object):
    max_vacation = 12 * 2.5
    no_vacation = 0
    vacation_per_month = 2
    credit_start_month = 4
    work_days_required= 14

    def __init__(self, empstartdate, vacation_year):
        self.days = self._calculate_vacation(empstartdate, vacation_year)

    def _calculate_vacation(self, start, year):
        if self._has_worked_longer_than_year(start, year):
            return self.max_vacation
        if self._started_after_holiday_credit_year_ended(start, year):
            return self.no_vacation
        return self._count_working_months(start) * self.vacation_per_month

    def _has_worked_longer_than_year(self, start, year):
        return year-start.year > 1 or \
                (year-start.year == 1 and start.month < self.credit_start_month)

    def _started_after_holiday_credit_year_ended(self, start, year):
        return start.year-year > 0 or \
                (year == start.year and start.month >= self.credit_start_month)

    def _count_working_months(self, start):
        months = self.credit_start_month - start.month
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
        return days < self.work_days_required

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

    def show_vacation(self, name, year):
        employee = self._employeestore.get_employee(name)
        vacation = Vacation(employee.startdate, int(year))
        return "%s has %d vacation days in year %s" \
                % (name, vacation.days, year)

    def add_employee(self, name, startdate):
        employee = Employee(name, startdate)
        self._employeestore.add_employee(employee)
        return "Successfully added employee '%s'." % employee.name

    def get_employee(self, name):
        employee = self._employeestore.get_employee(name)
        return '%s: start date %s' % (employee.name, employee.startdate)


def main(args):
    db_file = os.environ.get('VACALC_DB', os.path.join(tempfile.gettempdir(),
                                                        'vacalcdb.csv'))
    try:
        cmd = getattr(VacationCalculator(EmployeeStore(db_file)), args[0])
        return cmd(*args[1:])
    except (AttributeError, TypeError):
        raise VacalcError('invalid command or arguments')


if __name__ == '__main__':
    try:
        print main(sys.argv[1:])
        sys.exit(0)
    except VacalcError, err:
        print err
        sys.exit(1)
