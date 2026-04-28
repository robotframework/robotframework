*** Settings ***
Documentation     Consolidated tests for custom metadata parsing, edge cases, and variable resolution.
...               Comprehensive testing of [CustomName] syntax parsing, validation,
...               and integration with Robot Framework's variable system.
Suite Setup       Run Tests    ${EMPTY}    ${COMPREHENSIVE_FILE}
Resource          atest_resource.robot

*** Variables ***
${COMPREHENSIVE_FILE}      parsing/test_custom_metadata_compact.robot
${LEGACY_FILE}            parsing/custom_metadata.robot

*** Test Cases ***
Basic Custom Metadata Parsing
    [Documentation]    Test basic custom metadata parsing with compact test data
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.status}    PASS
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}           John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Priority']}        High
    Should Be Equal    ${tc.custom_metadata['Component']}       Authentication

Custom Metadata With Regular Settings
    [Documentation]    Test mixing custom metadata with regular test settings
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    Should Be True    ${tc.has_custom_metadata}
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Feature']}    Login System

Multiline And Empty Values
    [Documentation]    Test multiline custom metadata and empty values
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.custom_metadata['Long Description']}    This is a longer text value to test handling of extended content with punctuation, numbers like 123, and special characters: @#$%^&*()
    Should Be Equal    ${tc.custom_metadata['Empty Value']}    ${EMPTY}

Special Characters And Edge Cases
    [Documentation]    Test special characters and edge case metadata names
    ${tc} =    Check Test Case    Edge Cases Test
    Should Be Equal    ${tc.custom_metadata['Empty Key Test']}    ${EMPTY}
    Should Be Equal    ${tc.custom_metadata['UnicodeKey']}       Unicode key test
    Should Be Equal    ${tc.custom_metadata['HTML Tags']}        <div>HTML content</div>

Large Scale Metadata
    [Documentation]    Test handling of many metadata entries for performance
    ${tc} =    Check Test Case    Performance Scale Test
    Should Be Equal    ${tc.custom_metadata['Meta01']}    Value 01
    Should Be Equal    ${tc.custom_metadata['Meta10']}    Value 10
    Should Be Equal    ${tc.custom_metadata['Meta20']}    Value 20

Case Sensitivity Tests
    [Documentation]    Test custom metadata key case sensitivity
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    # Keys should be case-insensitive (Robot Framework standard)
    Dictionary Should Contain Key    ${tc.custom_metadata}    Owner
    Dictionary Should Contain Key    ${tc.custom_metadata}    owner
    Dictionary Should Contain Key    ${tc.custom_metadata}    OWNER
    Dictionary Should Contain Key    ${tc.custom_metadata}    OwNeR

HTML And URL Content
    [Documentation]    Test HTML tags and URLs in custom metadata
    ${tc} =    Check Test Case    Comprehensive Metadata Test  
    Should Be Equal    ${tc.custom_metadata['Email']}    test@example.com
    Should Be Equal    ${tc.custom_metadata['URL']}    https://api.example.com:8080/v1/test?param1=value1

Variable Resolution
    [Documentation]    Test variable resolution in custom metadata
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.custom_metadata['Build']}    2024
    Should Be Equal    ${tc.custom_metadata['Feature']}    Login System
    Should Not Contain    ${tc.custom_metadata['Build']}    \${

Complex Variables And Built-ins  
    [Documentation]    Test complex expressions and built-in variables
    ${tc} =    Check Test Case    Edge Cases Test
    Should Contain    ${tc.custom_metadata['UUID Sample']}    550e8400-e29b-41d4-a716-446655440000
    Should Contain    ${tc.custom_metadata['Base64 Sample']}    dGVzdCBkYXRhIGVuY29kZWQ=

Non-String Variable Conversion
    [Documentation]    Test that all metadata values are converted to strings  
    ${tc} =    Check Test Case    Edge Cases Test
    Should Be Equal    ${tc.custom_metadata['Numbers Only']}     1234567890
    Should Be String    ${tc.custom_metadata['Numbers Only']}

Unicode And Internationalization
    [Documentation]    Test Unicode and international character support
    ${tc} =    Check Test Case    Unicode Internationalization Test
    Should Be Equal    ${tc.custom_metadata['German']}    Umlaute: äöüÄÖÜß
    Should Be Equal    ${tc.custom_metadata['Chinese']}    简体中文：测试数据
    Should Be Equal    ${tc.custom_metadata['Emoji Mix']}    Hello世界🌍Test測試

Missing Variables Handling
    [Documentation]    Test handling of missing variables with legacy test data
    Run Tests    ${EMPTY}    parsing/test_custom_metadata_missing_vars.robot
    ${tc} =    Check Test Case    Missing Variables Test
    Should Contain    ${tc.custom_metadata['Missing']}    \${MISSING_VAR}

Environment And CLI Variables
    [Documentation]    Test environment and command line variables
    Set Environment Variable    CUSTOM_ENV_VAR    EnvValue
    Run Tests    ${EMPTY}    parsing/test_custom_metadata_env_vars.robot
    ${tc} =    Check Test Case    Environment Variables Test
    Should Be Equal    ${tc.custom_metadata['Environment']}    EnvValue
    [Teardown]    Remove Environment Variable    CUSTOM_ENV_VAR

Line Continuations
    [Documentation]    Test line continuation handling from comprehensive test data
    Run Tests    ${EMPTY}    ${COMPREHENSIVE_FILE}
    ${tc} =    Check Test Case    Comprehensive Metadata Test
    Should Contain    ${tc.custom_metadata['Multiline Notes']}    Line one content
    Should Contain    ${tc.custom_metadata['Multiline Notes']}    Line two content
    Should Contain    ${tc.custom_metadata['Multiline Notes']}    Line three: final
