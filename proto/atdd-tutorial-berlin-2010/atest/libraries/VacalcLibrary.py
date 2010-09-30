import datetime

from vacalc.employeestore import Employee

def amount_of_vacation_should_be(startdate, vacation_year, exp_vacation_days):
    try:
        sdate = datetime.date(*(int(item) for item in startdate.split('-')))
    except Exception, err:
        raise AssertionError('Invalid time format %s' % err)
    actual_days = Employee('Test Employee', sdate).count_vacation(int(vacation_year))
    if  actual_days != int(exp_vacation_days):
        raise AssertionError('%s != %s' % (exp_vacation_days, actual_days))
