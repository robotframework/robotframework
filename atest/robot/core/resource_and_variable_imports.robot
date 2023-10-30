*** Settings ***
Suite Setup        Run Tests With Non-ASCII Items In PYTHONPATH
Resource           atest_resource.robot

*** Variables ***
${DATAFILE}        core/resource_and_variable_imports.robot
${RESDIR}          ${DATADIR}/core/resources_and_variables
${PPATH_RESDIR}    ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Normal Resource Import
    [Documentation]    Test that path given in resource import is relative to
    ...                the current directory and that '/' is converted to
    ...                correct path separator depending on the OS.
    Check Test Case    ${TEST NAME}

Resource Import With Variables
    [Documentation]    Test that variables can be used in resource import path.
    ...                Also test that path can be absolute.
    Check Test Case    ${TEST NAME}

Normal Variable Import
    [Documentation]    Test that path given in variable import is relative to
    ...                the current directory and that '/' is converted to
    ...                correct path separator depending on the OS.
    Check Test Case    ${TEST NAME}

Not Included In __all__
    Check Test Case    ${TEST NAME}

Variable Import With Variables
    [Documentation]    Test that variables can be used in variable import path.
    ...                Also test that path can be absolute.
    Check Test Case    ${TEST NAME}

Invalid List Variable
    [Documentation]    List variable not containing a list value causes an error
    Check Test Case    ${TEST NAME}
    ${path} =    Normalize Path    ${RESDIR}/invalid_list_variable.py
    Error in file    17    ${DATAFILE}    48
    ...    Processing variable file '${path}' failed:
    ...    Invalid variable 'LIST__invalid_list': Expected a list-like value, got string.

Dynamic Variable File
    Check Test Case    ${TEST NAME}

Dynamic Variable File With Variables And Backslashes In Args
    Check Test Case    ${TEST NAME}

Static variable file does not accept arguments
    ${path} =    Normalize Path    ${DATADIR}/core/resources_and_variables/variables.py
    Error in file    6    ${DATAFILE}    18
    ...    Processing variable file '${path}' with arguments ['static', 'does', 'not', 'accept', 'args'] failed: Static variable files do not accept arguments.
    ...    pattern=False

Too few arguments to dynamic variable file
    ${path} =    Normalize Path    ${DATADIR}/core/resources_and_variables/dynamic_variables.py
    Error in file    7    ${DATAFILE}    19
    ...    Processing variable file '${path}' failed: Variable file expected 1 to 4 arguments, got 0.

Too many arguments to dynamic variable file
    ${path} =    Normalize Path    ${DATADIR}/core/resources_and_variables/dynamic_variables.py
    Error in file    8    ${DATAFILE}    20
    ...    Processing variable file '${path}' with arguments ['More', 'than', 'four', 'arguments', 'fails'] failed: Variable file expected 1 to 4 arguments, got 5.
    ...    pattern=False

Invalid return value from dynamic variable file
    ${path} =    Normalize Path    ${RESDIR}/dynamic_variables.py
    Error in file    4    ${DATAFILE}    10
    ...    Processing variable file '${path}' with arguments ['Three args', 'returns None', 'which is invalid'] failed:
    ...    Expected 'get_variables' to return a dictionary-like value, got None.
    ...    pattern=False

Dynamic variable file raises exception
    ${path} =    Normalize Path    ${RESDIR}/dynamic_variables.py
    Error in file    5    ${DATAFILE}    12
    ...    Processing variable file '${path}' with arguments ['Four', 'args', 'raises', 'exception'] failed:
    ...    Ooops!
    ...    pattern=False

Non-Existing Variable In Arguments To Dynamic Variable File
    ${path} =    Normalize Path    ${RESDIR}/dynamicVariables.py
    Error in file    16    ${DATAFILE}    47
    ...    Replacing variables from setting 'Variables' failed:
    ...    Variable '\${non_existing_var_as_arg}' not found.

Resource Importing Resources
    Check Test Case    ${TEST NAME}

Resource Importing Variables
    Check Test Case    ${TEST NAME}

