*** Settings ***
Library           Remote   http://127.0.0.1:${PORT}

*** Variables ***
${PORT}           8270

*** Test Cases ***
Non dict result dict
    [Documentation]    FAIL Invalid remote result dictionary: 42
    Non dict result dict

Invalid result dict
    [Documentation]    FAIL Invalid remote result dictionary: {}
    Invalid result dict

Invalid char in XML
    [Documentation]    FAIL STARTS: Processing XML-RPC return value failed. Most often this happens when the return value contains characters that are not valid in XML. Original error was: ExpatError:
    Invalid char in XML

Exception
    [Documentation]    FAIL <class 'Exception'>:my message
    Exception   my message

Broken connection
    [Documentation]    FAIL STARTS: Connection to remote server broken:
    Shutdown
    Exception    connection already broken
