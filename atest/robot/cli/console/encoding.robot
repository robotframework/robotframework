*** Settings ***
Resource          console_resource.robot

*** Variables ***
${STDOUT}         %{TEMPDIR}/redirect_stdout.txt
${STDERR}         %{TEMPDIR}/redirect_stderr.txt
@{COMMAND}        @{INTERPRETER.runner}
...               --output           NONE
...               --report           NONE
...               --log              NONE
...               --consolecolors    OFF
...               --pythonpath       ${CURDIR}${/}..${/}..${/}..${/}testresources${/}testlibs
...               ${DATADIR}/misc/non_ascii.robot

*** Test Cases ***
PYTHONIOENCODING is honored in console output
    ${result} =    Run Process
    ...    @{COMMAND}
    ...    env:PYTHONIOENCODING=ISO-8859-5
    ...    output_encoding=ISO-8859-5
    ...    stdout=${STDOUT}
    ...    stderr=${STDERR}
    Should Be Empty    ${result.stderr}
    # Non-ISO-8859-5 characters are replaced with `?`.
    Should Contain    ${result.stdout}    Circle is 360?, Hyv?? ??t?, ?? ? ? ? ? ? ?
    Should Contain    ${result.stdout}    ???-????? T??t ??d K?yw?rd N?m?s, Спасибо${SPACE*29}| PASS |

Invalid encoding configuration
    [Tags]    no-windows    no-osx
    ${cmd} =    Join command line
    ...    LANG=invalid
    ...    LC_TYPE=invalid
    ...    LANGUAGE=invalid
    ...    LC_ALL=invalid
    ...    PYTHONUTF8=0
    ...    @{COMMAND}
    ${result} =    Run Process
    ...    echo "redirect stdin" | ${cmd}
    ...    shell=True
    ...    stdout=${STDOUT}
    ...    stderr=${STDERR}
    Should Be Empty    ${result.stderr}
    # Non-ASCII characters are replaced with `?`.
    Should Contain    ${result.stdout}    Circle is 360?, Hyv?? ??t?, ?? ? ? ? ? ? ?
    Should Contain    ${result.stdout}    ???-????? T??t ??d K?yw?rd N?m?s, ???????${SPACE*29}| PASS |
