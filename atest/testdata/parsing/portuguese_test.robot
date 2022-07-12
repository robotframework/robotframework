*** Definições ***
Documentação                  Suite documentation.
Metadados                     Metadata    Value
Inicialização de Suíte        Suite Setup
Finalização de Suíte          Suite Teardown
Inicialização de Teste        Test Setup
Finalização de Teste          Test Teardown
Modelo de Teste               Test Template
Tempo Limite de Teste         1 minute
Etiquetas de Testes           test    tags
Etiquetas de Palavra-Chave    keyword    tags
Biblioteca                    OperatingSystem
Recurso                       portuguese.resource
Variável                      variables.py

*** Variáveis ***
${VARIABLE}         variable value

*** Casos de Teste ***
Test without settings
    Nothing to see here

Test with settings
    [Documentação]     Test documentation.
    [Etiquetas]        own tag
    [Inicialização]    NONE
    [Finalização]      NONE
    [Modelo]           NONE
    [Tempo Limite]     NONE
    Keyword            ${VARIABLE}

*** Palavras-Chave ***
Suite Setup
    Directory Should Exist    ${CURDIR}

Suite Teardown
    Keyword In Resource

Test Setup
    Should Be Equal    ${VARIABLE}         variable value
    Should Be Equal    ${RESOURCE FILE}    variable in resource file
    Should Be Equal    ${VARIABLE FILE}    variable in variable file

Test Teardown
    No Operation

Test Template
    [Argumentos]    ${message}
    Log    ${message}

Keyword
    [Documentação]     Keyword documentation.
    [Argumentos]       ${arg}
    [Etiquetas]        own tag
    [Tempo Limite]     1h
    Should Be Equal    ${arg}    ${VARIABLE}
    [Finalização]      No Operation

*** Comentários ***
Ignored comments.
