import unittest

from robot.utils.asserts import assert_equals, assert_true
from robot.model.statistics import Statistics
from robot.result import TestSuite, TestCase


def verify_stat(stat, name, passed, failed, critical=None, non_crit=None, id=None):
    assert_equals(stat.name, name, 'stat.name')
    assert_equals(stat.passed, passed)
    assert_equals(stat.failed, failed)
    if critical is not None:
        assert_equals(stat.critical, critical)
    if non_crit is not None:
        assert_equals(stat.non_critical, non_crit)
    if id:
        assert_equals(stat.id, id)

def verify_suite(suite, name, id, passed, failed):
    verify_stat(suite.stat, name, passed, failed, id=id)

def generate_suite():
    suite = TestSuite(name='Root Suite')
    suite.set_criticality(critical_tags=['smoke'])
    s1 = suite.suites.create(name='First Sub Suite')
    s2 = suite.suites.create(name='Second Sub Suite')
    s11 = s1.suites.create(name='Sub Suite 1_1')
    s12 = s1.suites.create(name='Sub Suite 1_2')
    s13 = s1.suites.create(name='Sub Suite 1_3')
    s21 = s2.suites.create(name='Sub Suite 2_1')
    s11.tests = [TestCase(status='PASS'), TestCase(status='FAIL', tags=['t1'])]
    s12.tests = [TestCase(status='PASS', tags=['t_1','t2',]),
                 TestCase(status='PASS', tags=['t1','smoke']),
                 TestCase(status='FAIL', tags=['t1','t2','t3','smoke'])]
    s13.tests = [TestCase(status='PASS', tags=['t1','t 2','smoke'])]
    s21.tests = [TestCase(status='FAIL', tags=['t3','Smoke'])]
    return suite


class TestStatisticsSimple(unittest.TestCase):

    def setUp(self):
        suite = TestSuite(name='Hello')
        suite.tests = [TestCase(status='PASS'), TestCase(status='PASS'),
                       TestCase(status='FAIL')]
        self.statistics = Statistics(suite)

    def test_total(self):
        verify_stat(self.statistics.total.critical, 'Critical Tests', 2, 1)
        verify_stat(self.statistics.total.all, 'All Tests', 2, 1)

    def test_suite(self):
        verify_suite(self.statistics.suite, 'Hello', 's1', 2, 1)

    def test_tags(self):
        assert_equals(list(self.statistics.tags), [])


class TestStatisticsNotSoSimple(unittest.TestCase):

    def setUp(self):
        suite = generate_suite()
        suite.set_criticality(critical_tags=['smoke'])
        self.statistics = Statistics(suite, 2, ['t*','smoke'], ['t3'],
                                     [('t? & smoke', ''), ('none NOT t1', 'a title')])

    def test_total(self):
        verify_stat(self.statistics.total.all, 'All Tests', 4, 3)
        verify_stat(self.statistics.total.critical, 'Critical Tests', 2, 2)

    def test_suite(self):
        suite = self.statistics.suite
        verify_suite(suite, 'Root Suite', 's1', 4, 3)
        [s1, s2] = suite.suites
        verify_suite(s1, 'Root Suite.First Sub Suite', 's1-s1', 4, 2)
        verify_suite(s2, 'Root Suite.Second Sub Suite', 's1-s2', 0, 1)
        assert_equals(len(s1.suites), 0)
        assert_equals(len(s2.suites), 0)

    def test_tags(self):
        # Tag stats are tested more thoroughly in their own suite.
        tags = self.statistics.tags
        verify_stat(tags.tags['smoke'], 'smoke', 2, 2, True, False)
        verify_stat(tags.tags['t1'], 't1', 3, 2, False, False)
        verify_stat(tags.tags['t2'], 't2', 2, 1, False, False)
        expected = [('smoke', 4), ('a title', 0), ('t? & smoke', 4), ('t1', 5), ('t2', 3)]
        assert_equals([(t.name, t.total) for t in tags], expected)


