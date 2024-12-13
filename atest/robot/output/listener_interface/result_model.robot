*** Settings ***
Suite Setup       Run Tests    --listener "${LISTENER DIR}/ResultModel.py;${MODEL FILE}" --loglevel DEBUG    ${LISTENER DIR}/result_model.robot
Resource          listener_resource.robot

*** Variables ***
${MODEL FILE}     %{TEMPDIR}/listener_result_model.json

*** Test Cases ***
Result model is consistent with information sent to listeners
    Should Be Empty    ${ERRORS}

Result model build during execution is same as saved to output.xml
    ${expected} =    Check Test Case    Test
    ${actual} =    Evaluate    robot.result.TestCase.from_json($MODEL_FILE)
    ${suite} =     Evaluate    robot.result.TestSuite.from_dict({'tests': [$actual]})    # Required to get correct id.
    Dictionaries Should Be Equal    ${actual.to_dict()}    ${expected.to_dict()}

Messages below log level and messages explicitly removed are not included
    ${tc} =    Check Test Case    Test
    Check Keyword Data    ${tc[2, 1]}       BuiltIn.Log    args=User keyword, DEBUG    children=3
    Check Log Message     ${tc[2, 1, 0]}    Starting KEYWORD
    Check Log Message     ${tc[2, 1, 1]}    User keyword    DEBUG
    Check Log Message     ${tc[2, 1, 2]}    Ending KEYWORD
    Check Keyword Data    ${tc[2, 2]}       BuiltIn.Log    args=Not logged, TRACE    children=2
    Check Log Message     ${tc[2, 2, 0]}    Starting KEYWORD
    Check Log Message     ${tc[2, 2, 1]}    Ending KEYWORD
    Check Keyword Data    ${tc[2, 3]}       BuiltIn.Log    args=Remove me!    children=2
    Check Log Message     ${tc[2, 3, 0]}    Starting KEYWORD
    Check Log Message     ${tc[2, 3, 1]}    Ending KEYWORD
