*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/avoid_properties_when_creating_libraries.robot
Resource          atest_resource.robot

*** Test Case ***
Python Property
    Check Test Case    ${TEST NAME}
