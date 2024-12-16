*** Settings ***
Suite Setup       Create XML and JSON outputs
Resource          rebot_resource.robot

*** Variables ***
${XML}            %{TEMPDIR}/rebot.xml
${JSON}           %{TEMPDIR}/rebot.json

*** Test Cases ***
JSON output contains same suite information as XML output
    Outputs Should Contain Same Data    ${JSON}    ${XML}

JSON output structure
    [Documentation]    JSON schema validation would be good, but it's too slow with big output files.
    ...                The following test validates a smaller suite and unit tests do schema validation as well.
    ${data} =    Evaluate    json.load(open($JSON, encoding='UTF-8'))
    Lists Should Be Equal    ${data}    ${{['generator', 'generated', 'rpa', 'suite', 'statistics', 'errors']}}
    Should Match       ${data}[generator]                     Rebot ?.* (* on *)
    Should Match       ${data}[generated]                     20??-??-??T??:??:??.??????
    Should Be Equal    ${data}[rpa]                           ${False}
    Should Be Equal    ${data}[suite][name]                   Misc
    Should Be Equal    ${data}[suite][suites][1][name]        Everything
    Should Be Equal    ${data}[statistics][total][skip]       ${3}
    Should Be Equal    ${data}[statistics][tags][4][label]    f1
    Should Be Equal    ${data}[statistics][suites][-1][id]    s1-s17
    Should Be Equal    ${data}[errors][0][level]              ERROR

JSON output schema validation
    Run Rebot Without Processing Output    --suite Everything --output %{TEMPDIR}/everything.json    ${JSON}
    Validate JSON Output    %{TEMPDIR}/everything.json

JSON input
    Run Rebot    ${EMPTY}    ${JSON}
    Outputs Should Contain Same Data    ${JSON}    ${OUTFILE}

JSON input combined
    Run Rebot    ${EMPTY}    ${XML} ${XML}
    Copy Previous Outfile    # Expected result
    Run Rebot    ${EMPTY}    ${JSON} ${XML}
    Outputs Should Contain Same Data    ${OUTFILE}    ${OUTFILE COPY}
    Run Rebot    ${EMPTY}    ${JSON} ${JSON}
    Outputs Should Contain Same Data    ${OUTFILE}    ${OUTFILE COPY}

Invalid JSON input
    Create File    ${JSON}    bad
    Run Rebot Without Processing Output    ${EMPTY}    ${JSON}
    ${json} =    Normalize Path    ${JSON}
    VAR    ${error}
    ...    Reading JSON source '${json}' failed:
    ...    Loading JSON data failed:
    ...    Invalid JSON data: *
    Stderr Should Match    [[] ERROR ] ${error}${USAGE TIP}\n

Non-existing JSON input
    Run Rebot Without Processing Output    ${EMPTY}    non_existing.json
    ${json} =    Normalize Path    ${DATADIR}/non_existing.json
    VAR    ${error}
    ...    Reading JSON source '${json}' failed:
    ...    No such file or directory
    Stderr Should Match    [[] ERROR ] ${error}${USAGE TIP}\n

*** Keywords ***
Create XML and JSON outputs
    Create Output With Robot    ${XML}    ${EMPTY}    misc
    Run Rebot Without Processing Output    --output ${JSON}    ${XML}
