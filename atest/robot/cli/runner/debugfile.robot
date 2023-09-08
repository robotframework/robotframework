*** Settings ***
Test Setup      Create Output Directory
Resource        cli_resource.robot

*** Variables ***
${TIMESTAMP}   20??-??-?? ??:??:??.??????

*** Test Cases ***
Debugfile
    Run Tests Without Processing Output  --outputdir=${CLI OUTDIR} --debugfile=DeBug.TXT -o o.xml  ${TESTFILE}
    Output Directory Should Contain  DeBug.TXT  o.xml
    ${content} =  Get File  ${CLI OUTDIR}${/}DeBug.TXT
    Debug file should contain    ${content}           + START SUITE: Normal
    Debug file should contain    ${content}           +- START TEST: First One
    Debug file should contain    ${content}
    ...      ${TIMESTAMP} - INFO - +-- START KEYWORD: BuiltIn.Log ? Test 1 ?
    ...      ${TIMESTAMP} - INFO - Test 1
    ...      ${TIMESTAMP} - INFO - +-- END KEYWORD: BuiltIn.Log
    Debug file should contain    ${content}
    ...      ${TIMESTAMP} - INFO - +-- START KEYWORD: BuiltIn.Log ? Logging with debug level | DEBUG ?
    ...      ${TIMESTAMP} - DEBUG - Logging with debug level
    ...      ${TIMESTAMP} - INFO - +-- END KEYWORD: BuiltIn.Log
    Debug file should contain    ${content}    + END SUITE: Normal
    Syslog Should Contain  DebugFile: DeBug.TXT
    ${path} =  Set Variable  [:.\\w /\\\\~+-]*DeBug\\.TXT
    Stdout Should Match Regexp  .*Debug: {3}${path}.*
    Syslog Should Match Regexp  .*Debug: ${path}.*

Debugfile Log Level Should Always Be Debug
    [Documentation]  --loglevel option should not affect what's written to debugfile
    Run Tests Without Processing Output  --outputdir ${CLI OUTDIR} -b debug.txt -o o.xml --loglevel WARN  ${TESTFILE}
    ${content}=     Get File     ${CLI OUTDIR}/debug.txt
    Debug file should contain    ${content}
    ...    ${TIMESTAMP} - INFO - +-- START KEYWORD: BuiltIn.Log ? Test 1 ?
    ...    ${TIMESTAMP} - INFO - Test 1
    ...    ${TIMESTAMP} - INFO - +-- END KEYWORD: BuiltIn.Log
    Debug file should contain    ${content}
    ...    ${TIMESTAMP} - INFO - +-- START KEYWORD: BuiltIn.Log ? Logging with debug level | DEBUG ?
    ...    ${TIMESTAMP} - DEBUG - Logging with debug level
    ...    ${TIMESTAMP} - INFO - +-- END KEYWORD: BuiltIn.Log

Debugfile timestamps are accurate
    Run Tests    --outputdir ${CLI OUTDIR} -b debug.txt -t LibraryAddsTimestampAsInteger
    ...    test_libraries/timestamps_for_stdout_messages.robot
    ${tc} =    Check Test Case    LibraryAddsTimestampAsInteger
    ${content} =     Get file     ${CLI OUTDIR}/debug.txt
    Debug file should contain    ${content}
    ...    ${tc.kws[0].msgs[0].timestamp} - INFO - Known timestamp
    ...    ${tc.kws[0].msgs[1].timestamp} - INFO - <b>Current</b>

Writing Non-ASCII To Debugfile
    [Documentation]    Tests also that '.txt' is appended if no extension given
    Run Tests Without Processing Output    --outputdir ${CLI OUTDIR} --debugfile debug -o o.xml    misc/non_ascii.robot
    Directory Should Contain    ${CLI OUTDIR}    debug.txt    o.xml
    Stderr Should Be Empty
    ${content} =    Get File    ${CLI OUTDIR}/debug.txt
    Debugfile should contain    ${content}    ${TIMESTAMP} - FAIL - Circle is 360°, Hyvää üötä, উৄ ৰ ৺ ট ৫ ৪ হ
    Debugfile should contain    ${content}    ${TIMESTAMP} - INFO - +- START TEST: Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо

No Debugfile
    Run Tests Without Processing Output  --outputdir ${CLI OUTDIR} --debugfile NoNe -o o.xml  ${TESTFILE}
    Directory Should Contain  ${CLI OUTDIR}  o.xml
    Syslog Should Contain  DebugFile: None

Invalid Debugfile
    Create Directory  %{TEMPDIR}/debug.txt
    Run Tests Without Processing Output  --outputdir ${CLI OUTDIR} -b %{TEMPDIR}/debug.txt  ${TESTFILE}
    Stderr Should Match Regexp  \\[ ERROR \\] Opening debug file '.*debug.txt' failed: .*
    Stdout Should Contain  2 tests, 2 passed, 0 failed

*** Keywords ***
Debugfile should contain
    [Arguments]     ${content}    @{lines}
    Should Not Be Empty    ${lines}    Invalid usage!!
    ${expected}=     Catenate   SEPARATOR=\n    @{lines}
    Should Match    ${content}    *${expected}*
