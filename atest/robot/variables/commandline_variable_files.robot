*** Settings ***
Documentation   How variables from CLI override other variables is tested in variable_priorities.robot
Suite Setup     Run Test Data
Resource        atest_resource.robot

*** Variables ***
${VARFILEDIR}  ${DATADIR}/variables/resvarfiles

*** Test Cases ***
Variables From Variable File
    Check Test Case  ${TEST NAME}

Arguments To Variable Files
    Check Test Case  ${TEST NAME}

Arguments To Variable Files Using Semicolon Separator
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH with arguments
    Check Test Case  ${TEST NAME}

Non-Existing Variable File
    Stderr Should Contain  [ ERROR ] Variable file '${VF3}' does not exist.
    Stderr Should Contain  [ ERROR ] Variable file '${VF4}' does not exist.

Too Few Arguments To Variable File
    Stderr Should Contain  [ ERROR ] Processing variable file '${VF2}' failed: TypeError: get_variables()

Too Many Arguments To Variable File
    Stderr Should Contain  [ ERROR ] Processing variable file '${VF2}' with arguments [ too | many | args ] failed: TypeError: get_variables()

Invalid Variable File
    Stderr Should Contain  [ ERROR ] Processing variable file '${VF2}' with arguments [ FAIL ] failed: ZeroDivisionError:

*** Keywords ***
Run Test Data
    ${VF1} =  Set Variable  ${VARFILEDIR}/cli_vars.py
    ${VF2} =  Set Variable  ${VARFILEDIR}/cli_vars_2.py
    ${VF3} =  Set Variable  ${VARFILEDIR}/non_existing.py
    ${VF4} =  Set Variable  non_absolute_non_existing.py
    ${options} =  Catenate
    ...  --variablefile ${VF1}
    ...  -V ${VF2}:arg
    ...  -V "${VF2}:arg2:value;with;semi;colons"
    ...  -V "${VF2};semicolon;separator"
    ...  -V "${VF2};semi:colon;separator:with:colons"
    ...  --VariableFile ${VF2}
    ...  -V ${VF2}:FAIL
    ...  -V ${VF2}:too:many:args
    ...  --variablef ${VF3}
    ...  --VARIABLEFILE ${VF4}
    ...  --VariableFile pythonpath_varfile.py
    ...  --VariableFile pythonpath_varfile.py:1:2:3
    ...  --pythonpath ${VARFILEDIR}/pythonpath_dir
    Run Tests  ${options}  variables/commandline_variable_files.robot
    ${VF2} =  Normalize Path  ${VARFILEDIR}/cli_vars_2.py
    ${VF3} =  Normalize Path  ${VARFILEDIR}/non_existing.py
    ${VF4} =  Normalize Path  non_absolute_non_existing.py
    Set Suite Variable  $VF2
    Set Suite Variable  $VF3
    Set Suite Variable  $VF4
