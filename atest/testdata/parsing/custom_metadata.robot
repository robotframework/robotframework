*** Settings ***
Documentation     Compact comprehensive custom metadata test data with maximum coverage
Metadata          Version           2.1.0
Metadata          System            ${{platform.version()}}
Metadata          Environment       ${{'Local' if os.getenv('CI') is None else 'CI/CD'}}

*** Variables ***
${BUILD_NUMBER}       2024
${LONG_TEXT}          This is a longer text value to test handling of extended content with punctuation, numbers like 123, and special characters: @#$%^&*()
${MULTILINE_VALUE}    Line one content
...                   Line two content  
...                   Line three: final

*** Test Cases ***
Comprehensive Metadata Test
    [Documentation]    Main test case covering essential metadata variations
    [Tags]                         abc    def
    [Owner]                        John Doe    Jane Smith
    [Requirement]                  REQ-001    REQ-002
    [Priority]                     High
    [Component]                    Authentication
    [Feature]                      Login System
    [Build]                        ${BUILD_NUMBER}
    [Long Description]             ${LONG_TEXT}
    [Multiline Notes]              ${MULTILINE_VALUE}
    [Empty Value]                  
    [Special Characters]           !@#$%^&*()_+-=[]{}|;:,.<>?/~`
    [Unicode Content]              测试数据    Тестовые данные    Données de test
    [HTML Content]                 <b>Bold</b> and <i>italic</i>
    [JSON Data]                    {"type": "test", "priority": "high", "count": 42}
    [URL]                          https://api.example.com:8080/v1/test?param1=value1
    [Email]                        test@example.com
    [Mixed Quotes]                 Value with "double" and 'single' quotes
    [My Custom Metadata]           My Custom Metadata
    [System]                       ${{platform.version()}}
    Log                            Comprehensive metadata test
    Should Be Equal                ${True}    ${True}

Edge Cases Test
    [Documentation]    Test case for edge cases and boundary conditions
    [Empty Key Test]               ${EMPTY}
    [CamelCaseKey]                 CamelCase value
    [snake_case_key]               snake_case value
    [kebab-case-key]               kebab-case value
    [Key With Spaces]              Value with spaces
    [UnicodeKey]                   Unicode key test
    [HTML Tags]                    <div>HTML content</div>
    [Numbers Only]                 1234567890
    [Boolean Like]                 True    False
    [Version Numbers]              1.0.0    2.1.3-beta.1
    [UUID Sample]                  550e8400-e29b-41d4-a716-446655440000
    [IP Address]                   192.168.1.100
    [Base64 Sample]                dGVzdCBkYXRhIGVuY29kZWQ=
    Log                            Edge cases test
    Should Be Equal                ${True}    ${True}

Performance Scale Test
    [Documentation]    Test case with multiple metadata entries for performance testing
    [Meta01]                      Value 01
    [Meta02]                      Value 02  
    [Meta05]                      Value 05
    [Meta10]                      Value 10
    [Meta15]                      Value 15
    [Meta20]                      Value 20
    Log                           Performance scale test
    Should Be Equal               ${True}    ${True}

Unicode Internationalization Test
    [Documentation]    Test Unicode and international character support
    [English]                     Standard ASCII text
    [German]                      Umlaute: äöüÄÖÜß
    [French]                      Accents: àáâäèéêëìíîï
    [Spanish]                     Tildes: ñÑáéíóúÁÉÍÓÚ
    [Russian]                     Cyrillic test data
    [Chinese]                     简体中文：测试数据
    [Japanese]                    Japanese test data
    [Emoji Mix]                   Hello世界🌍Test測試
    Log                           Unicode internationalization test
    Should Be Equal               ${True}    ${True}

*** Keywords ***
Enhanced Login Keyword
    [Documentation]    Enhanced keyword with essential metadata coverage
    [Owner]                       Jane Doe
    [API Endpoint]                POST /api/v1/auth/login
    [Response Status]             200 OK
    [Complexity]                  Medium
    [Dependencies]                User Database    Session Store
    [Security Level]              High
    [Performance Target]          < 2 seconds response
    Log                           Enhanced login execution
    No Operation

Data Processing Keyword
    [Documentation]    Keyword with data processing metadata
    [Input Format]                JSON    XML    CSV
    [Output Format]               Processed JSON
    [Memory Usage]                Optimized for large datasets
    [Quality Metrics]             Accuracy > 99.5%
    [Scalability]                 Horizontal scaling support
    [Data Privacy]                PII anonymization
    Log                           Data processing execution
    No Operation
