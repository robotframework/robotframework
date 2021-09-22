*** Settings ***
Suite Setup     Run Tests    --pythonpath ${ZIPLIB}    test_libraries/library_import_from_archive.robot
Resource        atest_resource.robot

*** Variables ***
${ZIPLIB}       ${CURDIR}/../../testresources/testlibs/ziplib.zip

*** Test Cases ***
Python Library From A Zip File
    Check Test Case    ${TEST NAME}
    Syslog Should Contain    Imported library 'ZipLib' with arguments [ ] (version <unknown>, class type, TEST scope, 1 keywords)
