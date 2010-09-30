import unittest
import datetime

from vacalc.employeestore import EmployeeStore, VacalcError


class TestEmployeeStore(unittest.TestCase):

    def test_adding_employee(self):
        store = EmployeeStore(None)
        employee = store.add_employee('Test Employee Store', '2000-12-24')
        self._assert_employee(employee, 'Test Employee Store',
                              datetime.date(2000, 12, 24))
        self.assertEquals(store.get_all_employees(), [employee])

    def test_adding_duplicate_employee(self):
        store = EmployeeStore(None)
        store.add_employee('test', '2000-12-24')
        self.assertRaises(VacalcError, store.add_employee,
                          'test', '2001-01-24')

    def test_getting_employee(self):
        store = EmployeeStore(None)
        employee = store.add_employee('Mr Foo Bar', '1990-02-03')
        self.assertEquals(store.get_employee('Mr Foo Bar'), employee)

    def test_get_missing_employee(self):
        store = EmployeeStore(None)
        self.assertRaises(VacalcError, store.get_employee, 'I am not here')

    def _assert_employee(self, employee, name, date):
        self.assertEquals(employee.name, name)
        self.assertEquals(employee.startdate, date)


if __name__ == '__main__':
    unittest.main()
