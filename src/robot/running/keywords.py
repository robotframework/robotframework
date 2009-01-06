#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import time

from robot import utils
from robot.errors import FrameworkError, ExecutionFailed, DataError
from robot.common import BaseKeyword
from robot.variables import is_list_var


def KeywordFactory(kwdata):
    if kwdata.type == 'kw':
        return Keyword(kwdata.name, kwdata.args)
    try:
        clazz = { 'set': SetKeyword, 'repeat': RepeatKeyword, 
                  'for': ForKeyword, 'parallel': ParallelKeyword,
                  'error': SyntaxErrorKeyword }[kwdata.type]
        return clazz(kwdata)
    except KeyError:
        raise FrameworkError("Invalid kw type '%s'" % kwdata.type)


class Keyword(BaseKeyword):

    def __init__(self, name, args, type='kw'):
        BaseKeyword.__init__(self, name, args, type=type)
        self.handler_name = name
        
    def run(self, output, namespace):
        handler = namespace.get_handler(self.handler_name)
        if handler.type == 'user':
            handler.init_user_keyword(namespace.variables)
        self.name = self._get_name(handler.longname, namespace.variables)
        self.doc = handler.shortdoc
        self.timeout = str(handler.timeout)
        self.starttime = utils.get_timestamp()
        output.start_keyword(self)
        if self.doc.startswith('*DEPRECATED*'):
            # SYSLOG is not initialized if imported in module
            from robot.output import SYSLOG
            msg = self.doc.replace('*DEPRECATED*', '', 1).strip()
            SYSLOG.warn("Keyword '%s' is deprecated. %s" % (self.name, msg))
        try:
            ret = self._run(handler, output, namespace)
        except ExecutionFailed, err:
            self.status = 'FAIL'
        else:
            self.status = 'PASS'
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        output.end_keyword(self)
        if self.status == 'FAIL':
            raise err
        return ret
    
    def _get_name(self, handler_name, variables):
        return handler_name
    
    def _run(self, handler, output, namespace):
        try:
            return handler.run(output, namespace, self.args[:])
        except ExecutionFailed:
            raise 
        except:
            msg, details = utils.get_error_details()
            output.fail(msg)
            if details:
                output.debug(details)
            raise ExecutionFailed(utils.cut_long_message(msg))


class SetKeyword(Keyword):
    
    def __init__(self, kwdata):
        self.scalar_vars = kwdata.scalar_vars
        self.list_var = kwdata.list_var
        Keyword.__init__(self, kwdata.name, kwdata.args, 'set')
        
    def _get_name(self, handler_name, variables):
        varz = self.scalar_vars[:]
        if self.list_var is not None:
            varz.append(self.list_var)
        return '%s = %s' % (', '.join(varz), handler_name)
    
    def _run(self, handler, output, namespace):
        ret = Keyword._run(self, handler, output, namespace)
        try:
            vars_to_set = self._get_vars_to_set(ret)
        except DataError, err:
            msg = str(err)
            output.fail(msg)
            raise ExecutionFailed(msg)
        for name, value in vars_to_set:
            namespace.variables[name] = value
            if is_list_var(name) or utils.is_list(value):
                value = utils.seq2str2(value)
            else:
                value = utils.unic(value)
            output.info('%s = %s' % (name, utils.cut_long_assign_msg(value)))
        
    def _get_vars_to_set(self, ret):
        if ret is None:
            return self._get_vars_to_set_when_ret_is_none()
        if self.list_var is None:
            return self._get_vars_to_set_with_only_scalars(ret)
        if utils.is_list(ret):
            return self._get_vars_to_set_with_scalars_and_list(ret)
        self._raise_invalid_return_value(ret, wrong_type=True)

    def _get_vars_to_set_when_ret_is_none(self):
        ret = [ (var, None) for var in self.scalar_vars ]
        if self.list_var is not None:
            ret.append((self.list_var, []))
        return ret

    def _get_vars_to_set_with_only_scalars(self, ret):
        needed = len(self.scalar_vars)
        if needed == 1:
            return [(self.scalar_vars[0], ret)]
        if not utils.is_list(ret):
            self._raise_invalid_return_value(ret, wrong_type=True)
        ret = list(ret)
        if len(ret) < needed:
            self._raise_invalid_return_value(ret)
        if len(ret) == needed:
            return zip(self.scalar_vars, ret)
        return zip(self.scalar_vars[:-1], ret) \
                    + [(self.scalar_vars[-1], ret[needed-1:])]
    
    def _get_vars_to_set_with_scalars_and_list(self, ret):
        ret = list(ret)
        needed_scalars = len(self.scalar_vars)
        if not needed_scalars:
            return [(self.list_var, ret)]
        if len(ret) < needed_scalars:
            self._raise_invalid_return_value(ret)
        return zip(self.scalar_vars, ret) \
                    + [(self.list_var, ret[needed_scalars:])]

    def _raise_invalid_return_value(self, ret, wrong_type=False):
        if wrong_type:
            err = 'Expected list, got %s instead' % utils.type_as_str(ret, True)
        elif ret is None:
            err = 'Keyword returned nothing'
        else:
            err = 'Need more values than %d' % len(ret)
        varz = self.scalar_vars[:]
        if self.list_var is not None: 
            varz.append(self.list_var)
        name = self.name.split(' = ', 1)[1]
        raise DataError("Cannot assign return value of keyword '%s' to "
                        "variable%s %s: %s" % (name, utils.plural_or_not(varz),
                                               utils.seq2str(varz), err))


