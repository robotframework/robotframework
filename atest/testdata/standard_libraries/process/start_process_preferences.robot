*** Settings ***
Library           Process
Library           OperatingSystem
Library           CustomLib.py
Resource          process_resource.robot

*** Test Cases ***
Explicitly run Operating System library keyword
    ${handle}=     OperatingSystem.Start Process    python -c "import os; print os.path.abspath(os.curdir);"
    ${out}=        Read Process Output

Explicitly run Process library keyword
    ${handle}=     Process.Start Process            python -c "import os; print os.path.abspath(os.curdir);"      shell=True
    ${out}=        Wait For Process

Implicitly run Process library keyword
    ${handle}=     Start Process                    python -c "import os; print os.path.abspath(os.curdir);"      shell=True
    ${out}=        Wait For Process
    ${out2}=       Get Process Id                          # Should call CustomLib keyword
    Should Match   ${out2}    The Pid
    ${items}=      Count Items In Directory    ${CURDIR}   # OperatingSystem keywords should be reachable

Implicitly run Operating System library keyword when library search order is set
    Set Library Search Order     OperatingSystem
    ${handle}=     Start Process    python -c "import os; print os.path.abspath(os.curdir);"
    ${out}=        Read Process Output
    [Teardown]  Set Library Search Order  ${EMPTY}

Process switch
    OperatingSystem.Start Process   python -c "print 'hello'"  alias=op1
    OperatingSystem.Start Process   python -c "print 'hello'"  alias=op2
    Start Process  python -c "print 'hello'"  shell=True  alias=p1
    Start Process  python -c "print 'hello'"  shell=True  alias=p2
    Switch Process  p1
    Switch Process  p2
    OperatingSystem.Switch Process  op1
    OperatingSystem.Switch Process  op2
