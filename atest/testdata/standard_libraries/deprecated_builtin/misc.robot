*** Test Case ***
Noop
    Noop

Set
    ${var}    Set    Hello
    Fail Unless    '${var}' == 'Hello'
    ${var1}    ${var2}    Set    Hello    world
    Fail Unless    '${var1}' == 'Hello'
    Fail Unless    '${var2}' == 'world'
    @{list}    Set    Hi    again
    Equals    '@{list}[0]'    'Hi'
    Equals    '@{list}[1]'    'again'
    ${scal}    Set    Hi    again
    Equals    '${scal[0]}'    'Hi'
    Equals    '${scal[1]}'    'again'
    ${scal2}    Set    ${scal}
    Equals    ${scal}    ${scal2}
    ${empty}    Set
    Equals    ${empty}    ${EMPTY}

Message
    Message    This text is shown    as keyword arguments    but ignored otherwise
    Message    One message
    Message
