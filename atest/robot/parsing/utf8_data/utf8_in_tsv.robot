*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/utf8_data.tsv
Force Tags      pybot  jybot  regression
Resource        atest_resource.txt

*** Test Cases ***
UTF-8 In Metadata
    Should Be Equal  ${SUITE.doc}  Testing that reading and writing of Unicode (äöå §½€ etc.) works properly.
    Should Be Equal as Strings  ${SUITE.metadata}  {Ä: §}
    Check Test Tags  UTF-8  tag-§  tag-€
    Check Test Doc  UTF-8  äöå §½€

UTF-8 In Keyword Arguments
    ${tc} =  Check Test Case  UTF-8
    Check Log Message  ${tc.setup.msgs[0]}  äöå
    Check Log Message  ${tc.kws[0].msgs[0]}  §½€
    Check Log Message  ${tc.kws[1].msgs[0]}  äöå §½€
    Check Log Message  ${tc.kws[2].kws[0].msgs[0]}  äöå
    Check Log Message  ${tc.kws[2].kws[1].msgs[0]}  äöå §½€
    Check Log Message  ${tc.kws[2].kws[2].msgs[0]}  §½€

UTF-8 In Test Case And UK Names
    ${tc} =  Check Test Case  UTF-8 Name Äöå §½€"
    Should Be Equal  ${tc.kws[0].name}  \${ret} = Äöå §½€
    Check Log Message  ${tc.kws[1].msgs[0]}  äöå §½€
    Check Log Message  ${tc.kws[3].msgs[0]}  value

