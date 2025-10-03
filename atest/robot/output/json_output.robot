*** Settings ***
Documentation     JSON output is tested in detailed level using unit tests.
Resource          atest_resource.robot

*** Variables ***
${JSON}           %{TEMPDIR}/output.json
${XML}            %{TEMPDIR}/output.xml

*** Test Cases ***
JSON output contains same suite information as XML output
    Run Tests    ${EMPTY}    misc
    Copy File    ${OUTFILE}    ${XML}
    Run Tests Without Processing Output    -o ${JSON}    misc
    Outputs Should Contain Same Data    ${JSON}    ${XML}    ignore_timestamps=True

JSON output structure
    [Documentation]    Full JSON schema validation would be good, but it's too slow with big output files.
    ...                The test after this one validates a smaller suite against a schema.
    ${data} =    Evaluate    json.load(open($JSON, encoding='UTF-8'))
    Lists Should Be Equal    ${data}    ${{['generator', 'generated', 'rpa', 'suite', 'statistics', 'errors']}}
    Should Match       ${data}[generator]                     Robot ?.* (* on *)
    Should Match       ${data}[generated]                     20??-??-??T??:??:??.??????
    Should Be Equal    ${data}[rpa]                           ${False}
    Should Be Equal    ${data}[suite][name]                   Misc
    Should Be Equal    ${data}[suite][suites][2][name]        Everything
    Should Be Equal    ${data}[statistics][total][skip]       ${3}
    Should Be Equal    ${data}[statistics][tags][4][label]    f1
    Should Be Equal    ${data}[statistics][suites][-1][id]    s1-s18
    Should Be Equal    ${data}[errors][0][level]              ERROR

JSON output matches schema
    [Tags]    require-jsonschema
    Run Tests Without Processing Output    -o OUT.JSON    misc/everything.robot
    Validate JSON Output    ${OUTDIR}/OUT.JSON

Invalid JSON output file
    ${path} =    Normalize Path    ${JSON}
    Remove File    ${path}
    Create Directory    ${path}
    Run Tests Without Processing Output    -o ${path}    misc/pass_and_fail.robot
    Stderr Should Match    [[] ERROR ] Opening output file '${path}' failed: *${USAGE TIP}\n
    [Teardown]    Remove Directory    ${JSON}
