*** Settings ***
Documentation     General variables and keywords used by the execution side of
...               Robot Framework acceptance tests.
Library           OperatingSystem
Library           Process
Library           Collections
Library           String
Library           TestCheckerLibrary
Library           TestHelper           # Combine with TestCheckerLibrary?
Library           XML
Variables         atest_variables.py

*** Variables ***
${OUTDIR}         %{TEMPDIR}${/}output
${OUTFILE}        ${OUTDIR}${/}output.xml
${SET SYSLOG}     True
${SYSLOG FILE}    ${OUTDIR}${/}syslog.txt
${SYSLOG LEVEL}   INFO
${STDOUT FILE}    ${OUTDIR}${/}stdout.txt
${STDERR FILE}    ${OUTDIR}${/}stderr.txt
${OUTFILE COPY}   %{TEMPDIR}${/}output-copy.xml
${SUITE}          Set by TestCheckerLibrary.Process Output
${ERRORS}         -- ;; --
${USAGE TIP}      \n\nTry --help for usage information.
${TESTNAME}       ${EMPTY}    # Used when not running test
${COMMON DEFAULTS}
...               --ConsoleColors OFF
...               --output ${OUTFILE}
...               --report NONE
...               --log NONE
${RUNNER DEFAULTS}
...               ${COMMON DEFAULTS}
...               --ConsoleMarkers OFF
...               --PYTHONPATH "${CURDIR}${/}..${/}testresources${/}testlibs"
...               --PYTHONPATH "${CURDIR}${/}..${/}testresources${/}listeners"

*** Keywords ***
Run Tests
    [Arguments]    ${options}=    ${sources}=    ${default options}=${RUNNER DEFAULTS}    ${output}=${OUTFILE}    ${validate output}=None
    [Documentation]    *OUTDIR:* file://${OUTDIR} (regenerated for every run)
    ${result} =    Execute    ${INTERPRETER.runner}   ${options}    ${sources}    ${default options}
    Log Many    RC: ${result.rc}    STDERR:\n${result.stderr}    STDOUT:\n${result.stdout}
    Process Output    ${output}    validate=${validate output}
    RETURN    ${result}

Run Tests Without Processing Output
    [Arguments]    ${options}=    ${sources}=    ${default options}=${RUNNER DEFAULTS}
    [Documentation]    *OUTDIR:* file://${OUTDIR} (regenerated for every run)
    ${result} =    Execute    ${INTERPRETER.runner}   ${options}    ${sources}    ${default options}
    Log Many    RC: ${result.rc}    STDERR:\n${result.stderr}    STDOUT:\n${result.stdout}
    RETURN    ${result}

Run Rebot
    [Arguments]    ${options}=    ${sources}=    ${default options}=${COMMON DEFAULTS}    ${output}=${OUTFILE}    ${validate output}=None
    [Documentation]    *OUTDIR:* file://${OUTDIR} (regenerated for every run)
    ${result} =    Execute    ${INTERPRETER.rebot}   ${options}    ${sources}    ${default options}
    Log Many    RC: ${result.rc}    STDERR:\n${result.stderr}    STDOUT:\n${result.stdout}
    Process Output    ${output}    validate=${validate output}
    RETURN    ${result}

Run Rebot Without Processing Output
    [Arguments]    ${options}=    ${sources}=    ${default options}=${COMMON DEFAULTS}
    [Documentation]    *OUTDIR:* file://${OUTDIR} (regenerated for every run)
    ${result} =    Execute    ${INTERPRETER.rebot}   ${options}    ${sources}    ${default options}
    Log Many    RC: ${result.rc}    STDERR:\n${result.stderr}    STDOUT:\n${result.stdout}
    RETURN    ${result}

Execute
    [Arguments]    ${executor}    ${options}    ${sources}    ${default options}=
    Set Execution Environment
    @{arguments} =    Get Execution Arguments    ${options}    ${sources}    ${default options}
    ${result} =    Run Process    @{executor}    @{arguments}
    ...    stdout=${STDOUTFILE}    stderr=${STDERRFILE}    output_encoding=SYSTEM
    ...    timeout=5min    on_timeout=terminate
    RETURN    ${result}

Get Execution Arguments
    [Arguments]    ${options}    ${sources}    ${default options}
    @{options} =    Split command line    --outputdir ${OUTDIR} ${default options} ${options}
    @{sources} =    Split command line    ${sources}
    @{sources} =    Join Paths    ${DATADIR}    @{sources}
    RETURN    @{options}    @{sources}

