*** Settings ***
Documentation     Test data for custom metadata with variables and edge cases.
Metadata    Test Suite Version    2.0
Metadata    Test Environment      ${SUITE_ENV}

*** Variables ***
${SUITE_ENV}      Development
${OWNER}          Test Team
${VERSION}        1.0-${BUILD_NUMBER}
${BUILD_NUMBER}   123
${EMPTY_VAR}      ${EMPTY}
&{CONFIG}         env=test    version=1.0

*** Test Cases ***
Variable Test  
    [Owner]           ${OWNER}
    [Version]         ${VERSION}
    [System]          ${{platform.system()}}
    [Environment]     ${CONFIG}[env]
    [Empty Value]     ${EMPTY_VAR}
    Log    Variable resolution test

Complex Variables Test
    [Documentation]    Test with complex variable expressions
    [Build Info]      Build ${BUILD_NUMBER} on ${{datetime.datetime.now().strftime('%Y-%m-%d')}}
    [Config Path]     /path/to/${CONFIG}[env]/config.xml
    [Tags]            smoke    ${CONFIG}[env]
    [Debug Mode]      ${{str(True).lower()}}
    Log    Complex variables test

Edge Cases Test
    [Documentation]    Test edge cases and special values
    [Special Chars]   Test with "quotes" and 'apostrophes' and ${SPACE}spaces${SPACE}
    [Unicode]         Test with üñíçødé characters 🚀
    [Long Value]      ${{' '.join(['Long'] * 20)}}
    [Null Value]      ${None}
    [Boolean]         ${True}
    [Number]          ${42}
    [List Value]      ${CONFIG.values()}
    Log    Edge cases test

Line Continuation Test
    [Multi Line]      This is a very long custom metadata value
    ...               that spans multiple lines
    ...               and should be properly concatenated
    ...               with preserved spacing and formatting
    [Complex Multi]   First part: ${OWNER}
    ...               Second part: ${VERSION} 
    ...               Third part: ${{platform.system()}}
    Log    Line continuation test

Escaping Test
    [Escaped Vars]    \${NOT_A_VARIABLE} should remain as is
    [Backslashes]     Path: C:\\temp\\file.txt with \\backslashes\\  
    [Mixed]           Normal ${OWNER} and \${ESCAPED_VAR} together
    Log    Escaping test

Non-String Variable Test
    [Number Meta]     ${42}
    [Boolean Meta]    ${True}  
    [None Meta]       ${None}
    [List Meta]       ${CONFIG.keys()}
    Log    Non-string variables test

*** Keywords ***
Custom Keyword With Variables
    [Documentation]    Keyword to test custom metadata with variables  
    [API Endpoint]    https://api.${CONFIG}[env].example.com/v1
    [Owner]           ${OWNER}
    [Complexity]      ${{random.choice(['Low', 'Medium', 'High'])}}
    [Timeout]         ${{30 if $CONFIG['env'] == 'test' else 60}}
    Log    Custom keyword executed

Dynamic Metadata Keyword
    [Documentation]    Test dynamic metadata generation
    [Timestamp]       ${{datetime.datetime.now().isoformat()}}
    [Random ID]       ${{uuid.uuid4().hex[:8]}}  
    [OS Info]         ${{platform.platform()}}
    [Python Version]  ${{sys.version.split()[0]}}
    Log    Dynamic metadata generated
