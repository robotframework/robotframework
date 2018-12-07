*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/data_formats/resource_extension
Resource         atest_resource.robot

*** Test Cases ***
Resource with '*.resource' extension
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    nested.resource
    Check Log Message    ${tc.kws[0].kws[3].msgs[0]}           resource.resource
    Check Log Message    ${tc.kws[1].kws[1].msgs[0]}           nested.resource
    Check Log Message    ${tc.kws[4].msgs[0]}                  resource.resource
    Check Log Message    ${tc.kws[5].msgs[0]}                  nested.resource

'*.resource' files are not parsed for tests
    Should Contain Suites    ${SUITE}    Tests
    Should Contain Tests     ${SUITE}    Resource with '*.resource' extension
    ${path} =    Normalize Path    ${DATADIR}/parsing/data_formats/resource_extension/tests.resource
    Check Syslog Contains    | INFO \ | Ignoring file or directory '${path}'.