Set Execution Environment
    Remove Directory    ${OUTDIR}    recursive
    Create Directory    ${OUTDIR}
    IF    ${SET SYSLOG}
        Set Environment Variable    ROBOT_SYSLOG_FILE    ${SYSLOG FILE}
        Set Environment Variable    ROBOT_SYSLOG_LEVEL    ${SYSLOG LEVEL}
    END

Copy Previous Outfile
    Copy File    ${OUTFILE}    ${OUTFILE COPY}

Check Test Suite
    [Arguments]    ${name}    ${message}    ${status}=${None}
    ${suite} =    Get Test Suite    ${name}
    IF    $status is not None
    ...    Should Be Equal    ${suite.status}    ${status}
    Should Be Equal    ${suite.full_message}    ${message}
    RETURN    ${suite}

Check Test Doc
    [Arguments]    ${name}    @{expected}
    ${tc} =    Check Test Case    ${name}
    ${expected} =    Catenate    @{expected}
    Should Be Equal    ${tc.doc}    ${expected}
    RETURN    ${tc}

Check Test Tags
    [Arguments]    ${name}    @{expected}
    ${tc} =    Check Test Case    ${name}
    Should Contain Tags    ${tc}    @{expected}
    RETURN    ${tc}

Check Keyword Data
    [Arguments]    ${kw}    ${name}    ${assign}=    ${args}=    ${status}=PASS    ${tags}=    ${doc}=*    ${type}=KEYWORD
    Should Be Equal    ${kw.full_name}               ${name}
    Should Be Equal    ${{', '.join($kw.assign)}}    ${assign}
    Should Be Equal    ${{', '.join($kw.args)}}      ${args}
    Should Be Equal    ${kw.status}                  ${status}
    Should Be Equal    ${{', '.join($kw.tags)}}      ${tags}
    Should Match       ${kw.doc}                     ${doc}
    Should Be Equal    ${kw.type}                    ${type}

Check TRY Data
    [Arguments]    ${try}    ${patterns}=    ${pattern_type}=${None}    ${assign}=${None}    ${status}=PASS
    Should Be Equal    ${try.type}                      TRY
    Should Be Equal    ${{', '.join($try.patterns)}}    ${patterns}
    Should Be Equal    ${try.pattern_type}              ${pattern_type}
    Should Be Equal    ${try.assign}                    ${assign}
    Should Be Equal    ${try.status}                    ${status}

Test And All Keywords Should Have Passed
    [Arguments]    ${name}=${TESTNAME}    ${allow not run}=False    ${allowed failure}=
    ${tc} =    Check Test Case    ${name}
    All Keywords Should Have Passed    ${tc}    ${allow not run}    ${allowed failure}

All Keywords Should Have Passed
    [Arguments]    ${tc_or_kw}    ${allow not run}=False    ${allowed failure}=
    FOR    ${index}    ${item}    IN ENUMERATE    @{tc_or_kw.body.filter(messages=False)}
        IF    $item.failed and not ($item.message == $allowed_failure)
            Fail    ${item.type} failed: ${item.message}
        ELSE IF    $item.not_run and not $allow_not_run
            Fail    ${item.type} was not run.
        ELSE IF    $item.skipped
            Fail    ${item.type} was skipped.
        ELSE IF    $item.passed and $item.message
            Fail    ${item.type} has unexpected message: ${item.message}
        END
        All Keywords Should Have Passed    ${item}    ${allow not run}    ${allowed failure}
    END

Get Output File
    [Arguments]    ${path}
    [Documentation]    Output encoding avare helper
    ${encoding} =    Set Variable If    r'${path}' in [r'${STDERR FILE}', r'${STDOUT FILE}']    SYSTEM    UTF-8
    ${file} =    Get File    ${path}    ${encoding}
    RETURN    ${file}

File Should Contain
    [Arguments]    ${path}    @{expected}    ${count}=None
    ${exp} =    Catenate    @{expected}
    ${file} =    Get Output File    ${path}
    IF    not ${count}
        Should Contain    ${file}    ${exp}
    ELSE
        Should Contain X Times    ${file}    ${exp}    ${count}
    END

File Should Not Contain
    [Arguments]    ${path}    @{expected}
    ${exp} =    Catenate    @{expected}
    ${file} =    Get Output File    ${path}
    Should Not Contain    ${file}    ${exp}

File Should Match Regexp
    [Arguments]    ${path}    @{expected}
    ${exp} =    Catenate    @{expected}
    ${file} =    Get Output File    ${path}
    Should Match Regexp    ${file.strip()}    (?s)^${exp}$

