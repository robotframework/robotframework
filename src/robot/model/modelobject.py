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

from robot.utils import SetterAwareType, py2to3, with_metaclass


@py2to3
class ModelObject(with_metaclass(SetterAwareType, object)):
    __slots__ = []

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return repr(str(self))

    def __setstate__(self, state):
        """Customize the attribute updating when using `copy.copy` or `copy.deepcopy`
        """

        # We should consider the state format per pickle protocol version
        # Refer to: https://www.python.org/dev/peps/pep-0307
        if isinstance(state, tuple) and len(state) == 2:
            dictstate, slotstate = state
        else:
            dictstate = state
            slotstate = None

        if dictstate is not None:
            self.__dict__.update(dictstate)

        def get_setter_name(x):
            return '_setter__' + x

        if slotstate is not None:
            for k, v in slotstate.iteritems():
                setter_name = get_setter_name(k)
                # If we have defined the attribute both in __slots__ and with @setter,
                # we just need to set the setter attribute.
                if setter_name in slotstate:
                    continue

                setattr(self, k, v)