class RepeatKeyword(Keyword):
    
    def __init__(self, kwdata):
        self._orig_repeat = self._repeat = kwdata.repeat
        self._error = None
        Keyword.__init__(self, kwdata.name, kwdata.args, 'repeat')
        data = ['%s x' % kwdata.repeat, kwdata.name] + kwdata.args
        self._syntax_example = '| %s |' % ' | '.join(data)
        
    def _run(self, handler, output, namespace):
        msg = ("Repeating keywords using the special syntax like '%s' "
               "is deprecated and will be removed in Robot Framework 2.2. "
               "Use 'BuiltIn.Repeat Keyword' instead." % self._syntax_example)
        output.warn(msg)
        output.syslog.warn(msg)
        if self._error is not None:
            output.fail(self._error)
            raise ExecutionFailed(self._error)
        for _ in range(self._repeat):
            Keyword._run(self, handler, output, namespace)
            
    def _get_name(self, handler_name, variables):
        if not utils.is_integer(self._orig_repeat):
            try:
                self._repeat = self._get_repeat(variables)
            except DataError, err:
                self._error = str(err)
        return '%sx %s' % (self._repeat, handler_name)

    def _get_repeat(self, variables):
        repeat = variables.replace_string(self._orig_repeat)
        try:
            return int(repeat)
        except ValueError:
            t = utils.type_as_str(repeat, printable=True) 
            raise DataError("Value of a repeat variable '%s' should be an "
                            "integer, got %s instead" % (self._orig_repeat, t))


