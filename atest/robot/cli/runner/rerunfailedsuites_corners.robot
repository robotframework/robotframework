*** Settings ***
Resource          atest_resource.robot
Suite Teardown    Remove File  ${RUN FAILED FROM}

*** Variables ***
${RUN FAILED FROM}    %{TEMPDIR}${/}run-failed-output.xml

*** Test Cases ***
Runs everything when output is set to NONE
    Run Tests  --ReRunFailedSuites NoNe  cli/runfailed/onlypassing
    File Should Exist  ${OUTFILE}
    Check Test Case    Passing

Stops on error when output contains only passing test cases
    Generate output  cli/runfailed/onlypassing
    Run Tests Without Processing Output  -S ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ] Collecting failed suites from '${RUN FAILED FROM}' failed: All suites passed.${USAGE TIP}\n

Stops on error when output contains only non-existing failing test cases
    Generate output  cli/runfailed/runfailed1.robot
    Run Tests Without Processing Output  --RERUNFAILEDSUITES ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ]  Suite 'Onlypassing'  contains no tests in suite  'Runfailed1'.${USAGE TIP}\n

Stops on error when output does not exist
    Run Tests Without Processing Output  --rerunfailedsuites nonex.xml  cli/runfailed/onlypassing
    Stderr Should Match
    ...  ? ERROR ? Collecting failed suites from 'nonex.xml' failed:
    ...  Reading XML source 'nonex.xml' failed:*${USAGE TIP}\n

Stops on error when output is invalid
    Create File  ${RUN FAILED FROM}  <xml><but not='correct'/></xml>
    Run Tests Without Processing Output  --rerunfailedsuites ${RUN FAILED FROM}  cli/runfailed/onlypassing
    Stderr Should Be Equal To
    ...  [ ERROR ] Collecting failed suites from '${RUN FAILED FROM}' failed:
    ...  Reading XML source '${RUN FAILED FROM}' failed:
    ...  Incompatible XML element 'xml'.${USAGE TIP}\n

*** Keywords ***
Generate Output
    [Arguments]  ${datafile}
    Run Tests  ${EMPTY}  ${datafile}
    Copy File  ${OUTFILE}  ${RUN FAILED FROM}
