*** Settings ***
Documentation   Tests for checking that library initialization arguments are handled correctly. Taking libraries without arguments is not tested here, because almost every other suite does that.
Suite Setup     Run Tests  ${EMPTY}  test_libraries/library_imports_with_args.robot
Resource        resource_for_importing_libs_with_args.robot
Test Template   Library import should have been successful


*** Test Cases ***

Mandatory arguments
    libswithargs.Mandatory  first arg  another arg

Default values
    libswithargs.Defaults  m1
    libswithargs.Defaults  m2  d1
    libswithargs.Defaults  m3  1  default2=2
    libswithargs.Defaults  mx  default2=xxx
    libswithargs.Defaults  mx  default2=xxx

Varargs
    libswithargs.Varargs  m1
    libswithargs.Varargs  m2  v1
    libswithargs.Varargs  m3  1  2

Mixed
    libswithargs.Mixed  m1
    libswithargs.Mixed  m2  d1
    libswithargs.Mixed  m3  d1
    libswithargs.Mixed  m4  d2  v
    libswithargs.Mixed  m5  d3  v1  v2

Variables containing objects
    libswithargs.Mixed  [1, 2, 3, 4, 'foo', 'bar']  {'a': 1}  None  42
    libswithargs.Defaults  None  1.0  default2=not named

Too Few Arguments
    [Template]  Library import should have failed
    libswithargs.Mandatory  2 arguments, got 1.
    libswithargs.Defaults  1 to 3 arguments, got 0.
    libswithargs.Varargs  at least 1 argument, got 0.

Too Many Arguments
    [Template]  Library import should have failed
    libswithargs.Mandatory  2 arguments, got 4.
    libswithargs.Defaults  1 to 3 arguments, got 5.

Non-existing variables
    [Template]
    Syslog Should Contain  Variable '\${NONEXISTING}' not found.
