*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/tags_with_variables.robot
Resource          atest_resource.robot

*** Test Case ***
External variable not resolved
    ${tc}    Check test case    ${TEST NAME}
    Check Keyword Data  ${tc.kws[1]}  Keyword attempting external tag    tags=\${external}

Argument is resolved
    ${tc}    Check test case    ${TEST NAME}
    Check Keyword Data  ${tc.kws[0]}    Keyword with tag argument    
                                 ...    args=This is an argument
                                 ...    tags=This is an argument

Part of tag as argument
    ${tc}    Check test case    ${TEST NAME}
    Check Keyword Data  ${tc.kws[0]}    Keyword with tag to complete
                                 ...    args=very
                                 ...    tags=Customisable tag is very cool