Resource Importing Library
    Check Test Case    ${TEST NAME}

Re-Import Resource File
    [Template]    File Should Have Already Been Imported
    Resource    resources.robot
    Resource    resources2.robot
    Resource    resources_imported_by_resource.robot

Re-Import Variable File
    [Template]    File Should Have Already Been Imported
    Variable    variables.py
    Variable    variables2.py
    Variable    variables_imported_by_resource.py
    Variable    dynamic_variables.py    ${SPACE}with arguments [ One arg works ]

Non-Existing Resource File
    Error in file    9    ${DATAFILE}    39
    ...    Resource file 'non_existing.robot' does not exist.

Non-Existing Variable File
    Error in file    10    ${DATAFILE}    40
    ...    Variable file 'non_existing.py' does not exist.

Empty Resource File
    ${path} =  Normalize Path  ${RESDIR}/empty_resource.robot
    Check log message    ${ERRORS}[11]
    ...    Imported resource file '${path}' is empty.    WARN

Invalid Resource Import Parameters
    Error in file    0    ${DATAFILE}    42
    ...   Setting 'Resource' accepts only one value, got 2.

Initialization file cannot be used as a resource file
    ${path} =  Normalize Path  ${DATADIR}/core/test_suite_dir_with_init_file/__init__.robot
    Error in file    12    ${DATAFILE}    43
    ...    Initialization file '${path}' cannot be imported as a resource file.
    ${path} =  Normalize Path  ${DATADIR}/core/test_suite_dir_with_init_file/sub_suite_with_init_file/__INIT__.robot
    Error in file    13    ${DATAFILE}    44
    ...    Initialization file '${path}' cannot be imported as a resource file.

Invalid Setting In Resource File
    Error in file    1    ${RESDIR}/resources.robot    8
    ...    Setting 'Test Setup' is not allowed in resource file.
    Error in file    2    ${RESDIR}/resources.robot    9
    ...    Non-existing setting 'Non Existing'.

Resource cannot contain tests
    ${path} =    Normalize Path    ${RESDIR}/resource_with_testcase_table.robot
    Error in file    3    ${RESDIR}/resources.robot    6
    ...    Error in file '${path}' on line 4:
    ...    Resource file with 'Test Cases' section is invalid.

Invalid Variable File
    ${path} =    Normalize Path    ${RESDIR}/invalid_variable_file.py
    Error in file    15    ${DATAFILE}    46
    ...    Processing variable file '${path}' failed:
    ...    Importing variable file '${path}' failed:
    ...    This is an invalid variable file
    ...    traceback=*

Resource Import Without Path
    Error in file    14    ${DATAFILE}    45
    ...    Resource setting requires value.

Variable Import Without Path
    Error in file    18    ${DATAFILE}    49
    ...    Variables setting requires value.

Resource File In PYTHONPATH
    Check Test Case    ${TEST NAME}

Variable File In PYTHONPATH
    Check Test Case    ${TEST NAME}

*** Keywords ***
Run Tests With Non-ASCII Items In PYTHONPATH
    Create Directory    %{TEMPDIR}/nön-äscïï
    Set PYTHONPATH    %{TEMPDIR}/nön-äscïï    ${PPATH_RESDIR}
    Run Tests    ${EMPTY}    ${DATAFILE}
    [Teardown]    Run Keywords
    ...    Remove Directory    %{TEMPDIR}/nön-äscïï    AND
    ...    Reset PYTHONPATH

Stderr Should Contain Error
    [Arguments]    ${path}    @{error parts}
    ${path} =    Join Path    ${DATADIR}    ${path}
    ${error} =    Catenate    @{error parts}
    Stderr Should Contain    [ ERROR ] Error in file '${path}': ${error}

File Should Have Already Been Imported
    [Arguments]    ${type}    ${path}   ${arguments}=    ${suite}=Resource And Variable Imports
    ${path} =    Join Path    ${RESDIR}    ${path}
    Syslog Should Contain    | INFO \ | ${type} file '${path}'${arguments} already imported by suite '${suite}'
