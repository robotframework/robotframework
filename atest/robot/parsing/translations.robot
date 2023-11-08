*** Settings ***
Resource         atest_resource.robot

*** Test Cases ***
Finnish
    Run Tests    --language fi    parsing/translations/finnish/tests.robot
    Validate Translations

Finnish task aliases
    [Documentation]
    ...    Also tests that
    ...    - '--language' works when running a directory,
    ...    - it is possible to use language class docstring, and
    ...    - '-' is ignored in the given name to support e.g. 'pt-br'.
    Run Tests    --language fin-nish --rpa    parsing/translations/finnish
    Validate Task Translations

Custom
    Run Tests    --lang ${DATADIR}/parsing/translations/custom/custom.py    parsing/translations/custom/tests.robot
    Validate Translations

Custom task aliases
    Run Tests    --lang ${DATADIR}/parsing/translations/custom/custom.py --rpa    parsing/translations/custom/tasks.robot
    Validate Task Translations

Custom Per file configuration
    Run Tests    -P ${DATADIR}/parsing/translations/custom    parsing/translations/custom/custom_per_file.robot
    Validate Translations

Invalid
    ${result} =    Run Tests Without Processing Output    --lang bad    parsing/finnish.robot
    Should Be Equal        ${result.rc}        ${252}
    Should Be Empty        ${result.stdout}
    ${error} =    Catenate    SEPARATOR=\n
    ...    Invalid value for option '--language': Importing language file 'bad' failed: ModuleNotFoundError: No module named 'bad'
    ...    Traceback \\(most recent call last\\):
    ...    .*${USAGE TIP}
    Should Match Regexp    ${result.stderr}    ^\\[ ERROR \\] ${error}$    flags=DOTALL

Per file configuration
    Run Tests    ${EMPTY}    parsing/translations/per_file_config/fi.robot
    Validate Translations

Per file configuration with multiple languages
    Run Tests    ${EMPTY}    parsing/translations/per_file_config/many.robot
    Should Be Equal    ${SUITE.doc}    Exemplo
    ${tc} =    Check Test Case    ตัวอย่าง
    Should Be Equal    ${tc.doc}    приклад

Invalid per file configuration
    Run Tests    ${EMPTY}    parsing/translations/per_file_config/many.robot
    Error in file    0    parsing/translations/per_file_config/many.robot    4
    ...    Invalid language configuration:
    ...    Language 'invalid' not found nor importable as a language module.

Per file configuration bleeds to other files
    [Documentation]    This is a technical limitation and will hopefully change!
    Run Tests    ${EMPTY}    parsing/translations/per_file_config/fi.robot parsing/translations/finnish/tests.robot
    Validate Translations    ${SUITE.suites[0]}
    Validate Translations    ${SUITE.suites[1]}

*** Keywords ***
Validate Translations
    [Arguments]    ${suite}=${SUITE}
    Should Be Equal    ${suite.name}                       Custom name
    Should Be Equal    ${suite.doc}                        Suite documentation.
    Should Be Equal    ${suite.metadata}[Metadata]         Value
    Should Be Equal    ${suite.setup.full_name}            Suite Setup
    Should Be Equal    ${suite.teardown.full_name}         Suite Teardown
    Should Be Equal    ${suite.status}                     PASS
    ${tc} =            Check Test Case                     Test without settings
    Should Be Equal    ${tc.doc}                           ${EMPTY}
    Should Be Equal    ${tc.tags}                          ${{['test', 'tags']}}
    Should Be Equal    ${tc.timeout}                       1 minute
    Should Be Equal    ${tc.setup.full_name}               Test Setup
    Should Be Equal    ${tc.teardown.full_name}            Test Teardown
    Should Be Equal    ${tc.body[0].full_name}             Test Template
    Should Be Equal    ${tc.body[0].tags}                  ${{['keyword', 'tags']}}
    ${tc} =            Check Test Case                     Test with settings
    Should Be Equal    ${tc.doc}                           Test documentation.
    Should Be Equal    ${tc.tags}                          ${{['test', 'tags', 'own tag']}}
    Should Be Equal    ${tc.timeout}                       ${NONE}
    Should Be Equal    ${tc.setup.full_name}               ${NONE}
    Should Be Equal    ${tc.teardown.full_name}            ${NONE}
    Should Be Equal    ${tc.body[0].full_name}             Keyword
    Should Be Equal    ${tc.body[0].doc}                   Keyword documentation.
    Should Be Equal    ${tc.body[0].tags}                  ${{['keyword', 'tags', 'own tag']}}
    Should Be Equal    ${tc.body[0].timeout}               1 hour
    Should Be Equal    ${tc.body[0].setup.full_name}       BuiltIn.Log
    Should Be Equal    ${tc.body[0].teardown.full_name}    BuiltIn.No Operation

Validate Task Translations
    ${tc} =            Check Test Case                     Task without settings
    Should Be Equal    ${tc.doc}                           ${EMPTY}
    Should Be Equal    ${tc.tags}                          ${{['task', 'tags']}}
    Should Be Equal    ${tc.timeout}                       1 minute
    Should Be Equal    ${tc.setup.full_name}               Task Setup
    Should Be Equal    ${tc.teardown.full_name}            Task Teardown
    Should Be Equal    ${tc.body[0].full_name}             Task Template
    ${tc} =            Check Test Case                     Task with settings
    Should Be Equal    ${tc.doc}                           Task documentation.
    Should Be Equal    ${tc.tags}                          ${{['task', 'tags', 'own tag']}}
    Should Be Equal    ${tc.timeout}                       ${NONE}
    Should Be Equal    ${tc.setup.full_name}               ${NONE}
    Should Be Equal    ${tc.teardown.full_name}            ${NONE}
    Should Be Equal    ${tc.body[0].full_name}             BuiltIn.Log
