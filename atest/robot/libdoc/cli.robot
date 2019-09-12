*** Settings ***
Resource         libdoc_resource.robot
Test Template    Run Libdoc And Verify Created Output File

*** Test Cases ***
Default format is got from output file extension
    String ${OUTHTML}    HTML    String
    String ${OUTXML}     XML     String    path=${OUTXML}

Using --format overrides output file extension
    -f XmL ${TESTDATADIR}/resource.robot ${OUTHTML}    XML         resource
    --format hTmL BuiltIn ${OUTPREFIX}.xxx             HTML        BuiltIn     path=${OUTPREFIX}.xxx
    --format XML:HTML String ${OUTXML}                 XML:HTML    String      path=${OUTXML}

Override name and version
    --name MyName --version 42 String ${OUTHTML}    HTML    MyName    42
    -n MyName -v 42 -f xml BuiltIn ${OUTHTML}       XML     MyName    42

Relative path with Python libraries
    [Template]    NONE
    ${dir in libdoc exec dir}=    Set Variable     ${ROBOTPATH}/../TempDirInExecDir
    Directory Should Not Exist    ${dir in libdoc exec dir}
    Create Directory    ${dir in libdoc exec dir}
    Create File    ${dir in libdoc exec dir}/MyLibrary.py    def my_keyword(): pass
    Run Libdoc And Parse Output    ${dir in libdoc exec dir}/MyLibrary.py
    Name Should Be    MyLibrary
    Keyword Name Should Be    0    My Keyword
    [Teardown]    Remove Directory    ${dir in libdoc exec dir}    recursively

*** Keywords ***
Run Libdoc And Verify Created Output File
    [Arguments]    ${args}   ${format}    ${name}    ${version}=    ${path}=${OUTHTML}
    ${stdout} =    Run Libdoc    ${args}
    Run Keyword    ${format} Doc Should Have Been Created    ${path}    ${name}    ${version}
    File Should Have Correct Line Separators    ${path}
    Path to output should be in stdout    ${path}    ${stdout.rstrip()}
    [Teardown]    Remove Output Files

HTML Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}
    ${libdoc}=    Get File    ${path}
    Should Start With    ${libdoc}    <!DOCTYPE
    Should Contain    ${libdoc}    ${name}
    Should Contain    ${libdoc}    ${version}

XML Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}
    ${libdoc}=           Parse Xml    ${path}
    Set Test Variable    ${libdoc}
    Name Should Be       ${name}
    Run Keyword If       "${version}"    Version Should Match    ${version}

XML:HTML Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}
    ${libdoc}=           Parse Xml    ${path}
    Set Test Variable    ${libdoc}
    Name Should Be       ${name}
    Format Should Be     HTML
    Run Keyword If       "${version}"    Version Should Match    ${version}

Path to output should be in stdout
    [Documentation]    Printed path may be in different format than original.
    ...                IronPython seems to like 'c:\olddos~1\format~2.ext'.
    [Arguments]    ${path}    ${stdout}
    File Should Exist    ${stdout}
    Remove File    ${path}
    File Should Not Exist    ${stdout}
