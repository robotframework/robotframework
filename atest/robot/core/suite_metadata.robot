*** Settings ***
Suite Setup     Run Tests  --variable meta_value_from_cli:my_metadata  core/suite_metadata.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

Documentation  Tests for commandline option --metadata are located in robot/cli/runner

*** Test Cases ***

Metadata
    Should be Equal  ${suite.metadata['Name']}  Value

Metadata In Multiple Columns
    Should be Equal  ${suite.metadata['Multiple columns']}  Value in multiple columns

Metadata In Multiple Lines
    Should be Equal  ${suite.metadata['multiple lines']}  Value in multiple lines '\n\n' and with\nreal newlines

Metadata With Variables
    Should be Equal  ${suite.metadata['variables']}  Version: 1.2

Metadata With Variable From Resource
    Should be Equal  ${suite.metadata['Variable from resource']}  Variable from a resource file

Metadata With Variable From Commandline
    Should be Equal  ${suite.metadata['Value from CLI']}  my_metadata

Using Same Name Twice
    Should be Equal  ${suite.metadata['Overridden']}  This overrides first value

Old Style Metadata
    Should be Equal  ${suite.metadata['old style meta']}  some value

Unescaping Metadata In Setting Table
    [Documentation]  Test that metadata in setting table is unescaped correctly. This is already partly tested in Suite Documentation
    ${stderr} =  Get File  ${STDERR FILE}
    Fail If Contains  ${stderr}  \${non-existing-in-suite-doc}
    Should be Equal  ${suite.metadata['Escaping']}  Three backslashes \\\\\\
