*** Settings ***
Suite Setup      Generate doc using Markdown source
Test Template    Doc should contain
Resource         libdoc_resource.robot

*** Test Cases ***
Basic formatting
    Basic Markdown formatting such as <strong>bold</strong>, <em>italics</em> and <code>code</code> works as expected.

Linking
    Normal Markdown <a href="http://example.com">inline</a> and <a href="http://example.com" title="An &quot;example&quot;!">reference</a> links are supported.
    URLs like <a href="http://example.com">http://example.com</a> are automatically linkified as a custom feature.
    ...    Surrounding URLs with angle brackets like <a href="http://example.com">http://example.com</a> works too.

Automatic reference targets
    Keywords like <a href="#References" title="&quot;References&quot; keyword">References</a> and <a href="#Admonitions" title="&quot;Admonitions&quot; keyword">admonitions</a>.
    Headers in the library introduction like <a href="#linking" title="&quot;Linking&quot; section">linking</a>, <a href="#basics" title="&quot;Basics&quot; section">Basics</a>
    ...    \ \ and <a href="#reference-w-special-chars" title="&quot;Reference w/ :special: &quot;chars&quot;?&quot; section">Reference w/ :special: "chars"?</a>.
    Predefined targets like <a href="#Introduction" title="&quot;Introduction&quot; section">Introduction</a> and <a href="#Keywords" title="&quot;Keywords&quot; section">keywords</a>.
    We can link to predefined targets like <a href="#Introduction" title="&quot;Introduction&quot; section">introduction</a>, to intro headers
    ...    like <a href="#linking" title="&quot;Linking&quot; section">linking</a>, to keywords like <a href="#Admonitions" title="&quot;Admonitions&quot; keyword">Admonitions</a> and to types like <a href="#type-integer" title="&quot;integer&quot; type">int</a>
    ...    and <a href="#type-list" title="&quot;list&quot; type">list</a>.
    ...    model=${MODEL}[keywords][2]

Custom references defined in introduction work also with keywords
    Custom references defined in introduction like <a href="http://example.com" title="An &quot;example&quot;!">reference</a> work too!
    ...    model=${MODEL}[keywords][2]

Unordered lists
    <ul>\n<li>First unordered item.</li>\n<li>Second item.</li>\n</ul>
    ...    model=${MODEL}[keywords][1]

Ordered lists
    <ol>\n<li>First ordered item.</li>\n<li>Second item.</li>\n</ol>
    ...    model=${MODEL}[keywords][1]

Nested lists
    <ol>
    ...    <li>First item in an ordered list.<ul>
    ...    <li>Nested unordered item.</li>
    ...    <li>Another nested item.</li>
    ...    </ul>
    ...    </li>
    ...    <li>Second item.<ol>
    ...    <li>Nested ordered item.</li>
    ...    <li>Another nested item.</li>
    ...    </ol>
    ...    </li>
    ...    </ol>
    ...    model=${MODEL}[keywords][1]
    <ul>
    ...    <li>First item in an unordered list.<ul>
    ...    <li>Nested unordered item.</li>
    ...    <li>Another nested item.</li>
    ...    </ul>
    ...    </li>
    ...    <li>Second item.<ol>
    ...    <li>Nested ordered item.</li>
    ...    <li>Another nested item.</li>
    ...    </ol>
    ...    </li>
    ...    </ul>
    ...    model=${MODEL}[keywords][1]

