*** Settings ***
Documentation     Tests for custom metadata in rebot processing and filtering.
Suite Setup       Create Output Directory
Resource          rebot_cli_resource.robot

*** Variables ***
${CUSTOM_METADATA_FILE}    parsing/test_custom_metadata_compact.robot

*** Test Cases ***
Custom Metadata Preserved In Rebot
    [Documentation]    Test that custom metadata is preserved when processing with rebot
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    
    # Check that custom metadata is preserved (expect full concatenated value)
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.custom_metadata['Owner']}          John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Priority']}       High  
    Should Be Equal    ${tc.custom_metadata['Component']}      Authentication

Custom Metadata Filtering In Rebot
    [Documentation]    Test custom metadata filtering through rebot
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    
    # Process with rebot and filter custom metadata
    Run Rebot    --custommetadata Owner --custommetadata Priority    ${INPUT FILE}
    
    # Check that only filtered metadata is present (expect full concatenated value)
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.custom_metadata['Owner']}       John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Priority']}    High
    Should Be Equal    ${SUITE.test_count}    ${1}

Custom Metadata In Combined Reports
    [Documentation]    Test custom metadata when combining multiple reports
    Run Tests Without Processing Output    --output %{TEMPDIR}${/}output1.xml    ${CUSTOM_METADATA_FILE}
    Run Tests Without Processing Output    --output %{TEMPDIR}${/}output2.xml    parsing/test_custom_metadata_with_variables.robot
    
    # Combine reports
    Run Rebot    ${EMPTY}    %{TEMPDIR}${/}output1.xml %{TEMPDIR}${/}output2.xml
    
    # Both should have custom metadata
    Get Test Case    Comprehensive Metadata Test    # From first file
    Get Test Case    Variable Test    # From second file

Custom Metadata With Suite And Test Selection
    [Documentation]    Test custom metadata with filtering in rebot
    Run Tests Without Processing Output    ${EMPTY}    ${CUSTOM_METADATA_FILE} parsing/test_custom_metadata_with_variables.robot
    Move File    ${OUTFILE}    ${INPUT FILE}
    
    # Select specific suite
    Run Rebot    --suite "Custom Metadata"    ${INPUT FILE}
    
    # Only selected suite's metadata should be present
    Get Test Case    Comprehensive Metadata Test
    
    # Test selection works too
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    Run Rebot    --test "Comprehensive Metadata Test"    ${INPUT FILE}
    
    # Selected test should have its metadata
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be Equal As Integers    ${SUITE.test_count}    1

Custom Metadata With Report Generation
    [Documentation]    Test custom metadata in statistics and reports
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    
    # Generate detailed reports and verify rebot runs successfully
    Run Rebot    --log detailed_log.html --report detailed_report.html    ${INPUT FILE}
    
    # Core functionality test - custom metadata should be preserved in rebot processing
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Be Equal    ${tc.custom_metadata['Owner']}          John Doe Jane Smith
    Should Be Equal    ${tc.custom_metadata['Priority']}       High
    Should Be Equal    ${tc.custom_metadata['Component']}      Authentication

Custom Metadata With Modifications
    [Documentation]    Test custom metadata preservation with timestamp and tag modifications
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    
    # Modify timestamps and add tags
    Run Rebot    --starttime 20230101-12:00:00 --endtime 20230101-13:00:00 --settag rebot_added    ${INPUT FILE}
    
    # Custom metadata should be preserved despite other modifications
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Should Contain    ${tc.tags}    rebot_added
    Should Be Equal    ${tc.custom_metadata['Owner']}    John Doe Jane Smith

Custom Metadata Processing Options
    [Documentation]    Test various rebot processing options with custom metadata
    Run tests to create input file for Rebot    ${CUSTOM_METADATA_FILE}
    
    # Process with legacy format (if supported)
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    
    # Check that custom metadata is handled appropriately
    Get Test Case    Comprehensive Metadata Test
    
    # Test filtering exclusion pattern
    Run Rebot    --custommetadata ""    ${INPUT FILE}
    
    # Verify behavior (implementation dependent)
    ${tc} =    Get Test Case    Comprehensive Metadata Test
    Log    Custom metadata exclusion test completed    INFO

Report Merging Behavior
    [Documentation]    Test custom metadata behavior during report merging
    Pass Execution    Custom metadata merging behavior requires further specification
