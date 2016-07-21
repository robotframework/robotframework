*** Settings ***
Documentation     Tests for --metadata are located in robot/cli/runner and
...               for other suite settings in suite_settings.robot.
Suite Setup       Run Tests    --variable meta_value_from_cli:my_metadata    parsing/suite_metadata.robot
Resource          atest_resource.robot

*** Test Cases ***
Metadata
    Should be Equal    ${SUITE.metadata['Name']}    Value

Metadata In Multiple Columns
    Should be Equal    ${SUITE.metadata['Multiple columns']}    Value in multiple columns

Metadata In Multiple Lines
    Should be Equal    ${SUITE.metadata['multiple lines']}    Value in multiple lines '\n\n' and with\nreal newlines

Metadata With Variables
    Should be Equal    ${SUITE.metadata['variables']}    Version: 1.2

Metadata With Variable From Resource
    Should be Equal    ${SUITE.metadata['Variable from resource']}    Variable from a resource file

Metadata With Variable From Commandline
    Should be Equal    ${SUITE.metadata['Value from CLI']}    my_metadata

Using Same Name Twice
    Should be Equal    ${SUITE.metadata['Overridden']}    This overrides first value

Unescaping Metadata In Setting Table
    ${stderr} =    Get File    ${STDERR FILE}
    Should Not Contain    ${stderr}    \${non-existing-in-suite-doc}
    Should be Equal    ${SUITE.metadata['Escaping']}    Three backslashes \\\\\\
