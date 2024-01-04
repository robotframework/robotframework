*** Settings ***
Suite Setup       Run Tests    --listener ${DATADIR}/${MODIFIER}    ${SOURCE}
Resource          atest_resource.robot

*** Variables ***
${SOURCE}         output/listener_interface/body_items_v3/keyword_arguments.robot
${MODIFIER}       output/listener_interface/body_items_v3/ArgumentModifier.py

*** Test Cases ***
Arguments as strings
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=\${STATE}, number=\${123}, obj=None, escape=c:\\\\temp\\\\new
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=new, 123, c:\\\\temp\\\\new, NONE

Arguments as tuples
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=\${STATE}, escape=c:\\\\temp\\\\new, obj=Object(123), number=\${123}
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=new, 1.0, obj=Object(1), escape=c:\\\\temp\\\\new

Arguments directly as positional and named
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=\${XXX}, 456, c:\\temp\\new, obj=Object(456)
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=state=\${XXX}, obj=Object(1), number=1.0, escape=c:\\temp\\new

Too many arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=a, b, c, d, e, f, g    status=FAIL
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=${{', '.join(str(i) for i in range(100))}}    status=FAIL

Conversion error
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=whatever, not a number    status=FAIL
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=number=bad    status=FAIL

Named argument not matching
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=no=match    status=FAIL
    Check Keyword Data    ${tc.body[1]}    Library.Library Keyword
    ...    args=o, k, bad=name    status=FAIL

Positional after named
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.body[0]}    Library.Library Keyword
    ...    args=positional, name=value, ooops    status=FAIL
