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

from robot.utils import SetterAwareType, py2to3, unicode, with_metaclass


@py2to3
class ModelObject(with_metaclass(SetterAwareType, object)):
    __slots__ = []

    def copy(self, **attributes):
        """Return shallow copy of this object.

        :param attributes: Attributes to be set for the returned copy
            automatically. For example, ``test.copy(name='New name')``.

        See also :meth:`deepcopy`. The difference between these two is the same
        as with the standard ``copy.copy`` and ``copy.deepcopy`` functions
        that these methods also use internally.

        New in Robot Framework 3.0.1.
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

        New in Robot Framework 3.0.1.
        """
        copied = copy.deepcopy(self)
        for name in attributes:
            setattr(copied, name, attributes[name])
        return copied

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return repr(unicode(self))

    def __setstate__(self, state):
        """Customize attribute updating when using the `copy` module.

        This may not be needed in the future if we fix the mess we have with
        different timeout types.
        """
        # We have __slots__ so state is always a two-tuple.
        # Refer to: https://www.python.org/dev/peps/pep-0307
        dictstate, slotstate = state
        if dictstate is not None:
            self.__dict__.update(dictstate)
        for name in slotstate:
            # If attribute is defined in __slots__ and overridden by @setter
            # (this is the case at least with 'timeout' of 'running.TestCase')
            # we must not set the "real" attribute value because that would run
            # the setter method and that would recreate the object when it
            # should not. With timeouts recreating object using the object
            # itself would also totally fail.
            setter_name = '_setter__' + name
            if setter_name not in slotstate:
                setattr(self, name, slotstate[name])
