*** Test Cases ***
Test with messages
  Log  <h1>html</h1>  HTML
  Log  infolevelmessage
  Log  warning  WARN
  Set Log Level  TRACE
  Log  debugging  DEBUG
  Log  tracing  TRACE
  Set Log Level  INFO
  Fail  *HTML* HTML tagged content <a href='http://www.robotframework.org'>Robot Framework</a>