Tables
    <table>
    ...    <thead>
    ...    <tr>
    ...    <th>Header 1</th>
    ...    <th>Header 2</th>
    ...    <th>Header 3</th>
    ...    </tr>
    ...    </thead>
    ...    <tbody>
    ...    <tr>
    ...    <td>item 1.1</td>
    ...    <td>item 2.1</td>
    ...    <td>item 3.1</td>
    ...    </tr>
    ...    <tr>
    ...    <td>item 1.2</td>
    ...    <td>item 2.2</td>
    ...    <td>item 3.2</td>
    ...    </tr>
    ...    </tbody>
    ...    </table>
    ...    model=${MODEL}[keywords][4]
    <table>
    ...    <thead>
    ...    <tr>
    ...    <th style="text-align: left;">Left</th>
    ...    <th style="text-align: center;">Center</th>
    ...    <th style="text-align: right;">Right</th>
    ...    </tr>
    ...    </thead>
    ...    <tbody>
    ...    <tr>
    ...    <td style="text-align: left;">1234567890</td>
    ...    <td style="text-align: center;">1234567890</td>
    ...    <td style="text-align: right;">1234567890</td>
    ...    </tr>
    ...    </tbody>
    ...    </table>
    ...    model=${MODEL}[keywords][4]

Syntax highlighting
    <div class="code"><pre><span></span><code><span class="gh">*** Test Cases ***</span>
    ...    <span class="gu">Example</span>
    ...    <span class="p"> \ \ \ </span><span class="nf">Keyword</span><span class="p"> \ \ \ </span><span class="s">arg</span>
    ...    </code></pre></div>
    ...    model=${MODEL}[keywords][3]
    <span class="c1"># This is comment in code, not a Markdown header!</span>
    ...    model=${MODEL}[keywords][3]
    <div class="code"><pre><span></span><code><span class="nb">print</span><span class="p">(</span><span class="s2">&quot;Fenced blocks are more commonly used.&quot;</span><span class="p">)</span>
    ...    </code></pre></div>
    ...    model=${MODEL}[keywords][3]

Admonitions
    <div class="admonition note">
    ...    <p class="admonition-title">Note</p>
    ...    <p>Admonitions are provided by the <code>admonition</code> plugin.</p>
    ...    <p>We need to make sure to add custom styles to make them render nicely.</p>
    ...    </div>
    ...    model=${MODEL}[keywords][0]
    <div class="admonition warning">
    ...    <p class="admonition-title">Interoperability risk!</p>
    ...    <p>Admonitions are not standard Markdown. Don't use them if you want good
    ...    interoperability with other Markdown tools.</p>
    ...    </div>
    ...    model=${MODEL}[keywords][0]

Table of contents
    <div class="toc">
    ...    <ul>
    ...    <li><a href="#basic-formatting">Basic formatting</a></li>
    ...    <li><a href="#linking">Linking</a><ul>
    ...    <li><a href="#link-syntax">Link syntax</a></li>
    ...    <li><a href="#automatic-reference-targets">Automatic reference targets</a></li>
    ...    <li><a href="#reference-w-special-chars">Reference w/ :special: "chars"?</a></li>
    ...    </ul>
    ...    </li>
    ...    <li><a href="#advanced-syntax">Advanced syntax</a></li>
    ...    <li><a href="#table-of-contents">Table of contents</a><ul>
    ...    <li><a href="#basics">Basics</a></li>
    ...    <li><a href="#differences-to-robot-format">Differences to Robot format</a></li>
    ...    </ul>
    ...    </li>
    ...    </ul>
    ...    </div>

Lines starting with `#` in code blocks are not considered headers
    <code># This is not a header!
    ...    </code>
    <code><span class="c1"># This is not a header either!</span>
    ...    </code>

Table of contents in keyword documentation
    <div class="toc">
    ...    <ul>
    ...    <li><a href="#where-it-works">Where it works?</a></li>
    ...    <li><a href="#where-to-learn-more">Where to learn more?</a></li>
    ...    </ul>
    ...    </div>
    ...    model=${MODEL}[keywords][5]

*** Keywords ***
Generate doc using Markdown source
    Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/MarkdownFormat.py

Doc should contain
    [Arguments]    @{content}    ${model}=${MODEL}
    VAR    ${content}    @{content}    separator=\n
    Should Contain    ${model}[doc]    ${content}
