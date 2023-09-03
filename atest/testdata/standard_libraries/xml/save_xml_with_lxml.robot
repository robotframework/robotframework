*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Test Setup        Remove File    ${OUTPUT}
Suite Teardown    Remove File    ${OUTPUT}
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Variables ***
${SIMPLE SAVED}       <root><child id="1">text</child><c2><gc/></c2></root>
${NON-ASCII}          <hyvää>yötä</hyvää>
${NON-ASCII SAVED}    <hyv&#228;&#228;>y&#246;t&#228;</hyv&#228;&#228;>

*** Test Cases ***
Save XML Element
    ${xml} =    Parse XML    ${SIMPLE}
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    ${SIMPLE SAVED}

Save XML String
    Save XML    ${SIMPLE}    ${OUTPUT}
    XML Content Should Be    ${SIMPLE SAVED}

Save XML File
    Save XML    ${TEST}    ${OUTPUT}
    Elements Should Be Equal    ${TEST}    ${OUTPUT}

Save XML Using Custom Encoding
    Save XML    ${SIMPLE}    ${OUTPUT}    encoding=US-ASCII
    XML Content Should Be    ${SIMPLE SAVED}    encoding=US-ASCII

Save Non-ASCII XML
    Save XML    ${NON-ASCII}    ${OUTPUT}
    XML Content Should Be    ${NON-ASCII}

Save Non-ASCII XML Using Custom Encoding
    Save XML    ${NON-ASCII}    ${OUTPUT}    ISO-8859-1
    XML Content Should Be    ${NON-ASCII}    ISO-8859-1

Save to `pathlib.Path`
    Save XML    ${SIMPLE}    ${{pathlib.Path($OUTPUT)}}
    XML Content Should Be    ${SIMPLE SAVED}

Save to Invalid File
    [Documentation]    FAIL REGEXP: (IOError|IsADirectoryError|PermissionError): .*
    Save XML    ${SIMPLE}    %{TEMPDIR}

Save Using Invalid Encoding
    [Documentation]    FAIL STARTS: LookupError:
    Save XML    ${SIMPLE}    ${OUTPUT}    encoding=invalid

Save Non-ASCII Using ASCII
    Save XML    ${NON-ASCII}    ${OUTPUT}    ASCII
    XML Content Should Be    ${NON-ASCII SAVED}   ASCII

Doctype is preserved
    Save XML    <!DOCTYPE foo><foo/>    ${OUTPUT}
    XML Content Should Be    <!DOCTYPE foo>\n<foo/>
    Save XML    <!DOCTYPE bar SYSTEM "bar.dtd">\n<bar>baari</bar>    ${OUTPUT}
    XML Content Should Be    <!DOCTYPE bar SYSTEM "bar.dtd">\n<bar>baari</bar>
    Save XML    <!DOCTYPE foo><foo/>    ${OUTPUT}    encoding=ASCII
    XML Content Should Be    <!DOCTYPE foo>\n<foo/>    encoding=ASCII

Comments and processing instructions are removed
    ${xml} =    Replace String    ${SIMPLE}    <    <!--c--><?p?><
    ${xml} =    Replace String    ${xml}    >    ><!--c--><?p?>
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    ${SIMPLE SAVED}

Element can be further modified after saving
    ${xml} =    Parse XML    <root><child>text</child></root>
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    <root><child>text</child></root>
    Remove Element    ${xml}    child
    Add Element    ${xml}    <new>elem</new>
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    <root><new>elem</new></root>

Element with namespaces can be further modified after saving
    ${xml} =    Parse XML    <root xmlns="xxx"><child>text</child></root>
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    <root xmlns="xxx"><child>text</child></root>
    Remove Element    ${xml}    child
    Add Element    ${xml}    <new>elem</new>
    Save XML    ${xml}    ${OUTPUT}
    XML Content Should Be    <root xmlns="xxx"><new>elem</new></root>
