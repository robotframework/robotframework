*** Settings ***
Suite Setup       Run Tests    --listener ${DATADIR}/${MODIFIER}    ${SOURCE}
Resource          atest_resource.robot

*** Variables ***
${SOURCE}         output/listener_interface/body_items_v3/keyword_arguments.robot
${MODIFIER}       output/listener_interface/body_items_v3/ArgumentModifier.py

*** Test Cases ***
Library keyword arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    Library.Library Keyword
    ...    args=\${STATE}, number=\${123}, obj=None, escape=c:\\\\temp\\\\new
    Check Keyword Data    ${tc[1]}    Library.Library Keyword
    ...    args=new, 123, c:\\\\temp\\\\new, NONE
    Check Keyword Data    ${tc[2]}    Library.Library Keyword
    ...    args=new, number=\${42}, escape=c:\\\\temp\\\\new, obj=Object(42)
    Check Keyword Data    ${tc[3]}    Library.Library Keyword
    ...    args=number=1.0, escape=c:\\\\temp\\\\new, obj=Object(1), state=new

User keyword arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    User keyword
    ...    args=A, B, C, D
    Check Keyword Data    ${tc[1]}    User keyword
    ...    args=A, B, d=D, c=\${{"c".upper()}}

Invalid keyword arguments
    ${tc} =    Check Test Case    Library keyword arguments
    Check Keyword Data    ${tc[4]}    Non-existing
    ...    args=p, n=1    status=FAIL

Too many arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    Library.Library Keyword
    ...    args=a, b, c, d, e, f, g    status=FAIL
    Check Keyword Data    ${tc[1]}    User keyword
    ...    args=a, b, c, d, e, f, g    status=FAIL
    Check Keyword Data    ${tc[2]}    Library.Library Keyword
    ...    args=${{', '.join(str(i) for i in range(100))}}    status=FAIL

Conversion error
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    Library.Library Keyword
    ...    args=whatever, not a number    status=FAIL
    Check Keyword Data    ${tc[1]}    Library.Library Keyword
    ...    args=number=bad    status=FAIL

Positional after named
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    Library.Library Keyword
    ...    args=positional, number=-1, ooops    status=FAIL
