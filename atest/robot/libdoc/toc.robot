*** Settings ***
Resource          libdoc_resource.robot

*** Test Cases ***
TOC is not replaced in model
    Run Libdoc And Parse Output    ${TESTDATADIR}/toc.py
    Doc should be
    ...    == Table of contents ==
    ...    %TOC%
    ...
    ...    = First level =
    ...
    ...    First level headers are included in TOC.
    ...
    ...    = First level again =
    ...
    ...    Yes, also this header is included.
    ...
    ...    == Second level ==
    ...
    ...    Also second level headers are included starting from RF 7.5.
    ...
    ...    === Third level ===
    ...
    ...    Third level headers aren't included.
    ...
    ...    ${SPACE * 3}== Second level again ==
    ...
    ...    This is included. Header indentation doesn't matter.
    ...
    ...    = First level once more =
    ...    == Second level once more ==
    ...
    ...    These are included.
    ...
    ...    = Just = text
    ...    here =
    ...
    ...    %TOC% isn't replaced when not alone.
    ...
    ...    Not even here:
    ...    %TOC%

TOC is replaced in HTML
    Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/toc.py
    Should Be Equal Multiline    ${MODEL}[doc]
    ...    <h3 id="Table of contents">Table of contents</h3>
    ...    <ul>
    ...    <li><a href="#First%20level">First level</a></li>
    ...    <li><a href="#First%20level%20again">First level again</a></li>
    ...    <ul>
    ...    <li><a href="#Second%20level">Second level</a></li>
    ...    <li><a href="#Second%20level%20again">Second level again</a></li>
    ...    </ul>
    ...    <li><a href="#First%20level%20once%20more">First level once more</a></li>
    ...    <ul>
    ...    <li><a href="#Second%20level%20once%20more">Second level once more</a></li>
    ...    </ul>
    ...    </ul>
    ...    <h2 id="First level">First level</h2>
    ...    <p>First level headers are included in TOC.</p>
    ...    <h2 id="First level again">First level again</h2>
    ...    <p>Yes, also this header is included.</p>
    ...    <h3 id="Second level">Second level</h3>
    ...    <p>Also second level headers are included starting from RF 7.5.</p>
    ...    <h4 id="Third level">Third level</h4>
    ...    <p>Third level headers aren't included.</p>
    ...    <h3 id="Second level again">Second level again</h3>
    ...    <p>This is included. Header indentation doesn't matter.</p>
    ...    <h2 id="First level once more">First level once more</h2>
    ...    <h3 id="Second level once more">Second level once more</h3>
    ...    <p>These are included.</p>
    ...    <p>= Just = text here =</p>
    ...    <p>%TOC% isn't replaced when not alone.</p>
    ...    <p>Not even here: %TOC%</p>
