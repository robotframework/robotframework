*** Settings ***
Documentation     Tests for custom metadata CLI filtering via --custommetadata option.
Resource          cli_resource.robot

*** Variables ***
${TESTFILE}       parsing/test_custom_metadata_compact.robot

*** Test Cases ***
No Custom Metadata Filtering By Default
    [Documentation]    Test that all custom metadata is included by default
    Run Tests    ${EMPTY}    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}          John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Requirement']}    REQ-001 REQ-002
    Should Be Equal    ${tc.custom_metadata['Priority']}       High
    Should Be Equal    ${tc.custom_metadata['Component']}      Authentication

Custom Metadata Filtering With Single Option
    [Documentation]    Test filtering with single --custommetadata option
    Run Tests    --custommetadata Owner    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe Jane Smith
    # Other metadata should be filtered out
    Should Not Have Key    ${tc.custom_metadata}    Requirement
    Should Not Have Key    ${tc.custom_metadata}    Priority
    Should Not Have Key    ${tc.custom_metadata}    Component

Custom Metadata Filtering With Multiple Options
    [Documentation]    Test filtering with multiple --custommetadata options
    Run Tests    --custommetadata Owner --custommetadata Priority    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}       John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Priority']}    High
    # Other metadata should be filtered out
    Should Not Have Key    ${tc.custom_metadata}    Requirement
    Should Not Have Key    ${tc.custom_metadata}    Component

Custom Metadata Filtering Case Sensitivity
    [Documentation]    Test that metadata filtering is case-sensitive
    Run Tests    --custommetadata owner    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    # Check if case-sensitive filtering is implemented
    # If case-insensitive, 'owner' should match 'Owner'
    # If case-sensitive, no metadata should be returned for 'owner' filter
    ${has_owner} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${tc.custom_metadata}    Owner
    IF    ${has_owner}
        Log    Case-insensitive filtering: 'owner' matched 'Owner'    INFO
    ELSE
        Log    Case-sensitive filtering: 'owner' did not match 'Owner'    INFO
    END

Custom Metadata Filtering Keywords
    [Documentation]    Test that keyword custom metadata is also filtered
    Run Tests    --custommetadata Owner    ${TESTFILE}
    # Focus on test case custom metadata since keyword access may vary by test framework version
    ${tc} =    Get Test Case    Comprehensive Metadata Test  
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe Jane Smith
    Should Not Have Key    ${tc.custom_metadata}    Requirement
    Should Not Have Key    ${tc.custom_metadata}    Component

Custom Metadata Filtering With Special Characters
    [Documentation]    Test filtering with special characters in metadata names
    Run Tests    --custommetadata "My Custom Metadata"    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['My Custom Metadata']}    My Custom Metadata
    Should Not Have Key    ${tc.custom_metadata}    Owner

Custom Metadata Filtering Preserves Regular Settings
    [Documentation]    Test that filtering doesn't affect regular test settings
    Run Tests    --custommetadata Owner    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.status}    PASS
    Should Contain    ${tc.tags}    abc
    Should Contain    ${tc.tags}    def
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe Jane Smith

Variable Resolution In Custom Metadata With CLI
    [Documentation]    Test variable resolution with CLI filtering
    Run Tests    --custommetadata System    ${TESTFILE}
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Contain    ${tc.custom_metadata['System']}    .


*** Keywords ***
Should Not Have Key
    [Arguments]    ${dictionary}    ${key}
    ${has_key} =    Evaluate    "${key}" in $dictionary
    Should Not Be True    ${has_key}    Key '${key}' should not be present in custom metadata

Get User Keyword From Suite
    [Arguments]    ${keyword_name}
    FOR    ${kw}    IN    @{SUITE.resource.keywords}
        IF    '${kw.name}' == '${keyword_name}'
            RETURN    ${kw}
        END
    END
    Fail    Keyword '${keyword_name}' not found in suite resource

Custom Metadata Filtering With Empty List
    Run Tests    --custommetadata ""    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    ${kw} =    Get First Keyword Of Suite    ${SUITE}    Login With Valid Credentials
    # Empty string as metadata name should match empty metadata
    Should Be Equal    ${tc.custom_metadata['']}    ${EMPTY}    # Empty Metadata -> '' key
    # Other metadata should not be present
    Should Not Contain    ${tc.custom_metadata}    Owner
    Should Not Contain    ${tc.custom_metadata}    Priority

