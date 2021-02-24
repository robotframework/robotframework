from robot.utils import get_timestamp, unic
from robot.version import get_full_version
from robot.result.visitor import ResultVisitor

from .loggerhelper import IsLogged

import enum
import json
import copy

# Temporary fix to not break RF
try:
    import jsonstreams
except ImportError:
    pass


class RobotElement(object):
    def __init__(self, subobject, elem_type, destination, elems=None):
        # Store the object we're writing into
        self._subobject = subobject
        self._body = None
        # Store the type & destination for the object
        self.destination = destination
        self.type = elem_type
        if elems:
            # Store the elements initially given into the subobject
            for key, value in elems.items():
                self[key] = value

    def __setitem__(self, key, value):
        # Ensure that the values aren't None, empty string, or empty list
        # Cannot do "if value" because this would ignore "False" booleans
        if value is not None and value != '' and value != []:
            self._subobject.write(key, value)

    def body(self):
        return self._body if self._body else self.create_body()

    def subobject(self, key=None):
        if key:
            return self._subobject.subobject(key)
        else:
            return self._subobject.subobject()

    def subarray(self, key):
        return self._subobject.subarray(key)

    def make_body(self):
        self._body = self._subobject.subarray('body')
        return self._body

    def make_branches(self):
        self._body = self._subobject.subarray('branches')
        return self._body

    def make_iter(self):
        self._body = self._subobject.subarray('iter')
        return self._body

    def create_body(self, ):
        if self.type == Items.IF_:
            return self.make_branches()
        elif self.type == Items.TEST or \
              self.type == Items.BODY:
            return self.make_body()
        elif self.type == Items.FOR_:
            return self.make_iter()
        else:
            raise ValueError("Bad element type attempting to make body")

    def close_body(self):
        if self._body:
            self._body.close()
            self._body = None

    def close(self):
        if self._body:
            self._body.close()
        try:
            self._subobject.close()
        except jsonstreams.ModifyWrongStreamError:
            # Already closed
            pass


class RobotSuiteElement(RobotElement):
    def __init__(self, subobject, elem_type, destination, elems=None):
        super(RobotSuiteElement, self).__init__(subobject, elem_type, destination, elems)
        self._suites = None
        self._tests = None

    def make_suites(self):
        self._suites = self._subobject.subarray('suites')
        return self._suites

    def suites(self):
        return self._suites if self._suites else self.make_suites()

    def make_tests(self):
        self._tests = self._subobject.subarray('tests')
        return self._tests

    def tests(self):
        return self._tests if self._tests else self.make_tests()

    def close_body(self):
        self.close_tests()

    def close_tests(self):
        if self._tests:
            self._tests.close()
            self._tests = None

    def close_suites(self):
        if self._suites:
            self._suites.close()
            self._suites = None

    def close(self):
        if self._suites:
            self._suites.close()
        if self._tests:
            self._tests.close()
        super(RobotSuiteElement, self).close()


class Items(enum.Enum):
    SUITE = "suite"
    TEST = "test"
    IF_ = "if"
    FOR_ = "for"
    BODY = "body"
    STATS = "stats"
    STAT = "stat"
    TOTAL = "total"
    TAG = "tag"
    SUITE_STATS = "suite"
    ERRORS = "errors"



