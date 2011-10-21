#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


TEMPLATE = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="RIDE" />
<meta name="rf-template" content="False" />
<style type="text/css">
html {
  font-family: Arial,Helvetica,sans-serif;
  background-color: white;
  color: black;
}
table {
  border-collapse: collapse;
  empty-cells: show;
  margin: 1em 0em;
  border: 1px solid black;
}
th, td {
  border: 1px solid black;
  padding: 0.1em 0.2em;
  height: 1.5em;
  width: 12em;
}
th {
  background-color: rgb(192, 192, 192);
  color: black;
  height: 1.7em;
  font-weight: bold;
  text-align: center;
  letter-spacing: 0.1em;
}
td.name {
  background-color: rgb(240, 240, 240);
  letter-spacing: 0.1em;
}
td.name, th.name {
  width: 10em;
}
</style>
<title>%(NAME)s</title>
</head>
<body>
<h1>%(NAME)s</h1>
<table id="settings" border="1"></table>
<table id="variables" border="1"></table>
<table id="testcases" border="1"></table>
<table id="keywords" border="1"></table>
</body>
</html>
"""
