*** Settings ***
Documentation   This resource file contains, or imports, all general variables and keywords used by the running side of Robot Framework acceptance tests.
Library         OperatingSystem
Library         Process
Library         Collections
Library         String
Library         TestCheckerLibrary
Library         TestHelper
Library         XML
Library         read_interpreter.py
Variables       atest_variables.py

*** Variables ***
${INTERPRETER}  Set in run_atests.py
${ROBOT}        Set in Set Variables
${REBOT}        -- ;; --
${OUTDIR}       -- ;; --
${OUTFILE}      -- ;; --
${SYSLOG FILE}  -- ;; --
${STDERR FILE}  -- ;; --
${STDOUT FILE}  -- ;; --
${SUITE}        Set in Run Helper
${ERRORS}       -- ;; --
${LIBPATH1}     ${CURDIR}${/}..${/}testresources${/}testlibs
${LIBPATH2}     ${CURDIR}${/}..${/}testresources${/}listeners
${USAGE_TIP}    \n\nTry --help for usage information.
${TESTNAME}     ${EMPTY}    # Used when not running test

*** Keywords ***
Run Robot Directly
    [Arguments]  ${opts and args}
    Set Runners
    ${output} =  Run  ${ROBOT} --outputdir %{TEMPDIR} ${opts and args}
    Log  ${output}
    [Return]  ${output}

Run Tests
    [Arguments]  ${options}  @{data list}
    ${rc} =  Run Tests Helper  ${options}  @{data list}
    Process Output  ${OUTFILE}
    [Return]  ${rc}

Run Tests Without Processing Output
    [Arguments]  ${options}  @{data list}
    ${rc} =  Run Tests Helper  ${options}  @{data list}
    [Return]  ${rc}

Run Tests Helper
    [Arguments]  ${user options}  @{data list}
    ${data string} =  Set Variables And Get Datasources  @{data list}
    ${options} =  Catenate
    ...    --ConsoleMarkers OFF    # AUTO (default) doesn't work with IronPython
    ...    ${user options}
    ...    --variable interpreter:${INTERPRETER}
    ...    --pythonpath ${LIBPATH1}
    ...    --pythonpath ${LIBPATH2}
    ${rc} =  Run Helper  ${ROBOT}  ${options}  ${data string}
    [Return]  ${rc}

Run Rebot
    [Arguments]  ${options}  @{data list}
    ${data string} =  Set Variables And Get Datasources  @{data list}
    ${rc} =  Run Helper  ${REBOT}  ${options}  ${data string}
    Process Output  ${OUTFILE}
    [Return]  ${rc}

Run Rebot Without Processing Output
    [Arguments]  ${options}  @{data list}
    ${data string} =  Set Variables And Get Datasources  @{data list}
    ${rc} =  Run Helper  ${REBOT}  ${options}  ${data string}
    [Return]  ${rc}

