import unittest

from robot.model import Criticality
from robot.utils.asserts import assert_equals, assert_none
from robot.model.tagstatistics import TagStatisticsBuilder, TagStatLink
from robot.model import Tags
from robot.result.testcase import TestCase
from robot.utils import MultiMatcher


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
            builder = TagStatisticsBuilder(Criticality(), incl, [])
            builder.add_test(TestCase(status='PASS', tags=tags))
            matcher = MultiMatcher(incl, match_if_no_patterns=True)
            expected = [tag for tag in tags if matcher.match(tag)]
            assert_equals([s.name for s in builder.stats], sorted(expected))

    def test_exclude(self):
        for excl, tags in self._incl_excl_data:
            builder = TagStatisticsBuilder(Criticality(), [], excl)
            builder.add_test(TestCase(status='PASS', tags=tags))
            matcher = MultiMatcher(excl)
            expected = [tag for tag in tags if not matcher.match(tag)]
            assert_equals([s.name for s in builder.stats], sorted(expected))

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
            builder = TagStatisticsBuilder(Criticality(), incl, excl)
            builder.add_test(TestCase(status='PASS', tags=tags))
            assert_equals([s.name for s in builder.stats], exp),

    def test_iter(self):
        builder = TagStatisticsBuilder(Criticality())
        assert_equals(list(builder.stats), [])
        builder.add_test(TestCase())
        assert_equals(list(builder.stats), [])
        builder.add_test(TestCase(tags=['a']))
        assert_equals(len(list(builder.stats)), 1)
        builder.add_test(TestCase(tags=['A', 'B']))
        assert_equals(len(list(builder.stats)), 2)

    def test_iter_with_combine(self):
        builder = TagStatisticsBuilder(Criticality(), combined=[('x*', 'title')])
        assert_equals(len(list(builder.stats)), 1)
        builder.add_test(TestCase(tags=['xxx', 'yyy']))
        assert_equals(len(list(builder.stats)), 3)

    def test_combine_with_name(self):
        for comb_tags, expected_name in [
                ([], '' ),
                ([('t1&t2', 'my name')], 'my name'),
                ([('t1NOTt3', 'Others')], 'Others'),
                ([('1:2&2:3', 'nAme')], 'nAme'),
                ([('3*', '')], '3*' ),
                ([('4NOT5', 'Some new name')], 'Some new name')
               ]:
            builder = TagStatisticsBuilder(Criticality(), combined=comb_tags)
            assert_equals(bool(list(builder.stats)), expected_name != '')
            if expected_name:
                assert_equals([s.name for s in builder.stats], [expected_name])

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
        builder = TagStatisticsBuilder(Criticality(), combined=[(comb_tags, 'name')])
        builder._add_to_combined_statistics(TestCase(tags=test_tags))
        assert_equals([s.total for s in builder.stats if s.combined], [expected_count])

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
                ('tNOTs*NOTr', ['R','T','s'], 0),
                ('*NOTt', ['t'], 0),
                ('*NOTt', ['e'], 1),
                ('*NOTt', [], 0),
               ]:
            self._verify_combined_statistics(comb_tags, test_tags, expected_count)

    def test_starting_with_not(self):
        for comb_tags, test_tags, expected_count in [
            ('NOTt', ['t'], 0),
            ('NOTt', ['e'], 1),
            ('NOTt', [], 1),
            ('NOTtORe', ['e'], 0),
            ('NOTtORe', ['e', 't'], 0),
            ('NOTtORe', ['h'], 1),
            ('NOTtORe', [], 1),
            ('NOTtANDe', [], 1),
            ('NOTtANDe', ['t'], 1),
            ('NOTtANDe', ['t', 'e'], 0),
            ('NOTtNOTe', ['t', 'e'], 0),
            ('NOTtNOTe', ['t'], 0),
            ('NOTtNOTe', ['e'], 0),
            ('NOTtNOTe', ['d'], 1),
            ('NOTtNOTe', [], 1),
            ('NOT*', ['t'], 0),
            ('NOT*', [], 1),
            ]:
            self._verify_combined_statistics(comb_tags, test_tags, expected_count)

    def test_combine_with_same_name_as_existing_tag(self):
        builder = TagStatisticsBuilder(Criticality(), combined=[('x*', 'name')])
        builder.add_test(TestCase(tags=['name', 'another']))
        assert_equals([(s.name, s.combined) for s in builder.stats],
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
            builder = TagStatisticsBuilder(Criticality(crit_tags),
                                           combined=[(t, '') for t in comb_tags])
            all_tags = []
            for tags in tests_tags:
                builder.add_test(TestCase(status='PASS', tags=tags),)
                all_tags.extend(tags)
            # 2) Actual values
            names = [stat.name for stat in builder.stats]
            # 3) Expected values
            exp_crit = []; exp_noncr = []
            for tag in Tags(all_tags):
                if tag in crit_tags:
                    exp_crit.append(tag)
                else:
                    exp_noncr.append(tag)
            exp_names = exp_crit + sorted(comb_tags) + exp_noncr
            # 4) Verify names (match counts were already verified)
            assert_equals(names, exp_names)

    def test_sorting(self):
        builder = TagStatisticsBuilder(Criticality(['c2', 'c1'], ['n*']),
                                       combined=[('c*', ''), ('xxx', 'a title')])
        builder.add_test(TestCase(tags=['c1', 'c2', 't1']))
        builder.add_test(TestCase(tags=['c1', 'n2', 't2']))
        builder.add_test(TestCase(tags=['n1', 'n2', 't1', 't3']))
        assert_equals([(s.name, s.info, s.total) for s in builder.stats],
                       [('c1', 'critical', 2), ('c2', 'critical', 1),
                        ('n1', 'non-critical', 1), ('n2', 'non-critical', 2),
                        ('a title', 'combined', 0), ('c*', 'combined', 2),
                        ('t1', '', 2), ('t2', '', 1), ('t3', '', 1)])


class TestTagStatDoc(unittest.TestCase):

    def test_simple(self):
        builder = TagStatisticsBuilder(docs=[('t1', 'doc')])
        builder.add_test(TestCase(tags=['t1', 't2']))
        builder.add_test(TestCase(tags=['T 1']))
        builder.add_test(TestCase(tags=['T_1'], status='PASS'))
        self._verify_stats(builder.stats.tags['t1'], 'doc', 2, 1)

    def test_pattern(self):
        builder = TagStatisticsBuilder(docs=[('t?', '*doc*')])
        builder.add_test(TestCase(tags=['t1', 'T2']))
        builder.add_test(TestCase(tags=['_t__1_', 'T 3']))
        self._verify_stats(builder.stats.tags['t1'], '*doc*', 2)
        self._verify_stats(builder.stats.tags['t2'], '*doc*', 1)
        self._verify_stats(builder.stats.tags['t3'], '*doc*', 1)

    def test_multiple_matches(self):
        builder = TagStatisticsBuilder(docs=[('t_1', 'd1'), ('t?', 'd2')])
        builder.add_test(TestCase(tags=['t1', 't_2']))
        self._verify_stats(builder.stats.tags['t1'], 'd1 & d2', 1)
        self._verify_stats(builder.stats.tags['t2'], 'd2', 1)

    def _verify_stats(self, stat, doc, failed, passed=0):
        assert_equals(stat.doc, doc)
        assert_equals(stat.failed, failed)
        assert_equals(stat.passed, passed)


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
