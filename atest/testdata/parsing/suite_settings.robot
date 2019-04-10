*** Settings ***
Documentation    ${1}st logical line
...              (i.e. paragraph)
...              is shortdoc on console.
...
...              Documentation can have multiple rows
...              and    also    multiple    columns.
...              Newlines can also be added literally with "\n".
...
...  Variables work since Robot ${version} and ${SUITE_DOC_FROM_CLI} works too.
...  Starting from RF 2.1 ${nonexisting} variables are left unchanged.
...  Escaping (e.g. '\${non-existing}', 'c:\\temp', '\\n') works too.

Default Tags      \    default  # Empty tags should be ignored
For CET ag S      f1    # This format deprecated since RF 3.1
...    F2
Test Setup        Log    Default test setup
Test Teardown     Log    Default test teardown  INFO
Suite Setup       ${SUITE_FIXTURE_FROM_CLI}    ${default} suite setup  # Global variables work here
Suite Teardown    ${SUITE_FIXTURE_FROM_CLI}    Default suite teardown

Invalid Setting    Yes, this is invalid.

*** Variables ***
${version}         1.2
${default}         Default

*** Test Cases ***
Test Case
    No Operation
