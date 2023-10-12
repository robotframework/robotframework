*** Variables ***
${resource_file_var}         Variable from a resource file
${resource_file_var_2}       Another variable from a resource file
@{resource_file_list_var}    List variable    from a resource file

*** Keywords ***
Imported UK
    Log    This is an imported user keyword
