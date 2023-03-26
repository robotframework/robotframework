*** Settings ***
Test Template      TestDoc Run Should Fail
Resource           testdoc_resource.robot

*** Test Cases ***
Invalid usage
    Expected at least 2 arguments, got 1.

Non-existing input
    Parsing '${EXECDIR}${/}nonex.robot' failed: File or directory to execute does not exist.
    ...    nonex.robot

Invalid input
    Suite 'Testdoc Resource' contains no tests or tasks.
    ...    ${CURDIR}/testdoc_resource.robot

Invalid output
    [Setup]    Create Directory    ${OUTFILE}
    Opening Testdoc output file '*[/\\]testdoc-output.html' failed: *Error: *
    ...    ${INPUT 1}    remove_outfile=False
    [Teardown]    Remove Directory    ${OUTFILE}
