*** Settings ***
Resource          atest_resource.robot
Suite Teardown    Remove File  ${RUN FAILED FROM}

*** Variables ***
${RUN FAILED FROM}    %{TEMPDIR}${/}run-failed-output.xml

*** Test Cases ***
Runs everything when output is set to NONE
    Run Tests  --ReRunFailed NoNe  cli/runfailed/onlypassing
    File Should Exist  ${OUTFILE}
    Check Test Case    Passing

Stops on error when output contains only passing test cases
    Generate output  cli/runfailed/onlypassing
    Run Tests Without Processing Output  -R ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ] Collecting failed tests from '${RUN FAILED FROM}' failed: All tests passed.${USAGE TIP}\n

Stops on error when output contains only non-existing failing test cases
    Generate output  cli/runfailed/runfailed2.robot
    Run Tests Without Processing Output  --RERUN ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ]  Suite 'Onlypassing' contains no tests named 'Runfailed2.Failing' or 'Runfailed2.Failing With Tag'.${USAGE TIP}\n

Stops on error when output does not exist
    Run Tests Without Processing Output  --rerunfailed nonex.xml  cli/runfailed/onlypassing
    Stderr Should Match
    ...  [ ERROR ] Collecting failed tests from 'nonex.xml' failed:
    ...  Reading XML source 'nonex.xml' failed:
    ...  No such file*${USAGE TIP}\n

Stops on error when output is invalid
    Create File  ${RUN FAILED FROM}  <xml><but not='correct'/></xml>
    Run Tests Without Processing Output  --rerunfailed ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ] Collecting failed tests from '${RUN FAILED FROM}' failed:
    ...  Reading XML source '${RUN FAILED FROM}' failed:
    ...  Incompatible XML element 'xml'.${USAGE TIP}\n

*** Keywords ***
Generate Output
    [Arguments]  ${datafile}
    Run Tests  ${EMPTY}  ${datafile}
    Copy File  ${OUTFILE}  ${RUN FAILED FROM}
