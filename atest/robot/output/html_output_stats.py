from robot.api import logger


class WrongStat(AssertionError):
    ROBOT_CONTINUE_ON_FAILURE = True


def get_total_stats(path):
    return get_all_stats(path)[0]

def get_tag_stats(path):
    return get_all_stats(path)[1]

def get_suite_stats(path):
    return get_all_stats(path)[2]

def get_all_stats(path):
    logger.info('Getting stats from <a href="file://%s">%s</a>' % (path, path),
                html=True)
    stats_line = _get_stats_line(path)
    logger.debug('Stats line: %s' % stats_line)
    total, tags, suite = eval(stats_line)
    return total, tags, suite

def _get_stats_line(path):
    prefix = 'window.output["stats"] = '
    with open(path) as file:
        for line in file:
            if line.startswith(prefix):
                return line[len(prefix):-2]

def verify_stat(stat, *attrs):
    stat.pop('elapsed')
    expected = dict(_get_expected_stat(attrs))
    if stat != expected:
        raise WrongStat('\n%-9s: %s\n%-9s: %s' % ('Got', stat, 'Expected', expected))

def _get_expected_stat(attrs):
    for key, value in (a.split(':', 1) for a in attrs):
        value = int(value) if value.isdigit() else str(value)
        yield str(key), value