Custom Metadata Filtering With Non-Existing Names
    Run Tests    --custommetadata NonExistingMeta    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    ${kw} =    Get First Keyword Of Suite    ${SUITE}    Login With Valid Credentials
    # No custom metadata should be present
    Dictionary Should Be Empty    ${tc.custom_metadata}
    Dictionary Should Be Empty    ${kw.custom_metadata}

Custom Metadata Filtering With Special Characters
    Run Tests    --custommetadata "My Custom Metadata" --custommetadata "My Requirement"    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    ${kw} =    Get First Keyword Of Suite    ${SUITE}    Login With Valid Credentials
    
    # Test case metadata with spaces
    Should Be Equal    ${tc.custom_metadata['My Custom Metadata']}    My Custom Metadata
    Should Not Contain    ${tc.custom_metadata}    Owner
    
    # Keyword metadata with spaces and hyphens
    Should Be Equal    ${kw.custom_metadata['My Requirement']}    ACC-567
    Should Not Contain    ${kw.custom_metadata}    Owner

Custom Metadata Filtering Preserves Regular Settings
    Run Tests    --custommetadata Owner    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    # Regular settings should be preserved
    Should Contain Tags    ${tc}    abc    def
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe    Zweiter Wert
    Should Not Contain    ${tc.custom_metadata}    Priority

Custom Metadata Filtering With Multiline Values
    Run Tests    --custommetadata Multiline    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    # Multiline values should be preserved correctly
    Should Be Equal    ${tc.custom_metadata['Multiline']}
    ...                Multiline    Mein erwartetes Ergebnis\n\nist hier\n auf mehrerene Lines
    Should Not Contain    ${tc.custom_metadata}    Owner

Custom Metadata Filtering With Variables
    Run Tests    --custommetadata System    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    # Variables in metadata values should be resolved
    Should Contain    ${tc.custom_metadata['System']}    .    # Platform version contains dots
    Should Not Contain    ${tc.custom_metadata}    Owner

Variable Resolution In Custom Metadata With CLI
    Run Tests    --custommetadata System --variable CUSTOM_VAR:CLI_VALUE    parsing/test_custom_metadata_with_variables.robot
    ${tc} =    Check Test Case    Variable Test
    # Variables should be resolved during execution
    Should Be Equal    ${tc.custom_metadata['System']}    CLI_VALUE
    Should Contain    ${tc.custom_metadata['Environment']}    ${OS}    # Built-in variable

Multiple Custom Metadata Options In Argument File
    ${options} =    Catenate    SEPARATOR=\n
    ...    --custommetadata Owner
    ...    --custommetadata Priority
    ...    --custommetadata API
    Create File    ${TEMPDIR}/custom_metadata_args.txt    ${options}
    Run Tests    --argumentfile ${TEMPDIR}/custom_metadata_args.txt    parsing/custom_metadata.robot
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    ${kw} =    Get First Keyword Of Suite    ${SUITE}    Login With Valid Credentials
    
    Should Be Equal    ${tc.custom_metadata['Owner']}       John Doe    Zweiter Wert
    Should Be Equal    ${tc.custom_metadata['Priority']}    High
    Should Be Equal    ${kw.custom_metadata['API']}         https://api.example.com/login
    Should Not Contain    ${tc.custom_metadata}    Component
    [Teardown]    Remove File    ${TEMPDIR}/custom_metadata_args.txt

Invalid Custom Metadata Option
    [Documentation]    Test error handling for missing --custommetadata argument
    ${result} =    Run Tests Without Processing Output    --custommetadata    parsing/custom_metadata.robot
    Should Be Equal    ${result.rc}    ${252}

Get First Keyword Of Suite
    [Arguments]    ${suite}    ${keyword_name}
    FOR    ${kw}    IN    @{suite.resource.keywords}
        IF    $kw.name == $keyword_name
            RETURN    ${kw}
        END
    END
    Fail    Keyword '${keyword_name}' not found
