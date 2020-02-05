*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/data_formats/resource_extensions
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
    Should Contain Tests     ${SUITE}
    ...    Resource with '*.resource' extension
    ...    Resource with '*.robot' extension
    ...    Resource with '*.txt' extension
    ...    Resource with '*.tsv' extension
    ...    Resource with '*.rst' extension
    ...    Resource with '*.rest' extension
    ...    Resource with invalid extension
    ${path} =    Normalize Path    ${DATADIR}/parsing/data_formats/resource_extensions/tests.resource
    Syslog Should Contain    | INFO \ | Ignoring file or directory '${path}'.

Resource with '*.robot' extension
    Check Test Case    ${TESTNAME}

Resource with '*.txt' extension
    Check Test Case    ${TESTNAME}

Resource with '*.tsv' extension
    Check Test Case    ${TESTNAME}

Resource with '*.rst' extension
    Check Test Case    ${TESTNAME}

Resource with '*.rest' extension
    Check Test Case    ${TESTNAME}

Resource with invalid extension
    Check Test Case    ${TESTNAME}
    Error in file    0    parsing/data_formats/resource_extensions/tests.robot    8
    ...    Invalid resource file extension '.invalid'.
    ...    Supported extensions are '.resource', '.robot', '.txt', '.tsv', '.rst' and '.rest'.
    Length should be    ${ERRORS}    1
