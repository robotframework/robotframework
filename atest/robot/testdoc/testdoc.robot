*** Settings ***
Resource        testdoc_resource.robot

*** Test Cases ***
One input
    Run TestDoc    ${INPUT 1}
    Testdoc Should Contain    "name":"First One"    "title":"Normal"    "numberOfTests":2
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Variables and imports are not processes
    Run TestDoc    ${INPUT 3}
    Testdoc Should Contain    "name":"Testdoc"    "title":"Testdoc"    "numberOfTests":1    "doc":"<p>Documentation with $\{CURDIR}\\x3c/p>"
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Many inputs
    Run TestDoc    --exclude    t1    --title    Nön-ÄSCII
    ...    ${INPUT 1}    ${INPUT2}    ${INPUT 3}
    Testdoc Should Contain    "name":"Normal &amp; Suites &amp; Testdoc"    "title":"Nön-ÄSCII"    "numberOfTests":7
    Testdoc Should Not Contain    "name":"Suite4 First"
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Argument file
    Create Argument File    ${ARGFILE 1}
    ...    --name Testing argument file
    ...    --doc Overridden from cli
    ...    ${EMPTY}
    ...    \# I'm a comment and I'm OK! And so are empty rows around me too.
    ...    ${EMPTY}
    ...    --exclude t2
    Create Argument File    ${ARGFILE 2}
    ...    --title My title!
    ...    ${INPUT 1}
    Run TestDoc
    ...    --name    Overridden by argument file
    ...    --argumentfile    ${ARGFILE 1}
    ...    --doc    The doc
    ...    -A    ${ARGFILE 2}
    Testdoc Should Contain    "name":"Testing argument file"    "title":"My title!"    "numberOfTests":1
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile
