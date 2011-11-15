import unittest

from robot.model import Criticality
from robot.utils.asserts import assert_equals, assert_none, fail
from robot.model.statistics import Statistics
from robot.model.tagstatistics import TagStatistics, TagStatLink, TagStatInfo
from robot.result import TestSuite, TestCase
from robot import utils


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

def verify_suite(suite, name, id, crit_pass, crit_fail, all_pass=None, all_fail=None):
    verify_stat(suite.critical, name, crit_pass, crit_fail, id=id)
    if all_pass is None:
        all_pass, all_fail = crit_pass, crit_fail
    verify_stat(suite.all, name, all_pass, all_fail, id=id)

def generate_default_suite():
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
        self.statistics = Statistics(generate_default_suite())

    def test_total(self):
        verify_stat(self.statistics.total.all, 'All Tests', 4, 3)
        verify_stat(self.statistics.total.critical, 'Critical Tests', 2, 2)

    def test_suite(self):
        suite = self.statistics.suite
        verify_suite(suite, 'Root Suite', 's1', 2, 2, 4, 3)
        assert_equals(len(suite.suites), 2)
        s1, s2 = suite.suites
        verify_suite(s1, 'Root Suite.First Sub Suite', 's1-s1', 2, 1, 4, 2)
        verify_suite(s2, 'Root Suite.Second Sub Suite', 's1-s2', 0, 1, 0, 1)
        assert_equals(len(s1.suites), 3)
        s11, s12, s13 = s1.suites
        verify_suite(s11, 'Root Suite.First Sub Suite.Sub Suite 1_1', 's1-s1-s1', 0, 0, 1, 1)
        verify_suite(s12, 'Root Suite.First Sub Suite.Sub Suite 1_2', 's1-s1-s2', 1, 1, 2, 1)
        verify_suite(s13, 'Root Suite.First Sub Suite.Sub Suite 1_3', 's1-s1-s3', 1, 0, 1, 0)
        assert_equals(len(s2.suites), 1)
        s21 = s2.suites[0]
        verify_suite(s21, 'Root Suite.Second Sub Suite.Sub Suite 2_1', 's1-s2-s1', 0, 1, 0, 1)

    def test_tags(self):
        tags = self.statistics.tags
        assert_equals(len(tags), 4)
        names = [t.name for t in tags]
        assert_equals(names, 'smoke t1 t2 t3'.split())
        verify_stat(tags.tags['smoke'], 'smoke', 2, 2, True, False)
        verify_stat(tags.tags['t1'], 't1', 3, 2, False, False)
        verify_stat(tags.tags['t2'], 't2', 2, 1, False, False)
        verify_stat(tags.tags['t3'], 't3', 0, 2, False, False)


class TestSuiteStatLevel(unittest.TestCase):

    def test_stat_level(self):
        suite = Statistics(generate_default_suite(), suite_stat_level=2).suite
        verify_suite(suite, 'Root Suite', 's1', 2, 2, 4, 3)
        assert_equals(len(suite.suites), 2)
        s1, s2 = suite.suites
        verify_suite(s1, 'Root Suite.First Sub Suite', 's1-s1', 2, 1, 4, 2)
        verify_suite(s2, 'Root Suite.Second Sub Suite', 's1-s2', 0, 1, 0, 1)
        assert_equals(len(s1.suites), 0)
        assert_equals(len(s2.suites), 0)


class TestTagStatistics(unittest.TestCase):
    _incl_excl_data = [([], []),
                       ([], ['t1','t2']),
                       (['t1'], ['t1','t2']),
                       (['t1','t2'], ['t1','t2','t3','t4']),
                       (['UP'], ['t1','t2','up']),
                       (['not','not2'], ['t1','t2','t3']),
                       (['t*'], ['t1','s1','t2','t3','s2','s3']),
                       (['T*','r'], ['t1','t2','r','teeeeeeee']),
                       (['*'], ['t1','t2','s1','tag']),
                       (['t1','t2','t3','not'], ['t1','t2','t3','t4','s1','s2'])]

    def test_include(self):
        for incl, tags in self._incl_excl_data:
            stats = TagStatistics(Criticality(), incl, [])
            stats.add_test(TestCase(status='PASS', tags=tags))
            expected = [tag for tag in tags
                        if incl == [] or any(utils.matches(tag, i) for i in incl)]
            assert_equals([s.name for s in stats], sorted(expected))

    def test_exclude(self):
        for excl, tags in self._incl_excl_data:
            stats = TagStatistics(Criticality(), [], excl)
            stats.add_test(TestCase(status='PASS', tags=tags))
            expected = [tag for tag in tags
                        if not any(utils.matches(tag, e) for e in excl)]
            assert_equals([s.name for s in stats], sorted(expected))

    def test_include_and_exclude(self):
        for incl, excl, tags, exp in [
               ([], [], ['t0','t1','t2'], ['t0','t1','t2']),
               (['t1'], ['t2'], ['t0','t1','t2'], ['t1']),
               (['t?'], ['t2'], ['t0','t1','t2','x'], ['t0','t1']),
               (['t?'], ['*2'], ['t0','t1','t2','x2'], ['t0','t1']),
               (['t1','t2'], ['t2'], ['t0','t1','t2'], ['t1']),
               (['t1','t2','t3','not'], ['t2','t0'],
                ['t0','t1','t2','t3','x'], ['t1','t3'] )
              ]:
            stats = TagStatistics(Criticality(), incl, excl)
            stats.add_test(TestCase(status='PASS', tags=tags))
            assert_equals([s.name for s in stats], exp),

    def test_len(self):
        stats = TagStatistics(Criticality())
        assert_equals(len(stats), 0)
        stats.add_test(TestCase())
        assert_equals(len(stats), 0)
        stats.add_test(TestCase(tags=['a']))
        assert_equals(len(stats), 1)
        stats.add_test(TestCase(tags=['A', 'B']))
        assert_equals(len(stats), 2)

    def test_len_with_combine(self):
        stats = TagStatistics(Criticality(), combine=[('x*', 'title')])
        assert_equals(len(stats), 1)
        stats.add_test(TestCase(tags=['xxx', 'yyy']))
        assert_equals(len(stats), 3)

    def test_combine_with_name(self):
        for comb_tags, expected_name in [
                ([], '' ),
                ([('t1&t2', 'my name')], 'my name'),
                ([('t1NOTt3', 'Others')], 'Others'),
                ([('1:2&2:3', 'nAme')], 'nAme'),
                ([('3*', '')], '3*' ),
                ([('4NOT5', 'Some new name')], 'Some new name')
               ]:
            stats = TagStatistics(Criticality(), combine=comb_tags)
            assert_equals(bool(stats), expected_name != '')
            if expected_name:
                assert_equals([s.name for s in stats], [expected_name])

    def test_is_combined_with_and_statements(self):
        for comb_tags, test_tags, expected_count in [
                ('t1', ['t1'], 1),
                ('t1', ['t2'], 0),
                ('t1&t2', ['t1'], 0),
                ('t1&t2', ['t1','t2'], 1),
                ('t1&t2', ['T1','t 2','t3'], 1),
                ('t*', ['s','t','u'], 1),
                ('t*', ['s','tee','t'], 1),
                ('t*&s', ['s','tee','t'], 1),
                ('t*&s&non', ['s','tee','t'], 0)
               ]:
            self._verify_combined_statistics(comb_tags, test_tags, expected_count)

    def _verify_combined_statistics(self, comb_tags, test_tags, expected_count):
        stats = TagStatistics(Criticality(), combine=[(comb_tags, 'name')])
        stats._add_to_combined_statistics(TestCase(tags=test_tags))
        assert_equals([s.total for s in stats if s.combined], [expected_count])

    def test_is_combined_with_not_statements(self):
        for comb_tags, test_tags, expected_count in [
                ('t1NOTt2', [], 0),
                ('t1NOTt2', ['t1'], 1),
                ('t1NOTt2', ['t1','t2'], 0),
                ('t1NOTt2', ['t3'], 0),
                ('t1NOTt2', ['t3','t2'], 0),
                ('t*NOTt2', ['t1'], 1),
                ('t*NOTt2', ['t'], 1),
                ('t*NOTt2', ['TEE'], 1),
                ('t*NOTt2', ['T2'], 0),
                ('T*NOTT?', ['t'], 1),
                ('T*NOTT?', ['tt'], 0),
                ('T*NOTT?', ['ttt'], 1),
                ('T*NOTT?', ['tt','t'], 0),
                ('T*NOTT?', ['ttt','something'], 1),
                ('tNOTs*NOTr', ['t'], 1),
                ('tNOTs*NOTr', ['t','s'], 0),
                ('tNOTs*NOTr', ['S','T'], 0),
                ('tNOTs*NOTr', ['R','T','s'], 1),
               ]:
            self._verify_combined_statistics(comb_tags, test_tags, expected_count)

    def test_combine_with_same_name_as_existing_tag(self):
        stats = TagStatistics(Criticality(), combine=[('x*', 'name')])
        stats.add_test(TestCase(tags=['name', 'another']))
        assert_equals([(s.name, s.combined) for s in stats],
                      [('name', 'x*'), ('another', ''), ('name', '')])

    def test_combine(self):
        # This is more like an acceptance test than a unit test ...
        for comb_tags, tests_tags, crit_tags in [
                (['t1&t2'], [['t1','t2','t3'],['t1','t3']], []),
                (['1&2&3'], [['1','2','3'],['1','2','3','4']], ['1','2']),
                (['1&2','1&3'], [['1','2','3'],['1','3'],['1']], ['1']),
                (['t*'], [['t1','x','y'],['tee','z'],['t']], ['x']),
                (['t?&s'], [['t1','s'],['tt','s','u'],['tee','s'],['s']], []),
                (['t*&s','*'], [['s','t','u'],['tee','s'],[],['x']], []),
                (['tNOTs'], [['t','u'],['t','s']], []),
                (['tNOTs','t&s','tNOTsNOTu', 't&sNOTu'],
                  [['t','u'],['t','s'],['s','t','u'],['t'],['t','v']], ['t']),
                (['nonex'], [['t1'],['t1,t2'],[]], [])
               ]:
            # 1) Create tag stats
            tagstats = TagStatistics(Criticality(crit_tags),
                                     combine=[(t, '') for t in comb_tags])
            all_tags = []
            for tags in tests_tags:
                tagstats.add_test(TestCase(status='PASS', tags=tags),)
                all_tags.extend(tags)
            # 2) Actual values
            names = [stat.name for stat in tagstats]
            # 3) Expected values
            exp_crit = []; exp_noncr = []
            for tag in utils.normalize_tags(all_tags):
                if tag in crit_tags:
                    exp_crit.append(tag)
                else:
                    exp_noncr.append(tag)
            exp_names = exp_crit + sorted(comb_tags) + exp_noncr
            # 4) Verify names (match counts were already verified)
            assert_equals(names, exp_names)

    def test_sorting(self):
        stats = TagStatistics(Criticality(['c2', 'c1'], ['n*']),
                              combine=[('c*', ''), ('xxx', 'a title')])
        stats.add_test(TestCase(tags=['c1', 'c2', 't1']))
        stats.add_test(TestCase(tags=['c1', 'n2', 't2']))
        stats.add_test(TestCase(tags=['n1', 'n2', 't1', 't3']))
        assert_equals([(s.name, s.info, s.total) for s in stats],
                       [('c1', 'critical', 2), ('c2', 'critical', 1),
                        ('n1', 'non-critical', 1), ('n2', 'non-critical', 2),
                        ('a title', 'combined', 0), ('c*', 'combined', 2),
                        ('t1', '', 2), ('t2', '', 1), ('t3', '', 1)])

    def test_through_suite(self):
        suite = generate_default_suite()
        suite.set_criticality(critical_tags=['smoke'])
        statistics = Statistics(suite, 1, ['t*','smoke'], ['t3'],
                                [('t1 & t2', ''), ('t? & smoke', ''),
                                 ('t1 NOT t2', ''), ('none & t1', 'a title')])
        expected = [('smoke', 4), ('a title', 0), ('t1 & t2', 3),
                    ('t1 NOT t2', 2), ('t? & smoke', 4), ('t1', 5), ('t2', 3)]
        assert_equals([(t.name, t.total) for t in statistics.tags], expected)


