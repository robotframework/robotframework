#  Copyright 2008-2014 Nokia Solutions and Networks
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


class _AbstractWinformsDialog:

    def __init__(self):
        raise RuntimeError('This keyword is not yet implemented with IronPython')


class MessageDialog(_AbstractWinformsDialog):

    def __init__(self, message):
        _AbstractWinformsDialog.__init__(self)


class InputDialog(_AbstractWinformsDialog):

    def __init__(self, message, default, hidden=False):
        _AbstractWinformsDialog.__init__(self)


class SelectionDialog(_AbstractWinformsDialog):

    def __init__(self, message, options):
        _AbstractWinformsDialog.__init__(self)


class PassFailDialog(_AbstractWinformsDialog):

    def __init__(self, message):
        _AbstractWinformsDialog.__init__(self)
