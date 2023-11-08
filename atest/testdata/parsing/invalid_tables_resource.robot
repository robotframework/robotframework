*** ***
This kind of tables caused bug
https://github.com/robotframework/robotframework/issues/793

***Keywords***
Keyword in valid table in resource
    Log    Kw in valid table in resource
    Directory Should Exist    ${DIR}

***Resource Error***
This stuff should be ignored

***Settings***
Library        OperatingSystem


*** Variables ***
${DIR}        ${CURDIR}
