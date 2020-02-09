from robot.result.visitor import ResultVisitor
import json

from robot.output.jsonlogger import JsonLogger


class JsonOutputWriter(JsonLogger):

    def __init__(self, output, rpa=False):
        JsonLogger.__init__(self, output, rpa=rpa, generator='Rebot')

    def start_message(self, msg):
        self._write_message(msg)

    def end_result(self, result):
        self.close()


class JsonWriter(object):

    def __init__(self, execution_result):
        self._execution_result = execution_result

    def write(self, output):
        writer = JsonOutputWriter(output)
        self._execution_result.visit(writer)


class JsonFileWriter(ResultVisitor):

    def __init__(self):
        self._data = dict()
        self._root_suite = None

    def write(self, output):
        with open(output, 'w') as json_outfile:
            json.dump(self._data, json_outfile)

    def start_suite(self, suite):
        if self._root_suite:
            return
        else:
            self._root_suite = suite
            self._data["suite"] = self._json_suite_convert(suite)

    def start_statistics(self, stats):
        self._data["statistics"] = dict()
        self._data["statistics"]["suite"] = self._json_suite_stats_convert(stats.suite)
        self._data["statistics"]["total"] = self._json_total_stats_convert(stats.total)
        self._data["statistics"]["tag"] = self._json_tag_stats_convert(stats.tags)

    def start_errors(self, errors):
        self._data["errors"] = [self._json_message_convert(msg) for msg in errors.messages]

    def _json_stat_convert(self, stat):
        stat_object = {
            'name': stat.name,
            'passed': stat.passed,
            'failed': stat.failed
        }
        suite_id = getattr(stat, "id", None)
        if suite_id:
            stat_object['id'] = suite_id
        return stat_object

    def _json_tag_stat_convert(self, tag_stat):
        stat_object = {
            'name': tag_stat.name,
            'passed': tag_stat.passed,
            'failed': tag_stat.failed,
            'critical': tag_stat.critical,
            'tag': tag_stat.name
        }
        if tag_stat.info:
            stat_object["info"] = tag_stat.info
        if tag_stat.doc:
            stat_object["doc"] = tag_stat.doc
        return stat_object

    def _json_total_stats_convert(self, total_stats):
        return [self._json_stat_convert(statistic) for statistic in [total_stats.all, total_stats.critical]]

    def _json_suite_stats_convert(self, suite_stats):
        suites = suite_stats.suites + [suite_stats]
        return [self._json_stat_convert(statistic.stat) for statistic in suites]

    def _json_tag_stats_convert(self, tag_stats):
        return [self._json_tag_stat_convert(tag_stats.tags[tag]) for tag in tag_stats.tags]

    def _json_keyword_convert(self, keyword):
        base_object = {
            'name': keyword.name,
            'status': self._json_status_convert(keyword),
            'type': keyword.type
        }
        if keyword.keywords:
            base_object['kw'] = [self._json_keyword_convert(kw) for kw in keyword.keywords]
        if keyword.messages:
            base_object['messages'] = [self._json_message_convert(msg) for msg in keyword.messages]
        if keyword.doc:
            base_object['doc'] = keyword.doc
        if keyword.tags:
            base_object['tags'] = list(keyword.tags)
        if keyword.timeout:
            base_object['timeout'] = keyword.timeout
        if keyword.args:
            base_object['args'] = list(keyword.args)
        if keyword.assign:
            base_object['assign'] = list(keyword.assign)
        if keyword.libname:
            base_object['library'] = keyword.libname
        return base_object

    def _json_test_convert(self, test):
        base_object = {
            'name': test.name,
            'id': test.id,
            'status': self._json_status_convert(test)
        }
        if test.keywords:
            base_object['kw'] = [self._json_keyword_convert(keyword) for keyword in test.keywords]
        if test.message:
            base_object['message'] = test.message
        if test.doc:
            base_object['doc'] = test.doc
        if test.tags:
            base_object['tags'] = list(test.tags)
        if test.timeout:
            base_object['timeout'] = test.timeout.value
        return base_object

    def _json_metadata_convert(self, metadata):
        return {key: metadata[key] for key in metadata}

    def _json_status_convert(self, data):
        base_object = {
            'status': data.status,
            'starttime': data.starttime if data.starttime else "N/A",
            'endtime': data.endtime if data.endtime else "N/A",
            'elapsedtime': str(data.elapsedtime) if data.elapsedtime else "N/A",
        }
        critical = getattr(data, "critical", None)
        if critical is not None:
            base_object['critical'] = critical
        return base_object

    def _json_message_convert(self, message):
        base_object = {
            "message": message.message,
            "level": message.level,
            "html": message.html,
            "timestamp": message.timestamp
        }
        return base_object

    def _json_suite_convert(self, test_suite):
        base_object = {
            'id': test_suite.id,
            'name': test_suite.name,
            'status': self._json_status_convert(test_suite)
        }
        if test_suite.keywords:
            base_object['kw'] = [self._json_keyword_convert(keyword) for keyword in test_suite.keywords]
        if test_suite.suites:
            base_object['suites'] = [self._json_suite_convert(suite) for suite in test_suite.suites]
        if test_suite.tests:
            base_object['tests'] = [self._json_test_convert(test) for test in test_suite.tests]
        if test_suite.doc:
            base_object['doc'] = test_suite.doc
        if test_suite.metadata:
            base_object['metadata'] = self._json_metadata_convert(test_suite.metadata)
        return base_object
