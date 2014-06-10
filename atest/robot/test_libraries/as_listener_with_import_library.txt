*** Settings ***
Suite Setup     Run Tests  ${EMPTY}
...      test_libraries/as_listener/import_library.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Import Library works
    Check Test Case  ${TESTNAME}