RECURSIVE_ITEMS = [Items.IF_, Items.FOR_, Items.BODY]



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

        # We need to keep track of the active suite, test, and body item
        self._suite = None
        self._body = None
        self._body_item = None
        self._test = None
        self._errors_element = None

        # We need to be able to track the type of item being processed
        # at any moment
        self._item_type = None

        self._root = jsonstreams.Stream(jsonstreams.Type.object, filename=self._path)
        self._root.write('rpa', rpa is not None)
        self._root.write('generator', get_full_version(generator))
        self._root.write('generated', get_timestamp())

    def _format_data(self, item):
        return {key: value for key, value in item.items() if value}

    def open_item(self):
        if self._item_type in RECURSIVE_ITEMS:
            if self._body_item:
                # Push this onto the stack
                subobject = self._body_item.body().subobject()
                self._item_stack.append(self._body_item)
            else:
                subobject = self._item_stack[-1].body().subobject()
        # If there is no current item then we're running inside of test case
        else:
            subobject = self._test.body().subobject()
            self._item_type = Items.TEST
        return subobject

    def close_item(self):
        # Get the items destination
        destination = self._body_item.destination
        # Close the ite,
        self._body_item.close()
        # Remove any reference to the item
        self._body_item = None
        # Mark down the destination type
        if destination in RECURSIVE_ITEMS:
            self._item_type = destination
        else:
            self._item_type = None

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
        if self._errors:
            self.start_errors()
            messages = [self._create_message(msg) for msg in self._errors]
            self.end_errors(messages)
        # Close the root object (and hence the file)
        self._root.close()

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
        if self._item_type in RECURSIVE_ITEMS:
            if self._body_item:
                item = self._body_item
            elif not self._body_item:
                item = self._item_stack[-1]
        else:
            item = self._test

        # Make the message
        message = self._create_message(msg)

        # Attach the message to the body
        RobotElement(item.body().subobject(), None, None, message).close()
        

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
        # Only a suite will not store a keyword in its body.
        # This is because for tests and setups to store them
        # differently would require more advanced JSON streaming
        subobject = None
        # Setup keywords can be emitted by Test cases and Suite
        if kw.type == 'SETUP' and not self._test and self._suite:
            subobject = self._suite.subobject('setup')
        # Teardown keywords can be emitted by Test cases, suites, and keywords
        if kw.type == 'TEARDOWN':
            # If the item stack is empty, or the item on the end of the stack is
            # not a BODY type and there is no test activate and the suite is active
            if (not self._item_stack or not self._item_stack[-1].type == Items.BODY) \
                 and not self._test and self._suite:
                # Close the body of the suite, since the teardown is being called
                # the suite
                self._suite.close_body()
                subobject = self._suite.subobject('teardown')
        if subobject is None:
            subobject = self.open_item()

        self._body_item = RobotElement(subobject, Items.BODY, copy.deepcopy(self._item_type), {
            'name': kw.kwname,
            'lib': kw.libname,
            'type': kw.type if kw.type != 'KEYWORD' else None,
            'doc': kw.doc,
            'tags': [unic(t) for t in kw.tags],
            'args': [unic(a) for a in kw.args],
            'var': [var for var in kw.assign]
        })
        # Mark the type of item
        self._item_type = Items.BODY

    def end_keyword(self, kw):
        # Check if we have an item in progress
        if not self._body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._body_item = self._item_stack.pop()
        self._body_item.close_body()

        # Add the rest of the information
        if kw.timeout:
            self._body_item['timeout'] = unic(kw.timeout)
        self._body_item['status'] = self._create_status(kw)
        self.close_item()

    def start_if(self, if_):
        self._body_item = RobotElement(self.open_item(), Items.IF_, copy.deepcopy(self._item_type), {
            'doc': if_.doc,
            'type': if_.type
        })
        # Mark the type of item
        self._item_type = Items.IF_

    def end_if(self, if_):
        # Check if we have an item in progress
        if not self._body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._body_item = self._item_stack.pop()
        self._body_item.close_body()

        self._body_item['status'] = self._create_status(if_)
        self.close_item()

    def start_if_branch(self, branch):
        self._body_item = RobotElement(self.open_item(), Items.BODY, copy.deepcopy(self._item_type), {
            'doc': branch.doc,                                                                                                             
            'type': branch.type,
            'condition': branch.condition
        })
        # Mark the type of item
        self._item_type = Items.BODY

    def end_if_branch(self, branch):
        # Check if we have an item in progress
        if not self._body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._body_item = self._item_stack.pop()
        self._body_item.close_body()

        self._body_item['status'] = self._create_status(branch)
        self.close_item()

    def start_for(self, for_):
        self._body_item = RobotElement(self.open_item(), Items.FOR_, copy.deepcopy(self._item_type), {
            'doc': for_.doc,
            'flavor': for_.flavor,
            'var': [var for var in for_.variables],
            'value': [value for value in for_.values],
            'type': for_.type
        })
        # Mark the type of item
        self._item_type = Items.FOR_

    def end_for(self, for_):
        # Check if we have an item in progress
        if not self._body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._body_item = self._item_stack.pop()
        self._body_item.close_body()

        self._body_item['status'] = self._create_status(for_)
        self.close_item()

    def start_for_iteration(self, iteration):
        self._body_item = RobotElement(self.open_item(), Items.BODY, copy.deepcopy(self._item_type), {
            'doc': iteration.doc,
            'var': {name: value for name, value in iteration.variables.items()},
            'type': iteration.type
        })
        # Mark the type of item
        self._item_type = Items.BODY

    def end_for_iteration(self, iteration):
        # Check if we have an item in progress
        if not self._body_item:
            # If not, then the keywords have been processed for the item on the stack
            self._body_item = self._item_stack.pop()
        self._body_item.close_body()

        self._body_item['status'] = self._create_status(iteration)
        self.close_item()

    def start_test(self, test):
        self._suite.close_suites()
        self._test = RobotElement(self._suite.tests().subobject(), Items.TEST, None, {
            'id': test.id,
            'name': test.name
        })
        # Mark the type of item (Identify where to place keywords)
        self._item_type = Items.TEST

    def end_test(self, test):
        self._test.close_body()
        self._test['doc'] = test.doc
        self._test['tags'] = [unic(t) for t in test.tags]
        if test.timeout:
            self._test['timeout'] = unic(test.timeout)
        self._test['status'] = self._create_status(test)
        self._test.close()
        self._test = None

    def start_suite(self, suite):
        # If there is an "open" suite, this will be placed inside its suites
        if self._suite:
            subobject = self._suite.suites().subobject()
            # Push this onto the stack
            self._item_stack.append(self._suite)
        elif self._item_stack:
            # This should be a suite object on the stack
            subobject = self._item_stack[-1].suites().subobject()
        else:
            subobject = self._root.subobject('suite')

        self._suite = RobotSuiteElement(subobject, Items.SUITE, None, {
            'id': suite.id,
            'name': suite.name,
            'source': suite.source
        })
        # Mark the type of item (not all items are placed back in the same place)
        self._item_type = Items.SUITE

    def end_suite(self, suite):
        # Check if we have an item in progress
        if not self._suite:
            # If not, then the suites have been processed for the suite on the stack
            self._suite = self._item_stack.pop()
        self._suite.close_suites()
        self._suite.close_tests()

        self._suite['doc'] = suite.doc
        self._suite['metadata'] = {key: suite.metadata[key] for key in suite.metadata}
        self._suite['status'] = self._create_status(suite)
        self._suite.close()
        self._suite = None
        # Mark the current item as being nothing
        self._item_type = ""

    def start_statistics(self, stats):
        self._body_item = RobotElement(self._root.subobject('statistics'), Items.STATS, Items.SUITE)
        self._item_type = Items.STATS

    def end_statistics(self, stats):
        self._body_item.close()

    def start_total_statistics(self, total_stats):
        if self._body_item.type != Items.STATS:
            raise ValueError("The current item is not set to be a statistic")
        subarray = self._body_item.subarray('total')
        self._item_stack.append(self._body_item)
        self._body_item = RobotElement(subarray, Items.TOTAL, Items.STATS)
        self._item_type = Items.TOTAL

    def end_total_statistics(self, total_stats):
        if self._item_type != Items.TOTAL:
            self._body_item = self._item_stack.pop()
        self._body_item.close() 
        # Pop the stack off of the queue
        self._body_item = self._item_stack.pop()

    def start_tag_statistics(self, tag_stats):
        if self._body_item.type != Items.STATS:
            raise ValueError("The current item is not set to be a statistic")
        subarray = self._body_item.subarray('tag')
        self._item_stack.append(self._body_item)
        self._body_item = RobotElement(subarray, Items.TOTAL, Items.STATS)
        self._item_type = Items.TAG

    def end_tag_statistics(self, tag_stats):
        if self._item_type != Items.TAG:
            self._body_item = self._item_stack.pop()
        self._body_item.close() 
        # Pop the stack off of the queue
        self._body_item = self._item_stack.pop()

    def start_suite_statistics(self, tag_stats):
        if self._body_item.type != Items.STATS:
            raise ValueError("The current item is not set to be a statistic")
        subarray = self._body_item.subarray('suite')
        self._item_stack.append(self._body_item)
        self._body_item = RobotElement(subarray, Items.TOTAL, Items.STATS)
        self._item_type = Items.SUITE_STATS

    def end_suite_statistics(self, tag_stats):
        if self._item_type != Items.SUITE_STATS:
            self._body_item = self._item_stack.pop()
        self._body_item.close() 
        # Pop the stack off of the queue
        self._body_item = self._item_stack.pop()

    def visit_stat(self, stat):
        subobject = self._body_item.subobject()
        stat_json = stat.get_attributes()
        stat_json['name'] = stat.name
        if self._item_type == Items.TAG:
            stat_json['tag'] = stat.name
        RobotElement(subobject, Items.STAT, self._item_type, stat_json).close()

    def start_errors(self, errors=None):
        self._errors_element = RobotElement(self._root.subarray('errors'), Items.ERRORS, Items.SUITE)

    def end_errors(self, errors=None):
        for msg in self._errors:        
            RobotElement(self._errors_element.subobject(),
                         Items.BODY,
                         Items.ERRORS,
                         self._create_message(msg)).close()
        self._errors_element.close()
        self._body_item = None

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
