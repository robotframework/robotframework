*** Settings ***
Suite Setup       Run Tests     --monitorwidth 50 --monitorc off --MonitorMarkers off    misc/pass_and_fail.robot
Force Tags        regression    pybot    jybot
Resource          console_resource.robot

*** Test Cases ***

--MonitorWidth is deprecated
    Check Stderr Contains    [ WARN ] Option '--monitorwidth' is deprecated. Use '--consolewidth' instead.
    Check Stdout Contains Regexp    \n={50}\n

--MonitorColors is deprecated
    Check Stderr Contains    [ WARN ] Option '--monitorcolors' is deprecated. Use '--consolecolors' instead.

--MonitorMarkers is deprecated
    Check Stderr Contains    [ WARN ] Option '--monitormarkers' is deprecated. Use '--consolemarkers' instead.
