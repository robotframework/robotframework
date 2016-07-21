*** Settings ***
Suite Setup     Run Tests With Non-ASCII Items In PYTHONPATH
Resource        atest_resource.robot

*** Variables ***
${DATAFILE}      core/resource_and_variable_imports.robot
${RESDIR}        ${DATADIR}/core/resources_and_variables
${PPATH_RESDIR}  ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Normal Resource Import
    [Documentation]  Test that path given in resource import is relative to the current
    ...  directory and that '/' is converted to correct path separator depending on os.
    Check Test Case  ${TEST NAME}

Resource Import With Variables
    [Documentation]  Test that variables can be used in resource import path.
    ...  Also test that path can be absolute.
    Check Test Case  ${TEST NAME}

Normal Variable Import
    [Documentation]  Test that path given in variable import is relative to the current
    ...  directory and that '/' is converted to correct path separator depending on os.
    Check Test Case  ${TEST NAME}

Not Included In __all__
    Check Test Case  ${TEST NAME}

Variable Import With Variables
    [Documentation]  Test that variables can be used in variable import path.
    ...  Also test that path can be absolute.
    Check Test Case  ${TEST NAME}

Invalid List Variable
    [Documentation]  List variable not containing a list value causes an error
    Check Test Case  ${TEST NAME}
    ${path} =  Normalize Path  ${RESDIR}/invalid_list_variable.py
    Stderr Should Contain Error    ${DATAFILE}
    ...  Processing variable file '${path}' failed:
    ...  Invalid variable '\@{invalid_list}': Expected list-like value, got string.

Dynamic Variable File
    [Documentation]  Test for getting variables dynamically from a variable file
    ...  using get_variables or getVariables and arguments.
    Check Test Case  ${TEST NAME} With No Args
    Check Test Case  ${TEST NAME} With One Arg

Dynamic Variable File With Variables And Backslashes In Args
    Check Test Case  ${TEST NAME}

Invalid Arguments To Dynamic Variable File
    ${path} =  Normalize Path  ${RESDIR}/dynamic_variables.py
    Stderr Should Contain Error    ${DATAFILE}
    ...  Processing variable file '${path}' with arguments [ Two args | returns invalid ] failed:
    ...  Expected 'get_variables' to return dict-like value, got None.
    Stderr Should Contain Error    ${DATAFILE}
    ...  Processing variable file '${path}' with arguments [ More | args | raises | exception ] failed:
    ...  Invalid arguments for get_variables

Non-Existing Variable In Arguments To Dynamic Variable File
    ${path} =  Normalize Path  ${RESDIR}/dynamicVariables.py
    Stderr Should Contain Error    ${DATAFILE}
    ...  Replacing variables from setting 'Variables' failed:
    ...  Variable '\${non_existing_var_as_arg}' not found.

Resource Importing Resources
    [Documentation]  Test that resource file can import more resources.
    Check Test Case  ${TEST NAME}

Resource Importing Variables
    [Documentation]  Test that resource file can import variables
    Check Test Case  ${TEST NAME}

Resource Importing Library
    [Documentation]  Test that resource file can import libraries
    Check Test Case  ${TEST NAME}

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
    Variable    dynamic_variables.py   ${SPACE}with arguments [ One arg works ]

Non-Existing Resource File
    Stderr Should Contain Error    ${DATAFILE}
    ...  Resource file 'non_existing.robot' does not exist

Non-Existing Variable File
    Stderr Should Contain Error    ${DATAFILE}
    ...  Variable file 'non_existing.py' does not exist

Empty Resource File
    ${path} =  Normalize Path  ${RESDIR}/empty_resource.robot
    Check Stderr Contains  [ WARN ] Imported resource file '${path}' is empty

Invalid Resource Import Parameters
    Stderr Should Contain Error    ${DATAFILE}
    ...  Resource file 'resources_and_variables${/}resources.robot only one parameter allowed' does not exist

Initialization file cannot be used as a resource file
    ${path} =  Normalize Path  ${DATADIR}/core/test_suite_dir_with_init_file/__init__.robot
    Stderr Should Contain Error    ${DATAFILE}
        ...  Initialization file '${path}' cannot be imported as a resource file.
    ${path} =  Normalize Path  ${DATADIR}/core/test_suite_dir_with_init_file/sub_suite_with_init_file/__INIT__.robot
    Stderr Should Contain Error    ${DATAFILE}
        ...  Initialization file '${path}' cannot be imported as a resource file.

Invalid Setting In Resource File
    Stderr Should Contain Error    ${RESDIR}/resources.robot
    ...  Non-existing setting 'Test Setup'.
    Stderr Should Contain Error    ${RESDIR}/resources.robot
    ...  Non-existing setting 'Non Existing'.
    ${invres} =  Normalize Path  ${RESDIR}/resource_with_testcase_table.robot
    Stderr Should Contain Error    ${RESDIR}/resources.robot
    ...  Resource file '${invres}' contains a test case table which is not allowed.
    Check Stderr Does Not Contain  AttributeError:

Invalid Variable File
    ${path} =  Normalize Path  ${RESDIR}/invalid_variable_file.py
    Stderr Should Contain Error    ${DATAFILE}
    ...    Processing variable file '${path}' failed:
    ...    Importing variable file '${path}' failed:
    ...    This is an invalid variable file

Resource Import Without Path
    Stderr Should Contain Error    ${DATAFILE}
    ...    Resource setting requires a name

Variable Import Without Path
    Stderr Should Contain Error    ${DATAFILE}
    ...    Variables setting requires a name

Resource File In PYTHONPATH
    Check Test Case  ${TEST NAME}

Variable File In PYTHONPATH
    Check Test Case  ${TEST NAME}

*** Keywords ***
Run Tests With Non-ASCII Items In PYTHONPATH
    Create Directory    %{TEMPDIR}/nön-äscïï
    Set PYTHONPATH    %{TEMPDIR}/nön-äscïï    ${PPATH_RESDIR}
    Run Tests  ${EMPTY}  ${DATAFILE}
    [Teardown]  Run Keywords
    ...    Remove Directory  %{TEMPDIR}/nön-äscïï    AND
    ...    Reset PYTHONPATH

Stderr Should Contain Error
    [Arguments]    ${path}    @{error parts}
    ${path} =  Join Path    ${DATADIR}    ${path}
    ${error} =  Catenate  @{error parts}
    Check Stderr Contains    [ ERROR ] Error in file '${path}': ${error}

File Should Have Already Been Imported
    [Arguments]    ${type}    ${path}   ${arguments}=    ${suite}=Resource And Variable Imports
    ${path} =  Join Path    ${RESDIR}    ${path}
    Check Syslog Contains  | INFO \ | ${type} file '${path}'${arguments} already imported by suite '${suite}'
