*** Settings ***
Test Setup        Create Output Directory
Suite Teardown    Remove Files    ${ARGFILE}    ${ARGFILE 2}    ${ÄRGFÏLË}
Resource          cli_resource.robot

*** Variables ***
${ARGFILE}        %{TEMPDIR}/arg_file_1.txt
${ARGFILE 2}      %{TEMPDIR}/arg_file_2.txt
${ÄRGFÏLË}        %{TEMPDIR}/ärg_fïlë_3.txt
${BOM}            \uFEFF

*** Test Cases ***
Argument File
    Create Argument File    ${ARGFILE}
    ...    --name=From Argfile With Spaces
    ...    --metadata${SPACE*10}Meta1:From AF
    ...    -M=Meta2:Overwritten
    ...    --RunEmptySuite
    ...    ${EMPTY}
    ...    \# comment line
    ...    ${EMPTY}
    ...    \# another comment
    ...    -d ${CLI OUTDIR}
    ...    -l=none
    ...    --report=none
    ...    -o${SPACE*5}output.xml
    ${result} =    Run Tests    -M Meta1:Overwritten --argumentfile ${ARGFILE} -M Meta2:cli    ${TESTFILE}
    ...    output=${CLI OUTDIR}/output.xml
    Execution Should Have Succeeded    ${result}
    Should Be Equal    ${SUITE.name}    From Argfile With Spaces
    Should Be Equal as Strings    ${SUITE.metadata}    {Meta1: From AF, Meta2: cli, Something: My Value}

Two Argument Files
    Create Argument File    ${ARGFILE}    --metadata A1:Value1    --metadata A2:to be overridden
    Create Argument File    ${ARGFILE2}    --metadata A2:Value2
    ${result} =    Run Tests    -A ${ARGFILE} --Argument-File ${ARGFILE2}    ${TESTFILE}
    Execution Should Have Succeeded    ${result}
    Should Be Equal    ${SUITE.metadata['A1']}    Value1
    Should Be Equal    ${SUITE.metadata['A2']}    Value2

Recursive Argument File
    Create Argument File    ${ARGFILE}    -M First:1    -M Second:overwritten    --ARGUMENTFILE ${ARGFILE2}
    Create Argument File    ${ARGFILE2}    --metadata Second:2
    ${result} =    Run Tests    -A ${ARGFILE}    ${TESTFILE}
    Execution Should Have Succeeded    ${result}
    Should Be Equal    ${SUITE.metadata['First']}    1
    Should Be Equal    ${SUITE.metadata['Second']}    2

Argument File with Non-ASCII Characters
    ${path} =    Copy File    ${DATADIR}/parsing/non_ascii_paths/test-auml-ouml.robot    %{TEMPDIR}/testäö.robot
    Create Argument File    ${ÄRGFÏLË}    -D äëïöüÿ    -C off    ${path}
    ${result} =    Run Tests    --argumentfile ${ÄRGFÏLË}
    Execution Should Have Succeeded    ${result}
    Should Contain    ${result.stdout}    Testäö :: äëïöüÿ

Arguments From Stdin
    ${test dir} =    Normalize Path    ${DATADIR}/misc/
    Create Argument File Without BOM    ${ARG FILE}
    ...    --name My Name with Nön Äscii
    ...    ${test dir}${/}normal.robot
    ${cmd} =    Join Command Line
    ...    @{INTERPRETER.runner}
    ...    --output    NONE
    ...    --report    NONE
    ...    --log       NONE
    ...    --doc    from command line
    ...    --argumentfile    stdin
    ...    ${test dir}${/}pass_and_fail.robot
    ${result} =    Run Process    ${cmd} < ${ARG FILE}    shell=True
    ...    stdout=${STDOUT FILE}    stderr=${STDERR FILE}
    Execution Should Have Succeeded    ${result}    rc=1
    Should Contain    ${result.stdout}    Normal
    Should Contain    ${result.stdout}    Pass And Fail
    Should Contain    ${result.stdout}    My Name with N
    Should Contain    ${result.stdout}    from command line

Option And Argument File Together
    Create Argument File    ${ARGFILE}    --name My name
    Create Argument File    ${ARGFILE2}    --doc My docu
    ${result} =    Run Tests    --argumentfile\=${ARGFILE} -A${ARGFILE2}    ${TESTFILE}
    Execution Should Have Succeeded    ${result}
    Should Be Equal    ${SUITE.name}    My name
    Should Be Equal    ${SUITE.doc}    My docu

Shortening --argumentfile is not possible
    Create Argument File    ${ARGFILE}    --name My name
    ${result} =    Run Tests Without Processing Output    --argumentfil ${ARGFILE}    ${TESTFILE}
    Execution Should Have Failed    ${result}
    ...    Using '--argumentfile' option in shortened format like '--argumentf' is not supported.

*** Keywords ***
Create Argument File
    [Arguments]    ${path}    @{lines}
    [Documentation]    Writes also UTF8 BOM to the file to test it's ignored
    ${content} =    Catenate    SEPARATOR=\n    @{lines}
    Create File    ${path}    ${BOM}${content}

Create Argument File Without BOM
    [Arguments]    ${path}    @{lines}
    ${content} =    Catenate    SEPARATOR=\n    @{lines}
    Create File    ${path}    ${content}

Execution Should Have Succeeded
    [Arguments]    ${result}    ${rc}=0
    Should Be Equal As Integers    ${result.rc}    ${rc}
    Should Be Empty    ${result.stderr}

Execution Should Have Failed
    [Arguments]    ${result}    ${error}    ${rc}=252
    Should Be Equal As Integers    ${result.rc}    ${rc}
    Should Be Equal    ${result.stderr}    [ ERROR ] ${error}${USAGE TIP}
