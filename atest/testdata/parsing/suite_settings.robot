*** Settings ***
Documentation    ${1}st line is shortdoc.
...              Text from     multiple    columns    is catenated with spaces,
...              and line continuation creates a new line.
...              Newlines can also be added literally "\n\n".
...  Variables work since Robot ${version} and ${SUITE_DOC_FROM_CLI} works too.
...  Starting from RF 2.1  ${nonexisting} variables are         left unchanged.
...  Escaping    (e.g. '\${non-existing}', 'c:\\temp', '\\n')    works too.

Default Tags    \    default  # Empty tags should be ignored
Forcetags    f1
...    F2
Test Setup  Log  Default test setup
Test Teardown  Log  Default test teardown  INFO
Suitesetup  ${SUITE_FIXTURE_FROM_CLI}  ${default} suite setup  # Global variables work here
Su ite Tear down    ${SUITE_FIXTURE_FROM_CLI}    Default suite teardown

Invalid Setting    Yes, this is invalid.

*** Variables ***
${version}  1.2
${default}  Default
@{Default_tags}  default-1O  default-2  # default-3 added separately


*** Test Cases ***
Test Case
    No Operation
