from robot.api import TestSuite

suite = TestSuite(name='Suite For Programmatic Tests')
suite.imports.library('OperatingSystem')
test_case = suite.tests.create(name='Should Initialize Environment', tags='regression')
test_case.keywords.create('Set Environment Variable', args=['SKYNET', 'true'], type='setup')
test_case.keywords.create('Environment Variable Should Be Set', args=['SKYNET'])
result = suite.run()
