import os
import tempfile
from java.util import Timer, TimerTask
from java.lang import Runnable
from javax.swing import SwingUtilities

from org.robotframework.vacalc import VacationCalculator

from vacalc.ui import VacalcFrame
from vacalc.employeestore import EmployeeStore, VacalcError


class VacalcApplication(VacationCalculator):

    def create(self):
        default_db = os.path.join(tempfile.gettempdir(), 'vacalcdb.csv')
        self._db_file= os.environ.get('VACALC_DB', default_db)
        self._size = os.stat(self._db_file).st_size if os.path.exists(self._db_file) else 0
        self._store = EmployeeStore(self._db_file)
        self._frame = VacalcFrame(EmployeeController(self._store))
        self._timer = Timer()
        self._timer.scheduleAtFixedRate(DbModificationTask(self), 0, 100)
        self._frame.show()

    def check_modified_time(self):
        if not os.path.exists(self._db_file) or os.stat(self._db_file).st_size != self._size:
            self._store.refresh()
            SwingUtilities.invokeLater(UpdateAction(self._frame.employees_changed))


class UpdateAction(Runnable):
    def __init__(self, action):
        self._action = action
    def run(self):
        self._action()


class DbModificationTask(TimerTask):
    def __init__(self, app):
        self._app = app
    def run(self):
        self._app.check_modified_time()


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

