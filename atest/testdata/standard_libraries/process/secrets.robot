*** Settings ***
Suite Setup       Set Environment Variable    v1    system
Resource          process_resource.robot

*** Variables ***
@{COMMAND}           python    -c    import os; print(' '.join([os.getenv('v1', '-'), os.getenv('v2', '-'), os.getenv('v3', '-')]))
${SECRET: Secret}    %{=This is secret!}

*** Test Cases ***
Run Process with Secret Argument
    ${result} =    Run Process    python    ${SCRIPT}    ${SECRET}
    Script result should equal    ${result}    stdout=This is secret!

Run Process with Mixed Arguments Including Secret
    ${result} =    Run Process    python    ${SCRIPT}    public_arg    ${SECRET}
    Script result should equal    ${result}    stdout=public_arg    stderr=This is secret!

Run Process with Stdin as Secret
    ${result} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=${SECRET}    cwd=%{TEMPDIR}
    Script result should equal    ${result}    stdout=This is secret!    stderr=

Start Process with Secret Argument
    ${handle} =    Start Process    python    ${SCRIPT}    ${SECRET}
    ${result} =    Wait For Process    ${handle}
    Script result should equal    ${result}    stdout=This is secret!

Start Process with Stdin as Secret
    ${handle} =    Start Process    python    -c    import sys; print(sys.stdin.read())    stdin=${SECRET}    cwd=%{TEMPDIR}
    ${result} =    Wait For Process    ${handle}
    Script result should equal    ${result}    stdout=This is secret!    stderr=

Secret in environment variable via env Dict
    ${env} =    Create environ    v1=${SECRET}
    ${result} =    Run Process    @{COMMAND}    env=${env}
    Script result should equal    ${result}    stdout=This is secret! - -    stderr=

Secret in environment variable via env:name Syntax
    ${result} =    Run Process    @{COMMAND}    env:v2=${SECRET}
    Script result should equal    ${result}    stdout=system This is secret! -    stderr=

Multiple Secrets in environment variables
    ${result} =    Run Process    @{COMMAND}    env:v1=${SECRET}    env:v2=XX    env:v3=${SECRET}
    Script result should equal    ${result}    stdout=This is secret! XX This is secret!    stderr=