class TestSuiteStatistics(unittest.TestCase):

    def test_all_levels(self):
        suite = Statistics(generate_suite()).suite
        verify_suite(suite, 'Root Suite', 's1', 4, 3)
        [s1, s2] = suite.suites
        verify_suite(s1, 'Root Suite.First Sub Suite', 's1-s1', 4, 2)
        verify_suite(s2, 'Root Suite.Second Sub Suite', 's1-s2', 0, 1)
        [s11, s12, s13] = s1.suites
        verify_suite(s11, 'Root Suite.First Sub Suite.Sub Suite 1_1', 's1-s1-s1', 1, 1)
        verify_suite(s12, 'Root Suite.First Sub Suite.Sub Suite 1_2', 's1-s1-s2', 2, 1)
        verify_suite(s13, 'Root Suite.First Sub Suite.Sub Suite 1_3', 's1-s1-s3', 1, 0)
        [s21] = s2.suites
        verify_suite(s21, 'Root Suite.Second Sub Suite.Sub Suite 2_1', 's1-s2-s1', 0, 1)

    def test_only_root_level(self):
        suite = Statistics(generate_suite(), suite_stat_level=1).suite
        verify_suite(suite, 'Root Suite', 's1', 4, 3)
        assert_equals(len(suite.suites), 0)

    def test_deeper_level(self):
        PASS = TestCase(status='PASS')
        FAIL = TestCase(status='FAIL')
        suite = TestSuite(name='1')
        suite.suites = [TestSuite(name='1'), TestSuite(name='2'), TestSuite(name='3')]
        suite.suites[0].suites = [TestSuite(name='1')]
        suite.suites[1].suites = [TestSuite(name='1'), TestSuite(name='2')]
        suite.suites[2].tests = [PASS, FAIL]
        suite.suites[0].suites[0].suites = [TestSuite(name='1')]
        suite.suites[1].suites[0].tests = [PASS, PASS, PASS, FAIL]
        suite.suites[1].suites[1].tests = [PASS, PASS, FAIL, FAIL]
        suite.suites[0].suites[0].suites[0].tests = [FAIL, FAIL, FAIL]
        s1 = Statistics(suite, suite_stat_level=3).suite
        verify_suite(s1, '1', 's1', 6, 7)
        [s11, s12, s13] = s1.suites
        verify_suite(s11, '1.1', 's1-s1', 0, 3)
        verify_suite(s12, '1.2', 's1-s2', 5, 3)
        verify_suite(s13, '1.3', 's1-s3', 1, 1)
        [s111] = s11.suites
        verify_suite(s111, '1.1.1', 's1-s1-s1', 0, 3)
        [s121, s122] = s12.suites
        verify_suite(s121, '1.2.1', 's1-s2-s1', 3, 1)
        verify_suite(s122, '1.2.2', 's1-s2-s2', 2, 2)
        assert_equals(len(s111.suites), 0)

    def test_iter_only_one_level(self):
        [stat] = list(Statistics(generate_suite(), suite_stat_level=1).suite)
        verify_stat(stat, 'Root Suite', 4, 3, id='s1')

    def test_iter_also_sub_suites(self):
        stats = list(Statistics(generate_suite()).suite)
        verify_stat(stats[0], 'Root Suite', 4, 3, id='s1')
        verify_stat(stats[1], 'Root Suite.First Sub Suite', 4, 2, id='s1-s1')
        verify_stat(stats[2], 'Root Suite.First Sub Suite.Sub Suite 1_1', 1, 1, id='s1-s1-s1')
        verify_stat(stats[3], 'Root Suite.First Sub Suite.Sub Suite 1_2', 2, 1, id='s1-s1-s2')
        verify_stat(stats[4], 'Root Suite.First Sub Suite.Sub Suite 1_3', 1, 0, id='s1-s1-s3')
        verify_stat(stats[5], 'Root Suite.Second Sub Suite', 0, 1, id='s1-s2')
        verify_stat(stats[6], 'Root Suite.Second Sub Suite.Sub Suite 2_1', 0, 1, id='s1-s2-s1')


if __name__ == "__main__":
    unittest.main()
