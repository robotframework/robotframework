*** Settings ***
Resource        atest_resource.txt

*** Keywords ***
Run if dependencies are available
    [arguments]    @{args}
    Make Suite Non-critical And Fail It If Screenshot dependencies are not installed
    Run Tests      @{args}

Make Suite Non-critical And Fail It If Screenshot dependencies are not installed
    ${dependencies} =     Are Screenshot dependencies available
    Run Keyword If    not ${dependencies}    Fail
    ...   This suite is made non-critical and not executed because Screenshot library's dependencies are not installed or tests are run without display.
    ...   -regression

Are Screenshot dependencies available
    ${lib} =    Normalize Path    ${ROBOT PATH}/libraries/Screenshot.py
    ${jpg} =    Normalize Path    %{TEMPDIR}/test-screenshot.jpg
    ${ppath}    ${_} =    Split Path    ${ROBOT PATH}
    ${result} =    Run Process   ${INTERPRETER}    ${lib}    test    ${jpg}    stderr=STDOUT
    ...    env:JYTHONPATH=${ppath}    env:IRONPYTHONPATH=${ppath}    shell=true
    Log    ${result.stdout}
    [teardown]    Remove File    ${jpg}
    [return]    ${result.rc == 0}
