*** Settings ***
Documentation     Tests for --metadata are located in robot/cli/runner and
...               for other suite settings in suite_settings.robot.
Suite Setup       Run Tests    --variable meta_value_from_cli:my_metadata    parsing/suite_metadata.robot
Test Template     Validate metadata
Resource          atest_resource.robot

*** Test Cases ***
Metadata
    Name    Value
    name    Value
    NAME    Value

Metadata In Multiple Columns
    Multiple columns          Value in multiple columns

Metadata In Multiple Lines
    Multiple lines            Metadata in multiple lines\nis parsed using\nsame semantics as documentation.

Metadata With Variables
    Variables                 Version: 1.2

Metadata With Variable From Resource
    Variable from resource    Variable from a resource file

Metadata With Variable From Commandline
    Value from CLI            my_metadata

Using Same Name Twice
    Overridden                This overrides first value

Unescaping Metadata In Setting Table
    Escaping                  Three backslashes \\\\\\ & \${version}

*** Keywords ***
Validate metadata
    [Arguments]    ${name}    ${value}
    Should be Equal    ${SUITE.metadata['${name}']}    ${value}
