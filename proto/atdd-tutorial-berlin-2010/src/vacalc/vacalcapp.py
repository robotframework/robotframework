import os
import tempfile

from org.robotframework.vacalc import VacationCalculator

from vacalc.ui import VacalcFrame
from vacalc.employeestore import EmployeeStore, Employee, VacalcError


class VacalcApplication(VacationCalculator):

    def create(self):
        db_file = os.environ.get('VACALC_DB', os.path.join(tempfile.gettempdir(),
                                                           'vacalcdb.csv'))
        store = EmployeeStore(db_file)
        self._frame = VacalcFrame(EmployeeController(store))
        self._frame.show()


class EmployeeController(object):

    def __init__(self, employeestore):
        self._store = employeestore
        self._change_listeners = []

    def all(self):
        return self._store.get_all_employees()

    def add(self, name, startdate):
        try:
            employee = self._store.add_employee(name, startdate)
        except VacalcError, err:
            for l in self._change_listeners:
                l.adding_employee_failed(unicode(err))
        else:
            for l in self._change_listeners:
                l.employee_added(employee)

    def add_change_listener(self, listener):
        self._change_listeners.append(listener)


class VacationCalculator(object):
    max_vacation = int(12 * 2.5)
    no_vacation = 0
    vacation_per_month = 2
    credit_start_month = 4
    work_days_required= 14

    def __init__(self, employeestore):
        self._employeestore = employeestore

    def show_vacation(self, name, year):
        employee = self._employeestore.get_employee(name)
        vacation = self._count_vacation(employee.startdate, int(year))
        return '%s days' % vacation

    def add_employee(self, name, startdate):
        employee = Employee(name, startdate)
        self._employeestore.add_employee(employee)
        return "Employee '%s' was added successfully" % employee.name

    def get_employee(self, name):
        employee = self._employeestore.get_employee(name)
        return '%s: start date %s' % (employee.name, employee.startdate)

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

