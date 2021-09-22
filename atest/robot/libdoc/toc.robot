*** Settings ***
Resource          libdoc_resource.robot

*** Test Cases ***
Simple TOC
   Run Libdoc And Parse Output    ${TESTDATADIR}/toc.py
   Doc should be
   ...    == Table of contents ==
   ...    - `First entry`
   ...    - `Second`
   ...    - `Third=entry`
   ...    - `Keywords`
   ...
   ...    = First entry =
   ...
   ...    = Second =
   ...    == Sub sections ==
   ...    === are not included ===
   ...
   ...    = \ Third=entry \ \ =
   ...
   ...    = Just = text
   ...    here =

Simple TOC without keywords
   Run Libdoc And Parse Output    ${TESTDATADIR}/toc_no_keywords.py
   Doc should be
   ...    == Table of contents ==
   ...    - `First entry`
   ...    - `Second`
   ...    - `Third=entry`
   ...
   ...    = First entry =
   ...
   ...    = Second =
   ...    == Sub sections ==
   ...    === are not included ===
   ...
   ...    = \ Third=entry \ \ =
   ...
   ...    = Just = text
   ...    here =

TOC with inits and tags
   Run Libdoc And Parse Output    ${TESTDATADIR}/TOCWithInitsAndKeywords.py
   Doc should be
   ...    = First entry =
   ...
   ...    TOC in somewhat strange place.
   ...
   ...    - `First entry`
   ...    - `Second`
   ...    - `3`
   ...    - `Importing`
   ...    - `Keywords`
   ...
   ...    = Second =
   ...
   ...    ${SPACE * 9}= 3 =
   ...
   ...    %TOC% not replaced here

TOC with inits and tags and DataTypes
   Run Libdoc And Parse Output    ${TESTDATADIR}/TOCWithInitsAndKeywordsAndDataTypes.py
   Doc should be
   ...    = First entry =
   ...
   ...    TOC in somewhat strange place.
   ...
   ...    - `First entry`
   ...    - `Second`
   ...    - `3`
   ...    - `Importing`
   ...    - `Keywords`
   ...    - `Data types`
   ...
   ...    = Second =
   ...
   ...    ${SPACE * 9}= 3 =
   ...
   ...    %TOC% not replaced here

TOC in generated HTML
   Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/TOCWithInitsAndKeywords.py
   Should Be Equal Multiline    ${MODEL}[doc]
   ...    <h2 id="First entry">First entry</h2>
   ...    <p>TOC in somewhat strange place.</p>
   ...    <ul>
   ...    <li><a href="#First%20entry" class="name">First entry</a></li>
   ...    <li><a href="#Second" class="name">Second</a></li>
   ...    <li><a href="#3" class="name">3</a></li>
   ...    <li><a href="#Importing" class="name">Importing</a></li>
   ...    <li><a href="#Keywords" class="name">Keywords</a></li>
   ...    </ul>
   ...    <h2 id="Second">Second</h2>
   ...    <h2 id="3">3</h2>
   ...    <p>%TOC% not replaced here</p>
