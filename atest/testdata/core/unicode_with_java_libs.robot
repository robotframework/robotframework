*** Setting ***
Library           UnicodeJavaLibrary

*** Test Case ***
Unicode
    Print Unicode Strings

Unicode Object
    ${obj} =    Print And Return Unicode Object
    Log    ${obj}
    Log    ${obj.name}

Unicode Error
    Raise Unicode Error