File Should Contain Regexp
    [Arguments]    ${path}    @{expected}
    ${exp} =    Catenate    @{expected}
    ${file} =    Get Output File    ${path}
    Should Match Regexp    ${file.strip()}    ${exp}

File Should Not Contain Regexp
    [Arguments]    ${path}    @{expected}
    ${exp} =    Catenate    @{expected}
    ${file} =    Get Output File    ${path}
    Should Not Match Regexp    ${file.strip()}    ${exp}

File Should Be Equal To
    [Arguments]    ${path}    @{expected}
    ${content} =    Get Output File    ${path}
    ${exp} =    Catenate    @{expected}
    Should Be Equal    ${content}    ${exp}

File Should Match
    [Arguments]    ${path}    @{expected}
    ${content} =    Get Output File    ${path}
    ${exp} =    Catenate    @{expected}
    Should Match    ${content}    ${exp}

File Should Contain Match
    [Arguments]    ${path}    @{expected}
    ${content} =    Get Output File    ${path}
    ${exp} =    Catenate    @{expected}
    Should Match    ${content}    *${exp}*

File Should Start With
    [Arguments]    ${path}    @{expected}
    ${content} =    Get Output File    ${path}
    ${exp} =    Catenate    @{expected}
    Should Start With    ${content}    ${exp}

Stderr Should Be Equal To
    [Arguments]    @{expected}
    File Should Be Equal To    ${STDERR FILE}    @{expected}

Stderr Should Start With
    [Arguments]    @{expected}
    File Should Start With    ${STDERR FILE}    @{expected}

Stderr Should Match
    [Arguments]    @{expected}
    File Should Match    ${STDERR FILE}    @{expected}

Stderr Should Be Empty
    ${stderr} =    Get Stderr
    Should Be Empty    ${stderr}    Errors in test execution:\n${stderr}

Stderr Should Contain
    [Arguments]    @{expected}    ${count}=None
    File Should Contain    ${STDERR_FILE}    @{expected}    count=${count}

Stderr Should Not Contain
    [Arguments]    @{expected}
    File Should Not Contain    ${STDERR_FILE}    @{expected}

Stderr Should Match Regexp
    [Arguments]    @{expected}
    File Should Match Regexp    ${STDERR_FILE}    @{expected}

Stderr Should Contain Regexp
    [Arguments]    @{expected}
    File Should Contain Regexp    ${STDERR_FILE}    @{expected}

Stdout Should Contain
    [Arguments]    @{expected}    ${count}=None
    File Should Contain    ${STDOUT_FILE}    @{expected}    count=${count}

Stdout Should Not Contain
    [Arguments]    @{expected}
    File Should Not Contain    ${STDOUT_FILE}    @{expected}

Stdout Should Match Regexp
    [Arguments]    @{expected}
    File Should Match Regexp    ${STDOUT_FILE}    @{expected}

Stdout Should Contain Regexp
    [Arguments]    @{expected}
    File Should Contain Regexp    ${STDOUT_FILE}    @{expected}

Get Syslog
    ${file} =    Get Output File    ${SYSLOG_FILE}
    RETURN    ${file}

Get Stderr
    ${file} =    Get Output File    ${STDERR_FILE}
    RETURN    ${file}

Get Stdout
    ${file} =    Get Output File    ${STDOUT_FILE}
    RETURN    ${file}

Syslog Should Contain Match
    [Arguments]    @{expected}
    File Should Contain Match    ${SYSLOG FILE}    @{expected}

Syslog Should Contain
    [Arguments]    @{expected}
    File Should Contain    ${SYSLOG_FILE}    @{expected}

Syslog Should Not Contain
    [Arguments]    @{expected}
    File Should Not Contain    ${SYSLOG_FILE}    @{expected}

Syslog Should Match Regexp
    [Arguments]    @{expected}
    File Should Match Regexp    ${SYSLOG_FILE}    @{expected}

Syslog Should Contain Regexp
    [Arguments]    @{expected}
    File Should Contain Regexp    ${SYSLOG_FILE}    @{expected}

Syslog Should Not Contain Regexp
    [Arguments]    @{expected}
    File Should Not Contain Regexp    ${SYSLOG FILE}    @{expected}

Check Names
    [Arguments]    ${item}    ${name}    ${longprefix}=
    Should Be Equal    ${item.name}    ${name}
    Should Be Equal    ${item.longname}    ${longprefix}${name}

Timestamp Should Be Valid
    [Arguments]    ${timestamp}
    Should Be True    isinstance($timestamp, datetime.datetime) and $timestamp.year > 2000

