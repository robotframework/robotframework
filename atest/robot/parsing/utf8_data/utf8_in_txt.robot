*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/utf8_data.robot
Resource          atest_resource.robot

*** Test Cases ***
UTF-8 In Metadata
    Should Be Equal    ${SUITE.doc}    Testing that reading and writing of Unicode (äöå §½€ etc.) works properly.
    Should Be Equal As Strings    ${SUITE.metadata}    {Ä: §}
    Check Test Tags    UTF-8    tag-§    tag-€
    Check Test Doc     UTF-8    äöå §½€

UTF-8 In Keyword Arguments
    ${tc} =    Check Test Case    UTF-8
    Check Log Message    ${tc.setup[0]}    äöå
    Check Log Message    ${tc[0, 0]}       §½€
    Check Log Message    ${tc[1, 0]}       äöå §½€
    Check Log Message    ${tc[2, 0, 0]}    äöå
    Check Log Message    ${tc[2, 1, 0]}    äöå §½€
    Check Log Message    ${tc[2, 2, 0]}    §½€

UTF-8 In Test Case And UK Names
    ${tc} =    Check Test Case    UTF-8 Name Äöå §½€"
    Check Keyword Data    ${tc[0]}       Äöå §½€    \${ret}
    Check Log Message     ${tc[1, 0]}    äöå §½€
    Check Log Message     ${tc[3, 0]}    value
