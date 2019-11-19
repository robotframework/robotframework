import json

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
    stats = _get_output_line(path, 'window.output["stats"]')
    total, tags, suite = json.loads(stats)
    return total, tags, suite


def _get_output_line(path, prefix):
    logger.info("Getting '%s' from '<a href=\"file://%s\">%s</a>'."
                % (prefix, path, path), html=True)
    prefix += ' = '
    with open(path, encoding='UTF-8') as file:
        for line in file:
            if line.startswith(prefix):
                logger.info('Found: %s' % line)
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


def get_expand_keywords(path):
    expand = _get_output_line(path, 'window.output["expand_keywords"]')
    return json.loads(expand)
