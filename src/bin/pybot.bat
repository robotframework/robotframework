@echo off

::  Copyright 2008-2009 Nokia Siemens Networks Oyj
::
::  Licensed under the Apache License, Version 2.0 (the "License");
::  you may not use this file except in compliance with the License.
::  You may obtain a copy of the License at
::
::      http://www.apache.org/licenses/LICENSE-2.0
::
::  Unless required by applicable law or agreed to in writing, software
::  distributed under the License is distributed on an "AS IS" BASIS,
::  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
::  See the License for the specific language governing permissions and
::  limitations under the License.


::
:: pybot.bat -- Python start up script for Robot Framework on Windows
:: 

:: Python executable to use. 
set python="[PYTHON_EXECUTABLE]"

:: Path to robot\runner.py
set runner="[ROBOT_DIR]\runner.py" 

:: Run Robot on Python interpreter
%python% %runner% %*
