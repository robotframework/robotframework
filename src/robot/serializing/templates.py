#  Copyright 2008-2010 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


_STYLE = '''
<style media="all" type="text/css">
  /* Generic styles */
  body {
    font-family: sans-serif;
    font-size: 0.8em;
    color: black;
    padding: 6px;
  }
  h2 {
    margin-top: 1.2em;
  }
  /* Statistics Table */
  table.statistics {
    width: 58em;
    border: 1px solid black;
    border-collapse: collapse;
    empty-cells: show;
    margin-bottom: 1em;
  }
  table.statistics td, table.statistics th {
    border: 1px solid black;
    padding: 1px 4px;
    margin: 0px;
  }
  table.statistics th {
    background: #C6C6C6;
  }
  .col_stat_name {
    width: 40em;
  }
  .col_stat {
    width: 3em;
    text-align: center;
  }
  .stat_name {
    float: left;
  }
  .stat_name a, .stat_name span {
    font-weight: bold;
  }
  .tag_links {
    font-size: 0.9em;
    float: right;
    margin-top: 0.05em;
  }
  .tag_links span {
    margin-left: 0.2em;
  }
  /* Statistics Table Graph */
  .pass_bar {
    background: #00f000;
  }
  .fail_bar {
    background: red;
  }
  .no_tags_bar {
    background: #E9E9E9;
  }
  .graph {
    position: relative;
    border: 1px solid black;
    width: 11em;
    height: 0.75em;
    padding: 0px;
    background: #E9E9E9;
  }
  .graph b {
    display: block;
    position: relative;
    height: 100%;
    float: left;
    font-size: 4px;  /* to make graphs thin also in IE */
  }
  /* Tables in documentation */
  table.doc {
    border: 1px solid gray;
    background: transparent;
    border-collapse: collapse;
    empty-cells: show;
    font-size: 0.9em;
  }
  table.doc td {
    border: 1px solid gray;
    padding: 0.1em 0.3em;
    height: 1.2em;
  }
  /* Misc Styles */
  .not_available {
    color: gray;      /* no grey in IE */
    font-weight: normal;
  }
  .parent_name {
    font-size: 0.7em;
    letter-spacing: -0.07em;
  }
  a:link, a:visited {
    text-decoration: none;
    color: blue;
  }
  a:hover, a:active {
    text-decoration: underline;
    color: purple;
  }
  /* Headers */
  .header {
    width: 58em;
    margin: 6px 0px;
  }
  h1 {
    margin: 0px;
    width: 70%;
    float: left;
  }
  .times {
    width: 29%;
    float: right;
    text-align: right;
  }
  .generated_time, .generated_ago {
    font-size: 0.9em;
  }
  .spacer {
    font-size: 0.8em;
    clear: both;
  }
  /* Status text colors */
  .error, .fail {
    color: red;
  }
  .pass {
    color: #009900;
  }
  .warn {
    color: #FFCC00;
  }
  .not_run {
    color: #663300;
  }
</style>
<style media="print" type="text/css">
  body {
    background: white;
    padding: 0px;
    font-size: 8pt;
  }
  a:link, a:visited {
    color: black;
  }
  .header, table.details, table.statistics {
    width: 100%;
  }
  .generated_ago, .expand {
    display: none;
  }
</style>
'''[1:-1]


_FUNCTIONS = '''
<!-- FUNCTION meta ${version} -->
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Expires" content="Mon, 20 Jan 2001 20:01:21 GMT" />
<meta name="generator" content="${version}" />
<!-- END FUNCTION -->
<!-- FUNCTION generate_header ${title} -->
<div class="header">
  <h1>${title}</h1>
  <div class="times">
    <span class="generated_time">Generated<br />${GENTIME_STR}</span><br />
	<span class="generated_ago">
<script type="text/javascript">
  function get_end(number) {
    if (number == 1) { return ' ' }
    return 's '
  }
  function get_sec_str(secs) {
    return secs + ' second' + get_end(secs)
  }
  function get_min_str(mins) {
    return mins + ' minute' + get_end(mins)
  }
  function get_hour_str(hours) {
    return hours + ' hour' + get_end(hours)
  }
  function get_day_str(days) {
    return days + ' day' + get_end(days)
  }
  function get_year_str(years) {
    return years + ' year' + get_end(years)
  }
  generated = ${GENTIME_INT}
  current = Math.round(new Date().getTime() / 1000)  // getTime returns millis
  elapsed = current - generated
  // elapsed should only be negative if clocks are not in sync
  if (elapsed < 0) {
    elapsed = Math.abs(elapsed)
    prefix = '- '
  }
  else {
    prefix = ''
  }
  secs  = elapsed % 60
  mins  = Math.floor(elapsed / 60) % 60
  hours = Math.floor(elapsed / (60*60)) % 24
  days  = Math.floor(elapsed / (60*60*24)) % 365
  years = Math.floor(elapsed / (60*60*24*365))
  if (years > 0) {
    // compencate the effect of leap years (not perfect but should be enough)
    days = days - Math.floor(years / 4)
    if (days < 0) { days = 0 }
    output = get_year_str(years) + get_day_str(days)
  }
  else if (days > 0) {
    output = get_day_str(days) +  get_hour_str(hours)
  }
  else if (hours > 0) {
    output = get_hour_str(hours) + get_min_str(mins)
  }
  else if (mins > 0) {
    output = get_min_str(mins) + get_sec_str(secs)
  }
  else {
    output = get_sec_str(secs)
  }
  document.write(prefix + output + 'ago')
</script>
    </span>
  </div>
</div>
<div class="spacer">&nbsp;</div>
<!-- END FUNCTION -->
'''


LOG = '''%(FUNCTIONS)s
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<!-- CALL meta ${version} -->
%(STYLE)s
<style media="all" type="text/css">
  /* Tables */
  body {
    background: white;
  }
  table.suite, table.errors {
    width: 100%%;
    border: 1px solid gray;  /* no grey in IE */
    margin: 0.2em 0em;
    padding: 0.2em;
  }
  table.errors td.level {
    font-weight: bold;
    width: 4em;
    text-align: center;
    vertical-align: top;
  }
  table.errors td.time {
    width: 10em;
    vertical-align: top;
  }
  table.test {
    width: 100%%;
    border: 1px dashed gray;
    margin: 0.2em 0em;
    padding: 0.2em;
  }
  table.metadata, table.keyword, table.messages {
    margin-left: 1.1em;
    width: 100%%;
  }
  table.metadata, table.messages {
    margin-right: 2em;
  }
  table.keyword table.metadata {
    font-size: 0.9em;
    margin-left: 1.4em;
  }
  table.messages {
    font-family: monospace;
    font-size: 1.2em;
  }
  table.metadata th {
    width: 12em;
    text-align: left;
    vertical-align: top;
  }
  table.metadata td {
    padding-left: 0.5em;
    vertical-align: top;
  }
  table.messages td {
    vertical-align: top;
  }
  table.messages td.time {
    width: 6em;
    letter-spacing: -0.05em;
  }
  table.messages td.level {
    width: 4em;
    text-align: center;
  }
  /* Folding buttons */
  div.foldingbutton {
    text-align: center;
    line-height: 0.8em;
    font-size: 0.8em;
    margin: 0.2em 0.4em 0em 0.1em;
    height: 0.9em;
    width: 0.9em;
    float: left;
    text-decoration: none;
    font-weight: bold;
    border: 1px solid black;
    border: 1px solid black;
  }
  div.foldingbutton:hover {
    background: yellow;
  }
 .expand {
   float: right;
   margin-right: 0.5em;
   font-size: 0.8em;
  }
  /* Test, suite and kw names */
  .name, .splitname {
    font-weight: bold;
    text-decoration: none;
  }
  a.name:hover {
    text-decoration: none;
    color: black;
  }
</style>
<script type="text/javascript">
    function toggle_child_visibility(element_id) {
        if (document.getElementById(element_id + '_children') != null) {
            toggle_visibility(element_id + '_children')
        }
        else {
            toggle_visibility(element_id)
        }
        if (document.getElementById(element_id + '_foldlink') != null) {
            toggle_visibility(element_id + '_foldlink')
        }
        if (document.getElementById(element_id + '_unfoldlink') != null) {
            toggle_visibility(element_id + '_unfoldlink')
        }
    }
    function toggle_visibility(element_id) {
        var element = document.getElementById(element_id)
        if (element == null) {
            return
        }
        if (element.style.display == 'none') {
            element.style.display = 'block'
        }
        else {
            element.style.display = 'none'
        }
    }
    function expand_all_children(element_id) {
        var elements = document.getElementById(element_id).getElementsByTagName('div')
        for (var i=0; i<elements.length; i++) {
            var element = elements[i]
            if (element.className == 'indent' && element.style.display == 'none') {
                toggle_child_visibility(element.getAttribute('id').replace(/_children/, ''))
            }
        }
    }
    function open_element_by_url() {
        var name = get_element_name_from_url()
        if (name != null) {
            set_element_visible(name)
            window.location.hash = name  // does not seem to work with Opera
        }
    }
    function get_element_name_from_url() {
        var hash = window.location.hash
        if (hash == '' || hash == '#' || hash == null) {
            return null
        }
        return hash.slice(1).replace(/%%20/g, ' ')
    }
    function set_element_visible(id_or_name) {
        var element = document.getElementById(id_or_name)
        if (element) {
            open_parents(element)
            return
        }
        var elements = document.getElementsByName(id_or_name)
        for (var i=0; i<elements.length; i++) {
            open_parents(elements[i])
        }
    }
    // Find right type of parent element, open it and its parents
    function open_parents(element) {
        var parent = element.parentNode
        if (!parent) {
            return
        }
        // Find a parent table with id
        while (parent.nodeName != 'TABLE' || parent.getAttribute('id') == null) {
            parent = parent.parentNode
            if (!parent) {
               return
            }
        }
        var element_id = parent.getAttribute('id')
        if (document.getElementById(element_id+'_children').style.display == 'none') {
            toggle_child_visibility(element_id)
        }
        open_parents(parent)
    }
</script>

<title>${title}</title>
</head>
<body onload="open_element_by_url()">
<!-- CALL generate_header ${title} -->
''' % {'STYLE': _STYLE, 'FUNCTIONS': _FUNCTIONS}


