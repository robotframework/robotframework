*** Settings ***
Resource          console_resource.robot

*** Variables ***
${CONSOLES}       ${CURDIR}${/}..${/}..${/}..${/}testresources${/}consoles

*** Test Cases ***
Custom console by path
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Test 'Fail' FAIL
    Stdout Should Contain    DEFAULT: Output:
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console by path with argument
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py:ARGUMENT    misc/pass_and_fail.robot
    Stdout Should Contain    ARGUMENT: Suite 'Pass And Fail' started
    Stdout Should Contain    ARGUMENT: Test 'Pass' PASS
    Stdout Should Contain    ARGUMENT: Closing
    Stderr Should Be Empty

Custom console by module name
    Run Tests    --console CustomConsole --pythonpath ${CONSOLES}    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console as module with functions
    Run Tests    --console ${CONSOLES}${/}module_console.py    misc/pass_and_fail.robot
    Stdout Should Contain    MODULE: Suite 'Pass And Fail' started
    Stdout Should Contain    MODULE: Test 'Pass' PASS
    Stdout Should Contain    MODULE: Closing
    Stdout Should Not Contain    Output:
    Stdout Should Not Contain    Report:
    Stdout Should Not Contain    Log:
    Stderr Should Be Empty

Custom console by dotted name
    Run Tests    --console CustomConsole.CustomConsole --pythonpath ${CONSOLES}    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console with named argument
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py:name=NAMED    misc/pass_and_fail.robot
    Stdout Should Contain    NAMED: Suite 'Pass And Fail' started
    Stdout Should Contain    NAMED: Test 'Pass' PASS
    Stdout Should Contain    NAMED: Closing
    Stderr Should Be Empty

Custom console with wrong arguments
    ${path} =    Normalize Path    ${CONSOLES}${/}CustomConsole.py
    Run Tests Without Processing Output    --console ${CONSOLES}${/}CustomConsole.py:too:many:args    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Taking console logger '${CONSOLES}${/}CustomConsole.py:too:many:args' into use failed: Importing console logger '${path}' failed: Console logger 'CustomConsole' expected 0 to 1 arguments, got 3.${USAGE TIP}\n

Non-existing custom console
    Run Tests Without Processing Output    --console NonExistent    misc/pass_and_fail.robot
    Stderr Should Start With    [ ERROR ] Taking console logger 'NonExistent' into use failed: Importing console logger 'NonExistent' failed: ModuleNotFoundError:
