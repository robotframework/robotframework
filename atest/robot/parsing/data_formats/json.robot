*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One JSON
    Run sample file and check tests    ${EMPTY}    ${JSON DIR}/sample.rbt

JSON With JSON Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Invalid JSON Resource
    Previous Run Should Have Been Successful
    ${path} =    Normalize Path    atest/testdata/parsing/data_formats/json/sample.rbt
    ${inva} =    Normalize Path    ${JSON DIR}/_invalid.json
    Check Log Message    ${ERRORS}[0]
    ...    Error in file '${path}' on line 12: Parsing JSON resource file '${inva}' failed: Loading JSON data failed: Invalid JSON data: *
    ...    level=ERROR    pattern=True

Invalid JSON Suite
    ${result} =    Run Tests    ${EMPTY}    ${JSON DIR}/_invalid.json    output=None
    Should Be Equal As Integers    ${result.rc}    252
    ${path} =    Normalize Path    ${JSON DIR}/_invalid.json
    Should Start With    ${result.stderr}
    ...    [ ERROR ] Parsing '${path}' failed: Loading JSON data failed: Invalid JSON data:

JSON Directory
    Run Suite Dir And Check Results    -F json:rbt    ${JSON DIR}

Directory With JSON Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