Run Helper
    [Arguments]  ${runner}  ${options}  ${data string}
    Remove Files  ${OUTFILE}  ${OUTDIR}/*.xml  ${OUTDIR}/*.html
    ${cmd} =  Catenate  ${runner}  --consolecolors OFF  --outputdir ${OUTDIR}  --output ${OUTFILE}  --report NONE  --log NONE
    ...  ${options}  ${data string}  1>${STDOUTFILE}  2>${STDERRFILE}
    ${rc} =  Run And Return RC  ${cmd}
    Log  <a href="file://${OUTDIR}">${OUTDIR}</a>  HTML
    Log  <a href="file://${OUTFILE}">${OUTFILE}</a>  HTML
    Log  <a href="file://${STDOUTFILE}">${STDOUTFILE}</a>  HTML
    Log  <a href="file://${STDERRFILE}">${STDERRFILE}</a>  HTML
    Log  <a href="file://${SYSLOGFILE}">${SYSLOGFILE}</a>  HTML
    [Return]  ${rc}

Set Variables And Get Datasources
    [Arguments]  @{data list}
    Set Suite Variable  $SUITE  ${NONE}
    ${name} =  Get Output Name  @{data list}
    Set Variables  ${name}
    @{data list} =  Join Paths  ${DATADIR}  @{data list}
    ${data string} =  Catenate  @{data list}
    [Return]  ${data string}

Set Variables
    [Arguments]  ${name}
    ${OUTDIR} =  Join Path  ${OUTPUTDIR}  output  ${name}
    Set Global Variable  $OUTDIR  ${OUTDIR.encode('ascii', 'ignore').replace('?', '_') .replace('*', '_')}
    Create Directory  ${OUTDIR}
    Set Suite Variable  $OUTFILE  ${OUTDIR}${/}output.xml
    Set Suite Variable  $STDOUT_FILE  ${OUTDIR}${/}stdout.txt
    Set Suite Variable  $STDERR_FILE  ${OUTDIR}${/}stderr.txt
    Set Suite Variable  $SYSLOG_FILE  ${OUTDIR}${/}syslog.txt
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${SYSLOG_FILE}
    Set Runners

Set Runners
    ${robot} =  Join Path  ${ROBOTPATH}  run.py
    Set Suite Variable  $ROBOT  ${INTERPRETER} ${robot}
    ${rebot} =  Join Path  ${ROBOTPATH}  rebot.py
    Set Suite Variable  $REBOT  ${INTERPRETER} ${rebot}

Check Test Case
    [Arguments]  ${name}=${TESTNAME}  ${status}=${NONE}  ${message}=${NONE}
    ${test} =  Get Test From Suite  ${SUITE}  ${name}
    Check Test Status  ${test}  ${status}  ${message}
    [Return]  ${test}

Check Test Suite
    [Arguments]  ${name}  ${message}  ${status}=${None}
    ${test suite} =  Get Test Suite  ${name}
    Run Keyword If  """${status}""" != "None"  Should Be Equal  ${test suite.status}  ${status}
    Should Be Equal  ${test suite.full_message}  ${message}
    [Return]  ${test suite}

Get Test Case
    [Arguments]  ${name}
    ${test} =  Get Test From Suite  ${SUITE}  ${name}
    [Return]  ${test}

Get Test Suite
    [Arguments]  ${name}
    ${suite} =  Get Suite From Suite  ${SUITE}  ${name}
    [Return]  ${suite}

Check Test Doc
    [Arguments]  ${test_name}  @{expected_doc}
    ${test} =  Check Test Case  ${test_name}
    ${expected} =  Catenate  @{expected_doc}
    Should Be Equal  ${test.doc}  ${expected}
    [Return]  ${test}

Check Test Tags
    [Arguments]  ${test_name}  @{expected_tags}
    ${test} =  Check Test Case  ${test_name}
    Should Contain Tags  ${test}  @{expected_tags}
    [Return]  ${test}

Check KW Arguments
    [Arguments]  ${kw}  @{expected args}
    Lists Should Be Equal  ${kw.args}  ${expected args}

Keyword data should be
    [Arguments]  ${kw}  ${name}  ${assign}=  ${args}=
    Should be equal  ${kw.name}  ${name}
    ${kwassign}=  Catenate  SEPARATOR=,${SPACE}  @{kw.assign}
    Should be equal  ${kwassign}  ${assign}
    ${kwargs}=  Catenate  SEPARATOR=,${SPACE}  @{kw.args}
    Should match  ${kwargs}  ${args}

Check Log Message
    [Arguments]  ${item}  ${msg}  ${level}=INFO  ${html}=${False}  ${pattern}=
    ${html} =  Set Variable If  ${html} or '${level}' == 'HTML'  ${True}  ${False}
    ${level} =  Set Variable If  '${level}' == 'HTML'  INFO  ${level}
    ${checker} =  Set Variable If  '${pattern}'  Should Match  Should Be Equal
    Run Keyword  ${checker}  ${item.message.rstrip()}  ${msg.rstrip()}  Wrong log message
    Should Be Equal  ${item.level}  ${level}  Wrong log level
    Should Be Equal  ${item.html}  ${html}  Wrong HTML status

Get Output File
    [Arguments]  ${path}
    [Documentation]  Output encoding avare helper
    ${encoding} =  Evaluate  __import__('robot').utils.encoding.OUTPUT_ENCODING
    ${encoding} =  Set Variable If  r'${path}' in [r'${STDERR FILE}',r'${STDOUT FILE}']  ${encoding}  UTF-8
    ${file} =  Log File  ${path}  ${encoding}
    [Return]  ${file}

Check File Contains
    [Arguments]  ${path}  @{expected}
    ${exp} =  Catenate  @{expected}
    ${file} =  Get Output File  ${path}
    Should Contain  ${file}  ${exp}

Check File Does Not Contain
    [Arguments]  ${path}  @{expected}
    ${exp} =  Catenate  @{expected}
    ${file} =  Get Output File  ${path}
    Should Not Contain  ${file}  ${exp}

Check File Matches Regexp
    [Arguments]  ${path}  @{expected}
    ${exp} =  Catenate  @{expected}
    ${file} =  Get Output File  ${path}
    Should Match Regexp  ${file.strip()}  ^${exp}$

Check File Contains Regexp
    [Arguments]  ${path}  @{expected}
    ${exp} =  Catenate  @{expected}
    ${file} =  Get Output File  ${path}
    Should Match Regexp  ${file.strip()}  ${exp}

File Should Be Equal To
    [Arguments]  ${path}  @{expected}
    ${content} =  Get Output File  ${path}
    ${exp} =  Catenate  @{expected}
    Should Be Equal  ${content}  ${exp}

File Should Match
    [Arguments]  ${path}  @{expected}
    ${content} =  Get Output File  ${path}
    ${exp} =  Catenate  @{expected}
    Should Match  ${content}  ${exp}

Stderr Should Be Equal To
    [Arguments]  @{expected}
    File Should Be Equal To  ${STDERR FILE}  @{expected}

Stderr Should Match
    [Arguments]  @{expected}
    File Should Match  ${STDERR FILE}  @{expected}

Stderr Should Be Empty
    ${stderr} =  Get Stderr
    Should Be Empty  ${stderr}  Errors in test execution:\n${stderr}

Check Stderr Contains
    [Arguments]  @{expected}
    Check File Contains  ${STDERR_FILE}  @{expected}

Check Stderr Does Not Contain
    [Arguments]  @{expected}
    Check File Does Not Contain  ${STDERR_FILE}  @{expected}

Check Stderr Matches Regexp
    [Arguments]  @{expected}
    Check File Matches Regexp  ${STDERR_FILE}  @{expected}

Check Stderr Contains Regexp
    [Arguments]  @{expected}
    Check File Contains Regexp  ${STDERR_FILE}  @{expected}

Check Stdout Contains
    [Arguments]  @{expected}
    Check File Contains  ${STDOUT_FILE}  @{expected}

Check Stdout Does Not Contain
    [Arguments]  @{expected}
    Check File Does Not Contain  ${STDOUT_FILE}  @{expected}

Check Stdout Matches Regexp
    [Arguments]  @{expected}
    Check File Matches Regexp  ${STDOUT_FILE}  @{expected}

Check Stdout Contains Regexp
    [Arguments]  @{expected}
    Check File Contains Regexp  ${STDOUT_FILE}  @{expected}

Get Syslog
    ${file} =  Get Output File  ${SYSLOG_FILE}
    [Return]  ${file}

Get Stderr
    ${file} =  Get Output File  ${STDERR_FILE}
    [Return]  ${file}

Get Stdout
    ${file} =  Get Output File  ${STDOUT_FILE}
    [Return]  ${file}

Check Syslog Contains
    [Arguments]  @{expected}
    Check File Contains  ${SYSLOG_FILE}  @{expected}

Check Syslog Does Not Contain
    [Arguments]  @{expected}
    Check File Does Not Contain  ${SYSLOG_FILE}  @{expected}

Check Syslog Matches Regexp
    [Arguments]  @{expected}
    Check File Matches Regexp  ${SYSLOG_FILE}  @{expected}

Check Syslog Contains Regexp
    [Arguments]  @{expected}
    Check File Contains Regexp  ${SYSLOG_FILE}  @{expected}

Check Names
    [Arguments]  ${item}  ${name}  ${longprefix}=
    Should Be Equal  ${item.name}  ${name}
    Should Be Equal  ${item.longname}  ${longprefix}${name}

Is Valid Timestamp
    [Arguments]  ${time}
    Log  ${time}
    Should Not Be Equal    ${time}    ${None}
    Should Match Regexp  ${time}  20\\d{6} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}  Not valid timestamp

Is Valid Elapsed Time
    [Arguments]  ${time}
    Log  ${time}
    Should Be True  isinstance(${time}, int) and ${time} >= 0  Not valid elapsed time

Previous test should have passed
    [Arguments]  ${name}
    Should be equal  ${PREV TEST NAME}  ${name}
    Should be equal  ${PREV TEST STATUS}  PASS

Get Stat Nodes
    [Arguments]  ${type}  ${output}=
    ${output} =  Set Variable If  "${output}"  ${output}  ${OUTFILE}
    ${nodes} =  Get Elements  ${output}  statistics/${type}/stat
    [Return]  ${nodes}

Get Tag Stat Nodes
    [Arguments]  ${output}=
    ${nodes} =  Get Stat Nodes  tag  ${output}
    [Return]  ${nodes}

Get Total Stat Nodes
    [Arguments]  ${output}=
    ${nodes} =  Get Stat Nodes  total  ${output}
    [Return]  ${nodes}

Get Suite Stat Nodes
    [Arguments]  ${output}=
    ${nodes} =  Get Stat Nodes  suite  ${output}
    [Return]  ${nodes}

Tag Statistics Should Be
    [Arguments]  ${tag}  ${pass}  ${fail}
    Log    ${tag.text}
    Should Be Equal As Integers  ${tag.attrib['pass']}  ${pass}
    Should Be Equal As Integers  ${tag.attrib['fail']}  ${fail}

Test And All Keywords Should Have Passed
    [Arguments]    ${name}=${TESTNAME}
    ${tc} =    Check Test Case    ${name}
    All Keywords Should Have Passed    ${tc}

All Keywords Should Have Passed
    [Arguments]    ${tc or kw}
    @{kws} =    Set Variable    ${tc or kw.kws}
    :FOR    ${kw}    IN    @{kws}
    \    Should Be Equal    ${kw.status}    PASS
    \    All Keywords Should Have Passed    ${kw}

Run on python 2.5 and 2.6
    [arguments]     ${kw}   @{args}
    ${interpreter} =    Get interpreter    ${OUTFILE}
    ${is 27} =   is 27    ${interpreter}
    Run keyword unless    ${is 27}    ${kw}   @{args}

Run on python 2.5
    [arguments]     ${kw}   @{args}
    ${interpreter} =    Get interpreter    ${OUTFILE}
    ${is 25} =   is 25    ${interpreter}
    Run keyword if    ${is 25}    ${kw}   @{args}

Make test non-critical if
    [Arguments]    ${condition}
    Run Keyword If    ${condition}    Remove Tags    regression

Make test non-critical on IronPython
    # This test isn't 100% safe. Should come up with better.
    Make test non-critical if    os.sep != '/' and 'ipy' in '${INTERPRETER}'

Set PYTHONPATH
    [Arguments]    @{values}
    ${value} =    Catenate    SEPARATOR=${:}    @{values}
    Run Keyword If    "${PYTHON}"        Set Environment Variable    PYTHONPATH        ${value}
    Run Keyword If    "${JYTHON}"        Set Environment Variable    JYTHONPATH        ${value}
    Run Keyword If    "${IRONPYTHON}"    Set Environment Variable    IRONPYTHONPATH    ${value}

Reset PYTHONPATH
    Run Keyword If    "${PYTHON}"        Remove Environment Variable    PYTHONPATH
    Run Keyword If    "${JYTHON}"        Remove Environment Variable    JYTHONPATH
    Run Keyword If    "${IRONPYTHON}"    Remove Environment Variable    IRONPYTHONPATH
