#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import copy

from robot.utils import py3to2, SetterAwareType, with_metaclass


@py3to2
class ModelObject(with_metaclass(SetterAwareType, object)):
    repr_args = ()
    __slots__ = []

    def config(self, **attributes):
        """Configure model object with given attributes.

        ``obj.config(name='Example', doc='Something')`` is equivalent to setting
        ``obj.name = 'Example'`` and ``obj.doc = 'Something'``.

        New in Robot Framework 4.0.
        """
        for name in attributes:
            setattr(self, name, attributes[name])
        return self

    def copy(self, **attributes):
        """Return shallow copy of this object.

        :param attributes: Attributes to be set for the returned copy
            automatically. For example, ``test.copy(name='New name')``.

        See also :meth:`deepcopy`. The difference between these two is the same
        as with the standard ``copy.copy`` and ``copy.deepcopy`` functions
        that these methods also use internally.
        """
        copied = copy.copy(self)
        for name in attributes:
            setattr(copied, name, attributes[name])
        return copied

    def deepcopy(self, **attributes):
        """Return deep copy of this object.

        :param attributes: Attributes to be set for the returned copy
            automatically. For example, ``test.deepcopy(name='New name')``.

        See also :meth:`copy`. The difference between these two is the same
        as with the standard ``copy.copy`` and ``copy.deepcopy`` functions
        that these methods also use internally.
        """
        copied = copy.deepcopy(self)
        for name in attributes:
            setattr(copied, name, attributes[name])
        return copied

    def __repr__(self):
        args = ['%s=%r' % (n, getattr(self, n)) for n in self.repr_args]
        module = type(self).__module__.split('.')
        if len(module) > 1 and module[0] == 'robot':
            module = module[:2]
        return '%s.%s(%s)' % ('.'.join(module), type(self).__name__, ', '.join(args))
