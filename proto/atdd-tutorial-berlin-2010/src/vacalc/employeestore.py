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
            raise VacalcError('Invalid time string.')
        try:
            return datetime.date(year, month, day)
        except ValueError, err:
            raise VacalcError(err.args[0].capitalize() + '.')


class Employee(object):
    max_vacation = int(12 * 2.5)
    no_vacation = 0
    vacation_per_month = 2
    credit_start_month = 4
    work_days_required= 14

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = startdate

    def count_vacation(self, year):
        return '%s days ' % self._count_vacation(self.startdate, year)

    def _count_vacation(self, startdate, year):
        if self._has_worked_longer_than_year(startdate, year):
            return self.max_vacation
        if self._started_after_holiday_credit_year_ended(startdate, year):
            return self.no_vacation
        return self._count_working_months(startdate) * self.vacation_per_month

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
