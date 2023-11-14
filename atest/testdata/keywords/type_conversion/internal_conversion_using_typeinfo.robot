language: German

*** Settings ***
Library       InternalConversionUsingTypeInfo.py

*** Test Cases ***
Internal conversion
    [Documentation]    FAIL    ValueError: Argument 'bad' cannot be converted to integer.
    Internal conversion    int            42               ${42}
    Internal conversion    int | float    3.14             ${3.14}
    Internal conversion    list[int]      [1, 2.0, '3']    ${{[1, 2, 3]}}
    Internal conversion    int            bad              whatever

Custom converters
    Custom converters    ROBOT FACE    🤖
    Custom converters    TROPHY        🏆

Language configuration
    Language configuration

Default language configuration
    Default language configuration
