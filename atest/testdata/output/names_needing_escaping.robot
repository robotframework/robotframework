*** Variables ***
${var}     value

*** Test Case ***
"Quotes"
    "Quotes"

Tag <pre>
    Tag <pre>

And &
    And &

Backslashes \\ \\\\ \\\\\\ \\\\\\\\
    Backslashes \ \\ \\\ \\\\

Variable \${var}
    Variable ${var}

Escaped \\\${var}
    Escaped \${var}

Newline \\n and Tab \\t
    Newline \n and Tab \t

*** Keyword ***
"Quotes"
    No Operation

Tag <pre>
    No Operation

And &
    No Operation

Backslashes \ \\ \\\ \\\\
    No Operation

Variable ${var}
    No Operation

Escaped \${var}
    No Operation

Newline \n and Tab \t
    No Operation
