*** Settings ***
Suite Setup       Create XML and JSON outputs
Resource          rebot_resource.robot

*** Variables ***
${XML}            %{TEMPDIR}/rebot.xml
${JSON}           %{TEMPDIR}/rebot.json

*** Test Cases ***
JSON output
    Outputs should be equal    ${JSON}    ${XML}

JSON input
    Run Rebot    ${EMPTY}    ${JSON}
    Outputs should be equal    ${JSON}    ${OUTFILE}

JSON input combined
    Run Rebot    ${EMPTY}    ${XML} ${XML}
    Copy Previous Outfile    # Expected result
    Run Rebot    ${EMPTY}    ${JSON} ${XML}
    Outputs should be equal    ${OUTFILE}    ${OUTFILE COPY}
    Run Rebot    ${EMPTY}    ${JSON} ${JSON}
    Outputs should be equal    ${OUTFILE}    ${OUTFILE COPY}

Invalid JSON input
    Create File    ${JSON}    bad
    Run Rebot Without Processing Output    ${EMPTY}    ${JSON}
    ${json} =    Normalize Path    ${JSON}
    VAR    ${error}
    ...    Reading JSON source '${json}' failed:
    ...    Loading JSON data failed:
    ...    Invalid JSON data: *
    Stderr Should Match    [[] ERROR ] ${error}${USAGE TIP}\n

*** Keywords ***
Create XML and JSON outputs
    Create Output With Robot    ${XML}    ${EMPTY}    misc
    Run Rebot Without Processing Output    --output ${JSON}    ${XML}
