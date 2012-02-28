*** Settings ***
Documentation  Test cases for metadata in  Setting table (incl. imports)    and within Test Case and    Keyword tables.
doc u ment  Text from multiple columns is catenated with spaces,  and line continuation creates a new line.  Real newlines can be  added with 'backslash+n' (e.g. '\n').\
...  Also variables work since Robot     ${version}, and they work   from commandline too:   ${SUITE_DOC_FROM_CLI}.
...  Starting from RF 2.1  ${nonexisting} variables are  just left unchanged.
...  Of course escaping  (e.g.    '\${non-existing-in-suite-doc}'    and '\\')  works too.
 Def ault TAGS  @{default_tags}
Default Tags  \  default-39  # Empty tags should be ignored
Forcetags  \  force-1
Test Setup  Log  Default test setup
Test Teardown  Log  Default test teardown  INFO
Suitesetup  ${SUITE_FIXTURE_FROM_CLI}  ${default} suite setup  # Global variables work here
Suite Teardown  ${SUITE_FIXTURE_FROM_CLI}
Suite Tear down  Default suite teardown

*** Variables ***
${version}  1.2
${default}  Default
@{Default_tags}  default-1O  default-2  # default-3 added separately


*** Test cases ***
Test Case  No Operation
