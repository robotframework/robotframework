*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Finish before timeout
    ${result} =    Run Process    python    -c    print 'Hello, world!'    timeout=10s
    Should Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    Hello, world!

On timeout process is terminated by default
    [Setup]    Check Precondition    sys.version_info >= (2,6)
    ${result} =    Run Process    python    -c    import time; time.sleep(1); print 'done'
    ...    timeout=3ms    stderr=STDOUT
    Should Not Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    ${EMPTY}

On timeout process can be killed
    [Setup]    Check Precondition    sys.version_info >= (2,6)
    ${result} =    Run Process    python    -c    import time; time.sleep(1); print 'done'
    ...    timeout=0.002s    on_timeout=kill    stderr=STDOUT
    Should Not Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    ${EMPTY}

On timeout process can be left running
    ${result} =    Run Process    python    -c    import time; time.sleep(0.1); print 'done'
    ...    timeout=0.001    alias=exceed    on_timeout=CONTINUE
    Should Be Equal    ${result}    ${None}
    ${result} =    Wait For Process    handle=exceed
    Should Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    done
