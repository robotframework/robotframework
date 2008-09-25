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


# Return codes from Robot and Rebot. 
# RC below 250 is the number of failed critical tests and exactly 250
# means that number or more such failures.
INFO_PRINTED    = 251   # --help or --version
DATA_ERROR      = 252   # Invalid data or cli args
STOPPED_BY_USER = 253   # KeyboardInterrupt or SystemExit
FRAMEWORK_ERROR = 255   # Unexpected error


class RobotError(Exception):
    """Base class for Robot errors
    
    Do not raise this method but use more specific errors instead.
    """

class FrameworkError(RobotError):
    """Can be used when the core framework goes to unexpected state

    It is good to explicitely raise a FrameworkError if some framework 
    component is used incorrectly. This is pretty much same as
    'Internal Error' and should of course never happen.
    """
    
class DataError(RobotError):
    """Should be used when provided test data is incorrect"""

class ExecutionFailed(RobotError):
    """Used for cummunicating failures in test execution"""
    
class TimeoutError(RobotError):
    """Used when test execution is timed out"""

class RemoteError(RobotError):
    """Used by Remote library to report remote errors"""
    def __init__(self, message, traceback):
        RobotError.__init__(self, message)
        self.traceback = traceback