class TestTagStatLink(unittest.TestCase):

    def test_valid_string_is_parsed_correctly(self):
        for arg, exp in [(('Tag', 'bar/foo.html', 'foobar'),
                          ('^Tag$', 'bar/foo.html', 'foobar')),
                         (('hello', 'gopher://hello.world:8090/hello.html',
                           'Hello World'),
                          ('^hello$', 'gopher://hello.world:8090/hello.html',
                           'Hello World'))]:
            link = TagStatLink(*arg)
            assert_equals(exp[0], link._regexp.pattern)
            assert_equals(exp[1], link._link)
            assert_equals(exp[2], link._title)

    def test_valid_string_containing_patterns_is_parsed_correctly(self):
        for arg, exp_pattern in [('*', '^(.*)$'), ('f*r', '^f(.*)r$'),
                                 ('*a*', '^(.*)a(.*)$'),  ('?', '^(.)$'),
                                 ('??', '^(..)$'), ('f???ar', '^f(...)ar$'),
                                 ('F*B?R*?', '^F(.*)B(.)R(.*)(.)$')]:
            link = TagStatLink(arg, 'some_url', 'some_title')
            assert_equals(exp_pattern, link._regexp.pattern)

    def test_underscores_in_title_are_converted_to_spaces(self):
        link = TagStatLink('', '', 'my_name')
        assert_equals(link._title, 'my name')

    def test_get_link_returns_correct_link_when_matches(self):
        for arg, exp in [(('smoke', 'http://tobacco.com', 'Lung_cancer'),
                          ('http://tobacco.com', 'Lung cancer')),
                         (('tag', 'ftp://foo:809/bar.zap', 'Foo_in a Bar'),
                          ('ftp://foo:809/bar.zap', 'Foo in a Bar'))]:
            link = TagStatLink(*arg)
            assert_equals(exp, link.get_link(arg[0]))

    def test_get_link_returns_none_when_no_match(self):
        link = TagStatLink('smoke', 'http://tobacco.com', 'Lung cancer')
        for tag in ['foo', 'b a r', 's moke']:
            assert_none(link.get_link(tag))

    def test_pattern_matches_case_insensitively(self):
        exp = 'http://tobacco.com', 'Lung cancer'
        link = TagStatLink('smoke', *exp)
        for tag in ['Smoke', 'SMOKE', 'smoke']:
            assert_equals(exp, link.get_link(tag))

    def test_pattern_matches_when_spaces(self):
        exp = 'http://tobacco.com', 'Lung cancer'
        link = TagStatLink('smoking kills', *exp)
        for tag in ['Smoking Kills', 'SMOKING KILLS']:
            assert_equals(exp, link.get_link(tag))

    def test_pattern_match(self):
        link = TagStatLink('f?o*r', 'http://foo/bar.html', 'FooBar')
        for tag in ['foobar', 'foor', 'f_ofoobarfoobar', 'fOoBAr']:
            assert_equals(link.get_link(tag), ('http://foo/bar.html', 'FooBar'))

    def test_pattern_substitution_with_one_match(self):
        link = TagStatLink('tag-*', 'http://tracker/?id=%1', 'Tracker')
        for id in ['1', '23', '456']:
            exp = ('http://tracker/?id=%s' % id, 'Tracker')
            assert_equals(exp, link.get_link('tag-%s' % id))

    def test_pattern_substitution_with_multiple_matches(self):
        link = TagStatLink('?-*', 'http://tracker/?id=%1-%2', 'Tracker')
        for id1, id2 in [('1', '2'), ('3', '45'), ('f', 'bar')]:
            exp = ('http://tracker/?id=%s-%s' % (id1, id2), 'Tracker')
            assert_equals(exp, link.get_link('%s-%s' % (id1, id2)))

    def test_pattern_substitution_with_multiple_substitutions(self):
        link = TagStatLink('??-?-*', '%3-%3-%1-%2-%3', 'Tracker')
        assert_equals(link.get_link('aa-b-XXX'), ('XXX-XXX-aa-b-XXX', 'Tracker'))

    def test_matches_are_ignored_in_pattern_substitution(self):
        link = TagStatLink('???-*-*-?', '%4-%2-%2-%4', 'Tracker')
        assert_equals(link.get_link('AAA-XXX-ABC-B'), ('B-XXX-XXX-B', 'Tracker'))


if __name__ == "__main__":
    unittest.main()
