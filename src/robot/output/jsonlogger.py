from robot.utils import get_timestamp, unic
from robot.version import get_full_version
from robot.result.visitor import ResultVisitor

from .loggerhelper import IsLogged

import json
import copy


RECURSIVE_ITEMS = ["if", "for", "body"]


class JsonLogger(ResultVisitor):

    def __init__(self, path, log_level='TRACE', rpa=False, generator='Robot'):
        self._log_message_is_logged = IsLogged(log_level)
        self._error_message_is_logged = IsLogged('WARN')
        self._path = path

        # Setup the JSON data to store before writing the file
        self._data = {
            'rpa': rpa is not None,
            'generator': get_full_version(generator),
            'generated': get_timestamp()
        }
        self._errors = []

        # Setup stacks
        self._item_stack = list()

        self._current_suite = None
        self._current_body_item = None
        self._current_test = None
        self._current_item = None

    def _format_data(self, item):
        return {key: value for key, value in item.items() if value}

    def append_to_item(self):
        # Remove the "destination" from the dictionary
        destination = self._current_body_item.pop('destination')
        # Format the keyword
        self._current_body_item = self._format_data(self._current_body_item)
        key = 'body'
        # To process the keyword we must have pushed something to the item stack (or have an active suite/test)
        if destination == 'suite':
            parent_item = self._current_suite
            key = 'kw'
        elif destination == 'test':
            parent_item = self._current_test
        elif destination == 'if':
            parent_item = self._item_stack[-1]
            key = 'branches'
        elif destination == 'for':
            parent_item = self._item_stack[-1]
            key = 'iter'
        else:
            parent_item = self._item_stack[-1]

        if key not in parent_item:
            parent_item[key] = list()
        parent_item[key].append(self._current_body_item)
        self._current_body_item = None
        if destination in RECURSIVE_ITEMS:
            self._current_item = destination
        else:
            self._current_item = None

    def _create_status(self, data):
        status = {
            'status': data.status
        }
        if data.starttime:
            status['starttime'] = data.starttime
        if data.endtime:
            status['endtime'] = data.endtime
        if str(data.elapsedtime):
            status['elapsedtime'] = str(data.elapsedtime)
        return status

    def close(self):
        # Create the errors
        messages = [self._create_message(msg) for msg in self._errors]
        self.end_errors(messages)
        # Write the output into a json file
        data = json.dumps(self._data)
        if not isinstance(self._path, str):
            self._path.write(data)
            self._path.close()
        else:
            with open(self._path, 'w') as json_outfile:
                json_outfile.write(data)

    def set_log_level(self, level):
        return self._log_message_is_logged.set_level(level)

    def message(self, msg):
        if self._error_message_is_logged(msg.level):
            self._errors.append(msg)

    def log_message(self, msg):        
        if self._log_message_is_logged(msg.level):
            self._write_message(msg)

    def _write_message(self, msg):
        # Decipher where the message belongs
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                item = self._current_body_item
            elif not self._current_body_item:
                item = self._item_stack[-1]
        else:
            item = self._current_test

        # Make the message
        message = self._create_message(msg)

        # Attach the message to the body
        if 'body' not in item:
            item['body'] = list()
        item['body'].append(message)

    def _create_message(self, msg):
        message = {
            'msg': msg.message,
            'level': msg.level,
            'timestamp': msg.timestamp or 'N/A',
            'type': msg.type
        }
        if msg.html:
            message['html'] = 'true'
        return message

    def start_keyword(self, kw):
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                # Push this onto the stack
                self._item_stack.append(self._current_body_item)
        # If there is no current test then the destination will be the suite
        elif not self._current_test:
            self._current_item = 'suite'
        # If there is no current item then we're running inside of test case
        else:
            self._current_item = 'test'

        self._current_body_item = {
            'name': kw.kwname,
            'lib': kw.libname,
            'type': kw.type if kw.type != 'KEYWORD' else None,
            'doc': kw.doc,
            'tags': [unic(t) for t in kw.tags],
            'args': [unic(a) for a in kw.args],
            'var': [var for var in kw.assign],
            'destination': copy.deepcopy(self._current_item)
        }

        # Mark the type of item
        self._current_item = 'body'

    def end_keyword(self, kw):
        # Check if we have an item in progress
        if not self._current_body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._current_body_item = self._item_stack.pop()

        # Add the rest of the information
        if kw.timeout:
            self._current_body_item['timeout'] = unic(kw.timeout)
        self._current_body_item['status'] = self._create_status(kw)
        self.append_to_item()

    def start_if(self, if_):
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                # Push this onto the stack
                self._item_stack.append(self._current_body_item)
        # If there is no current item then we're running inside of test case
        else:
            self._current_item = 'test'

        self._current_body_item = {
            'doc': if_.doc,
            'type': if_.type,
            'destination': copy.deepcopy(self._current_item)
        }

        # Mark the type of item
        self._current_item = 'if'

    def end_if(self, if_):
        # Check if we have an item in progress
        if not self._current_body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._current_body_item = self._item_stack.pop()

        self._current_body_item['status'] = self._create_status(if_)
        self.append_to_item()

    def start_if_branch(self, branch):
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                # Push this onto the stack
                self._item_stack.append(self._current_body_item)
        # If there is no current item then we're running inside of test case
        else:
            self._current_item = 'test'

        self._current_body_item = {
            'doc': branch.doc,
            'type': branch.type,
            'condition': branch.condition,
            'destination': copy.deepcopy(self._current_item)
        }

        # Mark the type of item
        self._current_item = 'body'

    def end_if_branch(self, branch):
        # Check if we have an item in progress
        if not self._current_body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._current_body_item = self._item_stack.pop()

        self._current_body_item['status'] = self._create_status(branch)
        self.append_to_item()

    def start_for(self, for_):
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                # Push this onto the stack
                self._item_stack.append(self._current_body_item)
        # If there is no current item then we're running inside of test case
        else:
            self._current_item = 'test'

        self._current_body_item = {
            'doc': for_.doc,
            'flavor': for_.flavor,
            'var': [var for var in for_.variables],
            'value': [value for value in for_.values],
            'type': for_.type,
            'destination': copy.deepcopy(self._current_item)
        }

        # Mark the type of item
        self._current_item = 'for'

    def end_for(self, for_):
        # Check if we have an item in progress
        if not self._current_body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._current_body_item = self._item_stack.pop()

        self._current_body_item['status'] = self._create_status(for_)
        self.append_to_item()

    def start_for_iteration(self, iteration):
        if self._current_item in RECURSIVE_ITEMS:
            if self._current_body_item:
                # Push this onto the stack
                self._item_stack.append(self._current_body_item)
        # If there is no current item then we're running inside of test case
        else:
            self._current_item = 'test'

        self._current_body_item = {
            'doc': iteration.doc,
            'var': {name: value for name, value in iteration.variables.items()},
            'type': iteration.type,
            'destination': copy.deepcopy(self._current_item)
        }

        # Mark the type of item
        self._current_item = 'body'

    def end_for_iteration(self, iteration):
        # Check if we have an item in progress
        if not self._current_body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._current_body_item = self._item_stack.pop()

        self._current_body_item['status'] = self._create_status(iteration)
        self.append_to_item()

    def start_test(self, test):
        self._current_test = {
            'id': test.id,
            'name': test.name
        }
        # Mark the type of item (Identify where to place keywords)
        self._current_item = 'test'

    def end_test(self, test):
        self._current_test['doc'] = test.doc
        self._current_test['tags'] = [unic(t) for t in test.tags]
        if test.timeout:
            self._current_test['timeout'] = unic(test.timeout)
        self._current_test['status'] = self._create_status(test)
        # Format the data
        self._current_test = self._format_data(self._current_test)
        # Tests are appended to suites
        if 'tests' not in self._current_suite:
            self._current_suite['tests'] = list()
        self._current_suite['tests'].append(self._current_test)
        self._current_test = None

    def start_suite(self, suite):
        # If there is an "open" suite, this will be placed inside its suites
        if self._current_suite:
            # Push this onto the stack
            self._item_stack.append(self._current_suite)

        # Default the current suite with the suites variables
        self._current_suite = {
            'id': suite.id,
            'name': suite.name,
            'source': suite.source
        }
        # Mark the type of item (not all items are placed back in the same place)
        self._current_item = "suite"

    def end_suite(self, suite):
        # Check if we have an item in progress
        if not self._current_suite:
            # If not, then the suites have been processed for the suite on the stack
            self._current_suite = self._item_stack.pop()

        self._current_suite['doc'] = suite.doc
        self._current_suite['metadata'] = {key: suite.metadata[key] for key in suite.metadata}
        self._current_suite['status'] = self._create_status(suite)

        # Format the data before it's pushed
        self._current_suite = self._format_data(self._current_suite)
        # We pushed onto the stack (the top item is the parent)
        # If there are items on the stack
        if self._item_stack:
            parent_suite = self._item_stack[-1]
            if 'suites' not in parent_suite:
                parent_suite['suites'] = list()
            parent_suite['suites'].append(self._current_suite)
            # Mark the current_suite as being none
            self._current_suite = None
            # Mark the current item as being nothing
            self._current_item = ""
        else:
            # We've reached the bottom of the stack, so assign this suite to the data
            self._data['suite'] = self._current_suite

    def start_statistics(self, stats):
        self._data['statistics'] = {
            'suite': self._create_suite_statistics(stats.suite),
            'total': self._create_total_statistics(stats.total),
            'tag': self._create_tag_statistics(stats.tags)
        }

    def end_errors(self, errors=None):
        if 'errors' not in self._data:
            self._data['errors'] = list()
        self._data['errors'].extend(errors)

    def _create_statistic(self, stat):
        statistic = {
            'name': stat.name,
            'passed': stat.passed,
            'failed': stat.failed
        }
        suite_id = getattr(stat, 'id', None)
        if suite_id:
            statistic['id'] = suite_id
        return statistic

    def _create_tag_stat(self, tag_stat):
        tag_statistic = {
            'name': tag_stat.name,
            'passed': tag_stat.passed,
            'failed': tag_stat.failed,
            'tag': tag_stat.name
        }
        if tag_stat.info:
            tag_statistic['info'] = tag_stat.info
        if tag_stat.doc:
            tag_statistic['doc'] = tag_stat.doc
        return tag_statistic

    def _create_total_statistics(self, total_stats):
        return [self._create_statistic(statistic) for statistic in total_stats]

    def _create_suite_statistics(self, suite_stats):
        suites = suite_stats.suites + [suite_stats]
        return [self._create_statistic(statistic.stat) for statistic in suites]

    def _create_tag_statistics(self, tag_stats):
        return [self._create_tag_stat(tag_stats.tags[tag]) for tag in tag_stats.tags]
