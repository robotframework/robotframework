from robot.api import TestSuiteBuilder

# First build test suite using existing files.
suite = TestSuiteBuilder().build('my_tests.txt')
assert suite.name == 'My Tests'
assert len(suite.tests) == 2

# Then, let's modify the suite:
test_case = suite.tests.create('Dynamically created test 3', tags=suite.tests[0].tags)
test_case.keywords.create('Log', args=['Hello world!'])
suite.tests[1].tags.add(['tag 1', 'tag 2'])
assert len(suite.tests) == 3

# Run the result
result = suite.run(critical='my critical tag')
assert len(result.errors) == 0
stats = result.suite.statistics
assert stats.critical.total == 1
assert stats.all.total == 3
