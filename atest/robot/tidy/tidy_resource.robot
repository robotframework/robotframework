*** Settings ***
Library           TidyLib.py    ${INTERPRETER}
Resource          atest_resource.robot

*** Variables ***
${DATA}           ${CURDIR}/../../testdata/tidy
${TEMP}           %{TEMPDIR}${/}tidy-test-dir
${OUTFILE}        ${TEMP}${/}tidy-test-file.robot

*** Keywords ***
Run tidy with golden file and check result
    [Arguments]    ${options}    ${expected}    ${input}=golden-input.robot
    ${output} =    Run tidy and check result    ${options}    ${input}    expected=${expected}
    [Return]    ${output}

Run tidy with golden resource file and check result
    [Arguments]    ${options}    ${expected}
    ${output} =    Run tidy and check result    ${options}    golden_resource.robot    expected=${expected}
    [Return]    ${output}

Check file count
    [Arguments]    ${directory}    ${pattern}    ${expected}
    ${files}=    Count Files In Directory    ${directory}    ${pattern}
    Should Be Equal As Numbers    ${files}    ${expected}

Check file counts
    [Arguments]    ${robot}=0    ${txt}=0    ${html}=0    ${tsv}=0
    Check file count    ${TEMP}    *.robot    ${robot}
    Check file count    ${TEMP}    *.txt      ${txt}
    Check file count    ${TEMP}    *.html     ${html}
    Check file count    ${TEMP}    *.tsv      ${tsv}