class ForKeyword(BaseKeyword):
   
    def __init__(self, kwdata):
        self.vars = kwdata.vars
        self.items = kwdata.items
        self.range = kwdata.range
        BaseKeyword.__init__(self, kwdata.name, type='for')
        self.keywords = [ KeywordFactory(kw) for kw in kwdata.keywords ]

    def run(self, output, namespace):
        self.starttime = utils.get_timestamp()
        output.start_keyword(self)
        try:
            self._run(output, namespace)
        except ExecutionFailed, err:
            error = err
        except DataError, err:
            msg = str(err)
            output.fail(msg)
            error = ExecutionFailed(msg)
        else:
            error = None
        self.status = error is None and 'PASS' or 'FAIL'
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        output.end_keyword(self)
        if error is not None:
            raise error
            
    def _run(self, output, namespace):
        items = self._replace_vars_from_items(namespace.variables)
        for i in range(0, len(items), len(self.vars)):
            values = items[i:i+len(self.vars)]
            self._run_one_round(output, namespace, self.vars, values)

    def _run_one_round(self, output, namespace, variables, values):
        foritem = ForItemKeyword(variables, values)
        output.start_keyword(foritem)
        for var, value in zip(variables, values):
            namespace.variables[var] = value
        error = None
        for kw in self.keywords:
            try:
                kw.run(output, namespace)
            except ExecutionFailed, error:
                break
        foritem.end(error is None and 'PASS' or 'FAIL')
        output.end_keyword(foritem)
        if error is not None:
            raise error

    def _replace_vars_from_items(self, variables):
        items = variables.replace_list(self.items)
        if self.range:
            items = self._get_range_items(items)
        if len(items) % len(self.vars) == 0:
            return items
        raise DataError('Number of FOR loop values should be multiple of '
                        'variables. Got %d variables (%s) but %d value%s.'
                        % (len(self.vars), utils.seq2str(self.vars), 
                           len(items), utils.plural_or_not(items)))

    def _get_range_items(self, items):
        try:
            items = [ int(item) for item in items ]
        except ValueError:
            raise DataError('FOR IN RANGE expected integer arguments, '
                            'got %s instead.' % utils.type_as_str(item, True))
        if not 1 <= len(items) <= 3:
            raise DataError('FOR IN RANGE expected 1-3 arguments, '
                            'got %d instead.' % len(items))
        return range(*items)
    
     
class ForItemKeyword(BaseKeyword):
    
    def __init__(self, vars, items):
        name = ', '.join([ '%s = %s' % (var, utils.cut_long_assign_msg(item))
                           for var, item in zip(vars, items) ])
        BaseKeyword.__init__(self, name, type='foritem')
        self.starttime = utils.get_timestamp()
        
    def end(self, status):
        self.status = status
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)

    
class ParallelKeyword(BaseKeyword):
    
    def __init__(self, kwdata):
        BaseKeyword.__init__(self, kwdata.name, type='parallel')
        self.keywords = [ KeywordFactory(kw) for kw in kwdata.keywords ]
                   
    def run(self, output, namespace):
        self.starttime = utils.get_timestamp()
        self.status = 'PASS'
        output.start_keyword(self)
        running_keywords = []
        errors = []
        for kw in self.keywords:
            kw.__call__ = kw.run
            recorder = _OutputRecorder()
            runner = utils.robotthread.Runner(kw, (recorder, namespace.copy()))
            utils.robotthread.Thread(runner).start()
            running_keywords.append((runner, recorder))
            # Give started keyword some time to really start. This is ugly
            # but required because there seems to be some threading problems
            # at least on faster machines otherwise. Would be better to 
            # investigate more but parallel execution is so little used 
            # feature that it does not make much sense right now.
            time.sleep(0.1)
        for runner, recorder in running_keywords:
            try:
                runner.get_result()
            except ExecutionFailed, err:
                errors.append(str(err))
                self.status = 'FAIL'
            recorder.replay(output)
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        output.end_keyword(self)
        if len(errors) > 0:
            if len(errors) > 1:
                errors = [ 'Error %d: %s' % (i+1, err) 
                           for i, err in enumerate(errors) ]
            raise ExecutionFailed('\n\n'.join(errors))


class _OutputRecorder:
    
    def __init__(self):
        self._actions = []
    
    def __getattr__(self, name):
        return lambda *args : self._actions.append((name, args))
        
    def replay(self, output):
        for name, args in self._actions:
            getattr(output, name)(*args)
            

class SyntaxErrorKeyword(BaseKeyword):
    
    def __init__(self, kwdata):
        BaseKeyword.__init__(self, kwdata.name, type='error')
        self._error = kwdata.error
        
    def run(self, output, namespace):
        self.starttime = utils.get_timestamp()
        self.status = 'FAIL'
        output.start_keyword(self)
        output.fail(self._error)
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        output.end_keyword(self)
        raise ExecutionFailed(self._error)