Timestamp Should Be
    [Arguments]    ${timestamp}    ${expected}
    IF    $expected is not None
        ${expected} =    Evaluate    datetime.datetime.fromisoformat('${expected}')
    END
    Should Be Equal    ${timestamp}    ${expected}

Elapsed Time Should Be Valid
    [Arguments]    ${elapsed}    ${minimum}=0    ${maximum}=${{sys.maxsize}}
    Should Be True    isinstance($elapsed, datetime.timedelta)
    Should Be True    $elapsed.total_seconds() >= ${minimum}
    Should Be True    $elapsed.total_seconds() <= ${maximum}

Elapsed Time Should Be
    [Arguments]    ${elapsed}    ${expected}
    IF    isinstance($expected, str)
        ${expected} =    Evaluate    ${expected}
    END
    Should Be Equal As Numbers    ${elapsed.total_seconds()}    ${expected}

Times Should Be
    [Arguments]    ${item}    ${start}    ${end}    ${elapsed}
    Timestamp Should Be       ${item.start_time}      ${start}
    Timestamp Should Be       ${item.end_time}        ${end}
    Elapsed Time Should Be    ${item.elapsed_time}    ${elapsed}

Previous test should have passed
    [Arguments]    ${name}
    Should be equal    ${PREV TEST NAME}    ${name}
    Should be equal    ${PREV TEST STATUS}    PASS

Get Stat Nodes
    [Arguments]    ${type}    ${output}=${OUTFILE}
    ${nodes} =    Get Elements    ${output}    statistics/${type}/stat
    RETURN    ${nodes}

Get Tag Stat Nodes
    [Arguments]    ${output}=${OUTFILE}
    ${nodes} =    Get Stat Nodes    tag    ${output}
    RETURN    ${nodes}

Get Total Stat Nodes
    [Arguments]    ${output}=${OUTFILE}
    ${nodes} =    Get Stat Nodes    total    ${output}
    RETURN    ${nodes}

Get Suite Stat Nodes
    [Arguments]    ${output}=${OUTFILE}
    ${nodes} =    Get Stat Nodes    suite    ${output}
    RETURN    ${nodes}

Tag Statistics Should Be
    [Arguments]    ${tag}    ${pass}    ${fail}
    Log    ${tag.text}
    Should Be Equal As Integers    ${tag.attrib['pass']}    ${pass}
    Should Be Equal As Integers    ${tag.attrib['fail']}    ${fail}

Set PYTHONPATH
    [Arguments]    @{values}
    ${value} =    Catenate    SEPARATOR=${:}    @{values}
    Set Environment Variable    PYTHONPATH    ${value}

Reset PYTHONPATH
    Remove Environment Variable    PYTHONPATH

Error in file
    [Arguments]    ${index}    ${path}    ${lineno}    @{message}    ${traceback}=
    ...    ${stacktrace}=    ${pattern}=True    ${level}=ERROR
    ${path} =    Join Path    ${DATADIR}    ${path}
    ${message} =    Catenate    @{message}
    ${error} =    Set Variable    Error in file '${path}' on line ${lineno}: ${message}
    ${error} =    Set Variable If    $traceback and not $stacktrace
    ...    ${error}\nTraceback (most recent call last):\n*${traceback}*
    ...    ${error}
    ${error} =    Set Variable If    $stacktrace
    ...    ${error}\n*${stacktrace}*
    ...    ${error}
    Check Log Message    ${ERRORS}[${index}]    ${error}    level=${level}    pattern=${pattern}

Error in library
    [Arguments]    ${name}    @{message}    ${pattern}=False    ${index}=0
    ${error} =    Catenate
    ...    Error in library '${name}':
    ...    @{message}
    Check Log Message    ${ERRORS}[${index}]    ${error}    level=ERROR    pattern=${pattern}

Setup Should Not Be Defined
    [Arguments]    ${model_object}
    Should Not Be True     ${model_object.setup}

Teardown Should Not Be Defined
    [Arguments]    ${model_object}
    Should Not Be True     ${model_object.teardown}

Traceback Should Be
    [Arguments]    ${msg}    @{entries}    ${error}
    ${exp} =    Set Variable    Traceback (most recent call last):
    FOR    ${path}    ${func}    ${text}    IN    @{entries}
        ${path} =    Normalize Path    ${DATADIR}/${path}
        ${exp} =    Set Variable    ${exp}\n${SPACE*2}File "${path}", line *, in ${func}\n${SPACE*4}${text}
    END
    Check Log Message    ${msg}    ${exp}\n${error}    DEBUG    pattern=True    traceback=True
