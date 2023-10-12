*** Settings ***
Suite Setup       Set And Remove Tags
Force Tags        force-init    remove-me-please

*** Keywords ***
Set And Remove Tags
    Set Tags    set-init    remove-me-too
    Remove Tags    remove-me-*
