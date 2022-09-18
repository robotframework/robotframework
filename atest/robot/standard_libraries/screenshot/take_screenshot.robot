*** Settings ***
Suite Setup     Run tests  -l log.html -L debug  standard_libraries/screenshot/take_screenshot.robot
Force Tags      require-screenshot
Resource        atest_resource.robot

*** Test Cases ***
Screenshot Is Embedded in Log File
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Embedding In Log  ${tc.kws[0].kws[0].msgs[1]}  screenshot_1.jpg

Each Screenshot Gets Separate Index
    Check Test Case  ${TESTNAME}

Basename May Be Defined
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Embedding In Log  ${tc.kws[0].kws[0].msgs[1]}  foo_1.jpg

Basename With Extension Turns Off Index Generation
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Embedding In Log  ${tc.kws[0].kws[0].msgs[1]}  xxx.jpg
    Check Embedding In Log  ${tc.kws[1].kws[0].msgs[1]}  yyy.jpeg

Name as `pathlib.Path`
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Embedding In Log  ${tc.kws[0].msgs[1]}  name.jpg

Screenshot Width Can Be Given
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Embedding In Log  ${tc.kws[0].msgs[1]}  screenshot_1.jpg  300px

Basename With Non-existing Directories Fails
    Check Test Case  ${TESTNAME}

Without Embedding
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Linking In Log  ${tc.kws[0].msgs[1]}  no_embed.jpeg

*** Keywords ***
Check Embedding In Log
    [Arguments]  ${message}  ${path}  ${width}=800px
    Check Log Message  ${message}  <a href="${path}"><img src="${path}" width="${width}"></a>  HTML

Check Linking In Log
    [Arguments]  ${message}  ${file}
    ${path} =  Normalize Path  ${OUTDIR}/${file}
    Check Log Message  ${message}  Screenshot saved to '<a href="${file}">${path}</a>'.  HTML
