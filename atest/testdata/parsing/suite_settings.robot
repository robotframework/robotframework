*** Settings ***
Name             Custom name
Documentation    ${1}st logical line
...              (i.e. paragraph)
...              is shortdoc on console.
...
...              Documentation can have multiple rows
...              and    also    multiple    columns.
...
...              Newlines can also be added literally with "\n".
...              If a row ends with a newline\n
...              or backslash \
...              no automatic newline is added.
...
...              | table | =header= |
...              | foo   |    bar   |
...              | ragged |
...
...  Variables work since Robot ${version} and ${SUITE_DOC_FROM_CLI} works too.
...  Starting from RF 2.1 ${nonexisting} variables are left unchanged.
...  Escaping (e.g. '\${non-existing}', 'c:\\temp', '\\n') works too.
...  Not ${closed

Default Tags      \    default  # Empty tags should be ignored
Force Tags        f1
...    F2
Test Setup        Log    Default test setup
Test Teardown     Log    Default test teardown  INFO
Suite Setup       ${SUITE_FIXTURE_FROM_CLI}    ${default} suite setup  # Global variables work here
Suite Teardown    ${SUITE_FIXTURE_FROM_CLI}    Default suite teardown

Invalid Setting    Yes, this is invalid.
Megadata           Small typo should provide recommendation

*** Variables ***
${version}         1.2
${default}         Default

*** Test Cases ***
Test Case
    No Operation
