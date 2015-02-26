*** Test Case ***
Noop
    Noop

Set
    ${var}    Set    Hello
    Should Be True    '${var}' == 'Hello'
    ${var1}    ${var2}    Set    Hello    world
    Should Be True    '${var1}' == 'Hello'
    Should Be True    '${var2}' == 'world'
    @{list}    Set    Hi    again
    Should Be Equal    '@{list}[0]'    'Hi'
    Should Be Equal    '@{list}[1]'    'again'
    ${scal}    Set    Hi    again
    Should Be Equal    '${scal[0]}'    'Hi'
    Should Be Equal    '${scal[1]}'    'again'
    ${scal2}    Set    ${scal}
    Should Be Equal    ${scal}    ${scal2}
    ${empty}    Set
    Should Be Equal    ${empty}    ${EMPTY}

Message
    Message    This text is shown    as keyword arguments    but ignored otherwise
    Message    One message
    Message