REPORT = '''%(FUNCTIONS)s
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<!-- CALL meta ${version} -->
<style media="all" type="text/css">
  body {
    background: ${BACKGROUND};
  }
  /* Generic Table Styles */
  table {
    background: white;
    border: 1px solid black;
    border-collapse: collapse;
    empty-cells: show;
    margin: 0px 1px;
  }
  th, td {
    border: 1px solid black;
    padding: 1px 5px;
  }
  th {
    background: #C6C6C6;
    color: black;
  }
  /* Test by Suite/Tag Tables */
  table.tests_by_suite, table.tests_by_tag {
    width: 100%%;
  }
  .col_name {
    width: 13em;
    font-weight: bold;
  }
  .col_doc {
    min-width: 13em;
  }
  .col_tags {
    width: 10em;
  }
  .col_crit {
    width: 2em;
    text-align: center;
  }
  .col_status {
    width: 3.5em;
    text-align: center;
  }
  .col_msg {
    min-width: 13em;
  }
  .col_times {
    width: 9em;
  }
  td.col_times{
    text-align: right;
  }
  .suite_row, .tag_row{
    background: #E9E9E9;
  }
  .meta_name {
    font-weight: bold;
  }
  /* Details Table */
  table.details {
    width: 58em;
  }
  table.details th {
    background: white;
    width: 9em;
    text-align: left;
    vertical-align: top;
    padding-right: 1em;
    border: none;
    padding: 2px 4px;
  }
  table.details td {
    vertical-align: top;
    border: none;
    padding: 2px 4px;
  }
  .status_fail {
    color: red;
    font-weight: bold;
  }
  .status_pass {
    color: #009900;
  }
</style>
%(STYLE)s
<title>${title}</title>
</head>
<body>
<!-- CALL generate_header ${title} -->
<h2>Summary Information</h2>

<table class="details">
<tr>
  <th>Status:</th>
<!-- IF ${SUITE.all_stats.failed} == 0 -->
  <td class="status_pass">All tests passed</td>
<!-- END IF -->
<!-- IF ${SUITE.all_stats.failed} != 0 and ${SUITE.critical_stats.failed} == 0 -->
  <td class="status_pass">All critical tests passed</td>
<!-- END IF -->
<!-- IF ${SUITE.critical_stats.failed} == 1 -->
  <td class="status_fail">1 critical test failed</td>
<!-- END IF -->
<!-- IF ${SUITE.critical_stats.failed} > 1 -->
  <td class="status_fail">${SUITE.critical_stats.failed} critical tests failed</td>
<!-- END IF -->
</tr>
<!-- IF ${SUITE.htmldoc.__len__()} > 0 -->
  <tr><th>Documentation:</th><td>${SUITE.htmldoc}</td></tr>
<!-- END IF -->
<!-- FOR ${meta} IN ${SUITE.get_metadata(html=True)} -->
  <tr><th>${meta[0]}:</th><td>${meta[1]}</td></tr>
<!-- END FOR -->
<!-- IF '${SUITE.starttime}' != 'N/A' -->
  <tr><th>Start Time:</th><td>${SUITE.starttime}</td></tr>
<!-- END IF -->
<!-- IF '${SUITE.endtime}' != 'N/A' -->
  <tr><th>End Time:</th><td>${SUITE.endtime}</td></tr>
<!-- END IF -->
<tr><th>Elapsed Time:</th><td>${ELAPSEDTIME}</td></tr>
</table>
''' % {'STYLE': _STYLE, 'FUNCTIONS': _FUNCTIONS}


del _STYLE
del _FUNCTIONS
