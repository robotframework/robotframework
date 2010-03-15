import datetime
import unittest

from vacalc import Employee, EmployeeStore, VacalcError


class TestEmployee(unittest.TestCase):

    def test_creating_employee(self):
        employee = Employee('Juan von Rantanen', '2010-3-15')
        self.assertEquals(employee.name, 'Juan von Rantanen')
        self.assertEquals(employee.startdate, datetime.date(2010, 3, 15))


class TestEmployeeStore(unittest.TestCase):

    def test_adding_employee(self):
        store = EmployeeStore(None)
        employee = store.add_employee('Test Employee Store', '2000-12-24')
        self.assertEquals(employee.name, 'Test Employee Store')
        self.assertEquals(employee.startdate, datetime.date(2000, 12, 24))
        self.assertEquals(store._employees, {employee.name: employee})

    def test_adding_duplicate_employee(self):
        store = EmployeeStore(None)
        employee = store.add_employee('test', '2000-12-24')
        self.assertRaises(VacalcError, store.add_employee, 'test', '2001-01-24')


if __name__ == '__main__':
    unittest.main()
