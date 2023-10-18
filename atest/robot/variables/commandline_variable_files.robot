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

Argument Conversion
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH with arguments
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH as module
    Check Test Case  ${TEST NAME}

Variable File From PYTHONPATH as submodule
    Check Test Case  ${TEST NAME}

Too Few Arguments To Variable File
    Check Log Message    ${ERRORS}[0]    Processing variable file '${VF2}' failed: Variable file expected 1 to 3 arguments, got 0.    level=ERROR

Too Many Arguments To Variable File
    Check Log Message    ${ERRORS}[2]    Processing variable file '${VF2}' with arguments ['too', 'many', 'args', 'here', 'we', 'have'] failed: Variable file expected 1 to 3 arguments, got 6.    level=ERROR

Invalid Arguments To Variable File
    Check Log Message    ${ERRORS}[3]    Processing variable file '${VF2}' with arguments ['ok', 'ok', 'not number'] failed: ValueError: Argument 'conversion' got value 'not number' that cannot be converted to integer.    level=ERROR

Invalid Variable File
    Check Log Message    ${ERRORS}[1]    Processing variable file '${VF2}' with arguments [[]'FAIL'[]] failed: ZeroDivisionError: *    level=ERROR    pattern=True

Non-Existing Variable File
    Check Log Message    ${ERRORS}[4]     Variable file '${VF3}' does not exist.    level=ERROR
    Check Log Message    ${ERRORS}[5]     Variable file '${VF4}' does not exist.    level=ERROR

*** Keywords ***
Run Test Data
    ${VF1} =  Set Variable  ${VARFILEDIR}/cli_vars.py
    ${VF2} =  Set Variable  ${VARFILEDIR}/cli_vars_2.py
    ${VF3} =  Set Variable  ${VARFILEDIR}/non_existing.py
    ${VF4} =  Set Variable  non_absolute_non_existing.py
    ${options} =  Catenate
    ...  --variablefile ${VF1}
    ...  -V ${VF2}:arg:conversion=42
    ...  -V "${VF2}:arg2:value;with;semi;colons"
    ...  -V "${VF2};semicolon;separator"
    ...  -V "${VF2};semi:colon;separator:with:colons;42"
    ...  --VariableFile ${VF2}
    ...  -V ${VF2}:FAIL
    ...  -V ${VF2}:too:many:args:here:we:have
    ...  -V "${VF2}:ok:ok:not number"
    ...  --variablef ${VF3}
    ...  --VARIABLEFILE ${VF4}
    ...  --VariableFile pythonpath_varfile.py
    ...  --VariableFile pythonpath_varfile.py:1:2:3
    ...  --VariableFile pythonpath_varfile:as:module
    ...  -V package.submodule
    ...  --pythonpath ${VARFILEDIR}/pythonpath_dir
    Run Tests  ${options}  variables/commandline_variable_files.robot
    ${VF2} =  Normalize Path  ${VARFILEDIR}/cli_vars_2.py
    ${VF3} =  Normalize Path  ${VARFILEDIR}/non_existing.py
    ${VF4} =  Normalize Path  non_absolute_non_existing.py
    Set Suite Variable  $VF2
    Set Suite Variable  $VF3
    Set Suite Variable  $VF4
