*** Settings ***
Documentation    ${1}st line is shortdoc.
...              Text from     multiple    columns    is catenated with spaces,
...              and line continuation creates a new line.
...              Newlines can also be added literally "\n\n".
...  Variables work since Robot ${version} and ${SUITE_DOC_FROM_CLI} works too.
...  Starting from RF 2.1  ${nonexisting} variables are         left unchanged.
...  Escaping    (e.g. '\${non-existing}', 'c:\\temp', '\\n')    works too.
...
Document    For backwards compatibility reasons we still support 'Document'
...  setting name and continuing
Doc U Ment    the doc by just repeating the setting multiple times.

 Def ault TAGS  @{default_tags}
Default Tags  \  default-39  # Empty tags should be ignored
Forcetags  \  force-1
Test Setup  Log  Default test setup
Test Teardown  Log  Default test teardown  INFO
Suitesetup  ${SUITE_FIXTURE_FROM_CLI}  ${default} suite setup  # Global variables work here
Suite Teardown  ${SUITE_FIXTURE_FROM_CLI}
Suite Tear down  Default suite teardown

Invalid Setting    Yes, this is invalid.

*** Variables ***
${version}  1.2
${default}  Default
@{Default_tags}  default-1O  default-2  # default-3 added separately


*** Test cases ***
Test Case  No Operation
