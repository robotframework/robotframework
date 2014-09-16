*** Settings ***
Suite Teardown  Delete Environment Variable  ROBOT_SYSLOG_FILE
Test Setup      Create Output Directory and Set Variables
Default Tags    regression  pybot  jybot
Resource        cli_resource.robot

*** Test Cases ***
Argument File
    Create Argument File  ${ARGFILE}  --name=From Argfile_With Spaces
    ...  --metadata${SPACE*10}Meta1:From AF  -M=Meta2:Overwritten
    ...  --RunEmptySuite
    ...  ${EMPTY}  \# comment line  ${EMPTY}  \# another comment
    ...  -d ${CLI OUTDIR}  -l=none --report=none  -o${SPACE*5}output.xml
    Run Tests Without Processing Output  -M Meta1:Overwritten -A ${ARGFILE} -M Meta2:cli  ${TESTFILE}
    Process Output  ${CLI OUTDIR}/output.xml
    Should Be Equal  ${SUITE.name}  From Argfile With Spaces
    Should Be Equal as Strings  ${SUITE.metadata}  {Meta1: From AF, Meta2: cli, Something: My Value}

Two Argument Files
    Create Argument File  ${ARGFILE}  --metadata A1:Value1  --metadata A2:to be overridden
    Create Argument File  ${ARGFILE2}  --metadata A2:Value2
    Run Tests  -A ${ARGFILE} --argumentfile ${ARGFILE2}  ${TESTFILE}
    Should Be Equal  ${SUITE.metadata['A1']}  Value1
    Should Be Equal  ${SUITE.metadata['A2']}  Value2

Recursive Argument File
    Create Argument File  ${ARGFILE}  -M First:1  -M Second:overwritten  --argumentfile ${ARGFILE2}
    Create Argument File  ${ARGFILE2}  --metadata Second:2
    Run Tests  -A ${ARGFILE}  ${TESTFILE}
    Should Be Equal  ${SUITE.metadata['First']}  1
    Should Be Equal  ${SUITE.metadata['Second']}  2

Argument File with Non-ASCII Characters
    Copy File  ${DATADIR}/parsing/non_ascii_paths/test-auml-ouml.robot  %{TEMPDIR}/testäö.txt
    ${path} =  Normalize Path  %{TEMPDIR}/testäö.txt
    Create Argument File  ${ARGFILE 3}  -D äëïöüÿ  -C off  ${path}
    ${output} =  Run Robot Directly  --argumentfile ${ARGFILE 3}
    Should Not Contain  ${output.upper()}  ERROR
    Should Contain  ${output}  Testäö :: äëïöüÿ

Arguments From Stdin
    ${test dir} =  Normalize Path  ${DATADIR}/misc/
    Create Argument File Without BOM  ${ARG FILE}  --name My Name with Nön Äscii  ${test dir}${/}normal.robot
    ${output}=  Run Robot Directly  --doc from_command_line --argumentfile stdin ${test dir}${/}pass_and_fail.robot < ${ARG FILE}
    Should Contain  ${output}  Normal
    Should Contain  ${output}  Pass And Fail
    Should Contain  ${output}  My Name with N
    Should Contain  ${output}  from command line

Option And Argument File Together
    Create Argument File  ${ARGFILE}  --name My name
    Create Argument File  ${ARGFILE2}  --doc My docu
    Run Tests  --argumentfile=${ARGFILE} -A${ARGFILE2}  ${TESTFILE}
    Should Be Equal  ${SUITE.name}  My name
    Should Be Equal  ${SUITE.doc}  My docu

*** Keywords ***
Create Output Directory and Set Variables
    Create Output Directory
    Set Suite Variable  ${ARGFILE}  ${CLI OUTDIR}/arg_file_1.txt
    Set Suite Variable  ${ARGFILE 2}  ${CLI OUTDIR}/arg_file_2.txt
    Set Suite Variable  ${ARGFILE 3}  ${CLI OUTDIR}/ärg_fïlë_3.txt
    Set Environment Variable  ROBOT_SYSLOG_FILE  ${CLI OUTDIR}/syslog.txt

Create Argument File
    [Arguments]  ${path}  @{lines}
    [Documentation]  Writes also UTF8 BOM to the file to test it's ignored
    ${content} =  Catenate  SEPARATOR=\n  @{lines}
    ${bom} =  Evaluate  codecs.BOM_UTF8.decode('UTF-8')  modules=codecs
    Create File  ${path}  ${bom}${content}

Create Argument File Without BOM
    [Arguments]  ${path}  @{lines}
    ${content} =  Catenate  SEPARATOR=\n  @{lines}
    Create File  ${path}  ${content}
