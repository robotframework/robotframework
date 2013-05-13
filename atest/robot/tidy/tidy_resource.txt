*** Settings ***
Library           TidyLib.py    ${INTERPRETER}
Resource          atest_resource.txt

*** Variables ***
${DATA}           ${CURDIR}/../../testdata/tidy
${TEMP}           %{TEMPDIR}${/}tidy-test-dir
${TEMPFILE}       ${TEMP}${/}tidy-test-file.txt

*** Keywords ***
Run tidy with golden file and check result
    [Arguments]    ${options}    ${expected}
    ${output} =    Run tidy and check result    ${options}    golden.txt    expected=${expected}
    [Return]    ${output}

Run tidy with golden resource file and check result
    [Arguments]    ${options}    ${expected}
    ${output} =    Run tidy and check result    ${options}    golden_resource.txt    expected=${expected}
    [Return]    ${output}

Check file count
    [Arguments]    ${directory}    ${pattern}    ${expected}
    ${files}=    Count Files In Directory    ${directory}    ${pattern}
    Should Be Equal As Numbers    ${files}    ${expected}
