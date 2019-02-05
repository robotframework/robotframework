*** Settings ***
Resource     resources_and_variables/resources.robot
Resource     RESOURCES_AND_VARIABLES/resources.robot  # Normalize on Windows
RESOURCE     ${resource_dir}/resources2.robot
VARIABLES    resources_and_variables/variables.py
Variables    ${variables2_file}

# Arguments to variable files
VarIables    resources_and_variables/dynamic_variables.py    # No args works
variables    resources_and_variables/dynamic_variables.py    One arg works
Variables    resources_and_variables/dynamic_variables.py
...          Two args   returns invalid
Variables    resources_and_variables/dynamic_variables.py
...          More   args   raises    exception
Variables    resources_and_variables/dynamicVariables.py
...          This    ${1}    ${works}    back \\ slash    \${escaped}    ${CURDIR}

# Resources and variables in PYTHONPATH
Resource     resource_in_pythonpath.robot
resource     resvar_subdir/resource_in_pythonpath_2.robot
Variables    variables_in_pythonpath.py
Variables    resvar_subdir/variables_in_pythonpath_2.py
...          Variable from variable file    in PYTHONPATH    (version 2)

# Duplicate imports should be ignored with a message to syslog
Resource     resources_and_variables/resources.robot
Resource     ${resource_dir}/resources2.robot
Resource     ${resource_dir}/resources_imported_by_resource.robot
Variables    resources_and_variables/variables.py
Variables    ${resource_dir}/variables2.py
Variables    ${resource_dir}/variables_imported_by_resource.py
Variables    resources_and_variables/dynamic_variables.py    One arg works

# Invalid imports
Resource     non_existing.robot
Variables    non_existing.py
Resource     ${resource_dir}/empty_resource.robot
Resource     resources_and_variables/resources.robot   only one parameter allowed
Resource     test_suite_dir_with_init_file/__init__.robot
Resource     ${INIT FILE}
Resource
Variables    ${resource_dir}/invalid_variable_file.py
Variables    resources_and_variables/dynamicVariables.py    ${non_existing_var_as_arg}
Variables    resources_and_variables/invalid_list_variable.py
Variables

*** Variables ***
${resource_dir}       ${CURDIR}${/}resources_and_variables
${variables2_file}    ${resource_dir}/variables2.py
${works}              works
${INIT FILE}          ${CURDIR}/test_suite_dir_with_init_file/sub_suite_with_init_file/__INIT__.robot

*** Test Cases ***
Normal Resource Import
    [Documentation]  Test that path given in resource import is relative to the current directory and that '/' is converted to correct path separator depending on os.
    Should Be Equal  ${resources}  Variable from resources.robot
    Resources

Resource Import With Variables
    [Documentation]  Test that variables can be used in resource import path. Also test that path can be absolute.
    Should Be Equal  ${resources2}  Variable from resources2.robot
    Resources2

Normal Variable Import
    [Documentation]  Test that path given in variable import is relative to the current directory and that '/' is converted to correct path separator depending on os.
    Should Be Equal  ${variables}  Variable from variables.py
    Should Be True  @{valid_list} == ['This','is','a','list']

Not Included in __all__
    [Documentation]  FAIL Variable '\${not included}' not found.
    Log  ${not included}

Variable Import With Variables
    [Documentation]  Test that variables can be used in variable import path. Also test that path can be absolute.
    Should Be Equal  ${variables2}  Variable from variables2.py

Invalid List Variable
    [Documentation]  List variable not containing a list value causes an error
    Variable Should Not Exist  \@{invalid_list}
    Variable Should Not Exist  \${var_in_invalid_list_variable_file}

Dynamic Variable File With No Args
    Variable Should Not Exist  $no_args_vars
    Variable Should Not Exist  $one_arg_vars
    Variable Should Not Exist  $get_variables
    Log Variables
    Should Be Equal  ${dyn_no_args_get_var}  Dyn var got with no args from get_variables
    Should Be Equal  ${dyn_no_args_get_var_2}  ${2}
    Should Be Equal  @{dyn_no_args_get_var_list}[0]  one
    Should Be Equal  @{dyn_no_args_get_var_list}[1]  ${2}

Dynamic Variable File With One Arg
    Should Be Equal  ${dyn_one_arg_get_var}  Dyn var got with one arg from get_variables
    Should Be Equal  ${dyn_one_arg_get_var_False}  ${False}
    Should Be Equal  @{dyn_one_arg_get_var_list}[0]  one
    Should Be Equal  @{dyn_one_arg_get_var_list}[1]  ${False}
    ${dict} =  Set Variable  @{dyn_one_arg_get_var_list}[2]
    Should Be Equal  ${dict['dyn_no_args_get_var_2']}  ${2}

Dynamic Variable File With Variables And Backslashes In Args
    Should Be Equal  ${dyn_multi_args_getVar}  Dyn var got with multiple args from getVariables
    Should Be Equal  ${dyn_multi_args_getVar_x}  This 1 works back \\ slash \${escaped} ${CURDIR}

Resource Importing Resources
    [Documentation]  Test that resource file can import more resources. resources_imported_by_resource.robot was imported ok by resources.robot
    Should Be Equal  ${resources_imported_by_resource}  Variable from resources_imported_by_resource.robot
    Resources Imported By Resource

Resource Importing Variables
    [Documentation]  Test that resource file can import variables
    Should Be Equal  ${variables_imported_by_resource}  Variable from variables_imported_by_resource.py

Resource Importing Library
    [Documentation]  Test that resource file can import libraries
    Directory Should Exist  ${CURDIR}

Resource File In PYTHONPATH
    Should Be Equal  ${PPATH_RESFILE}  Variable from resource file in PYTHONPATH
    PPATH KW
    Should Be Equal  ${PPATH_RESFILE_2}  Variable from resource file in PYTHONPATH (version 2)
    PPATH KW 2

Variable File In PYTHONPATH
    Should Be Equal  ${PPATH_VARFILE}  Variable from variable file in PYTHONPATH
    Should Be Equal  ${PPATH_VARFILE_2}  Variable from variable file in PYTHONPATH (version 2)
    Should Be Equal  @{PPATH_VARFILE_2_LIST}[0]  Variable from variable file
    Should Be Equal  @{PPATH_VARFILE_2_LIST}[1]  in PYTHONPATH
    Should Be Equal  @{PPATH_VARFILE_2_LIST}[2]  (version 2)
