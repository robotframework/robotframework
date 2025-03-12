*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/data_formats/resource_extensions
Resource         atest_resource.robot

*** Test Cases ***
Resource with '*.resource' extension
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1, 0]}    nested.resource
    Check Log Message    ${tc[0, 3, 0]}       resource.resource
    Check Log Message    ${tc[1, 1, 0]}       nested.resource
    Check Log Message    ${tc[4, 0]}          resource.resource
    Check Log Message    ${tc[5, 0]}          nested.resource

'*.resource' files are not parsed for tests
    Should Contain Suites    ${SUITE}    Tests
    ${path} =    Normalize Path    ${DATADIR}/parsing/data_formats/resource_extensions/tests.resource
    Syslog Should Contain    | INFO \ | Ignoring file or directory '${path}'.

Resource with '*.robot' extension
    Check Test Case    ${TESTNAME}

Resource with '*.txt' extension
    Check Test Case    ${TESTNAME}

Resource with '*.tsv' extension
    Check Test Case    ${TESTNAME}

Resource with '*.rst' extension
    [Tags]    require-docutils
    Check Test Case    ${TESTNAME}

Resource with '*.rest' extension
    [Tags]    require-docutils
    Check Test Case    ${TESTNAME}

Resource with '*.rsrc' extension
    Check Test Case    ${TESTNAME}

Resource with '*.json' extension
    Check Test Case    ${TESTNAME}

Resource with invalid extension
    Check Test Case    ${TESTNAME}
    Error in file    0    parsing/data_formats/resource_extensions/tests.robot    10
    ...    Invalid resource file extension '.invalid'.
    ...    Supported extensions are '.json', '.resource', '.rest', '.robot', '.rsrc', '.rst', '.tsv' and '.txt'.
    Length should be    ${ERRORS}    1
