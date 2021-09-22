*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/DataTypesLibrary.py
Test Template     Should Be Equal Multiline

*** Test Cases ***
Documentation
    ${MODEL}[doc]    <p>This Library has Data Types.</p>
    ...   <p>It has some in <code>__init__</code> and others in the <a href=\"#Keywords\" class=\"name\">Keywords</a>.</p>
    ...   <p>The DataTypes are the following that should be linked. <span class=\"name\">HttpCredentials</span> , <a href=\"#GeoLocation\" class=\"name\">GeoLocation</a> , <a href=\"#Small\" class=\"name\">Small</a> and <a href=\"#AssertionOperator\" class=\"name\">AssertionOperator</a>.</p>

Init Arguments
    [Template]    Verify Argument Models
    ${MODEL}[inits][0][args]     credentials: Small = one

Init docs
    ${MODEL}[inits][0][doc]     <p>This is the init Docs.</p>
    ...   <p>It links to <a href=\"#Set%20Location\" class=\"name\">Set Location</a> keyword and to <a href=\"#GeoLocation\" class=\"name\">GeoLocation</a> data type.</p>

Keyword Arguments
    [Tags]        require-py3.7
    [Template]    Verify Argument Models
    ${MODEL}[keywords][0][args]     value    operator: AssertionOperator | None = None    exp: str = something?
    ${MODEL}[keywords][1][args]     funny: bool | int | float | str | AssertionOperator | Small | GeoLocation | None = equal
    ${MODEL}[keywords][2][args]     location: GeoLocation
    ${MODEL}[keywords][3][args]     list_of_str: List[str]    dict_str_int: Dict[str, int]    Whatever: Any    *args: List[typing.Any]

TypedDict
    ${Model}[dataTypes][typedDicts][0][name]    GeoLocation
    ${Model}[dataTypes][typedDicts][0][type]    TypedDict
    ${Model}[dataTypes][typedDicts][0][doc]    <p>Defines the geolocation.</p>
    ...    <ul>
    ...    <li><code>latitude</code> Latitude between -90 and 90.</li>
    ...    <li><code>longitude</code> Longitude between -180 and 180.</li>
    ...    <li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0.</li>
    ...    </ul>
    ...    <p>Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></p>

TypedDict Items
    [Template]    NONE
    ${required}     Set Variable    ${Model}[dataTypes][typedDicts][0][items][0][required]
    IF   $required is None
        ${longitude}=    Create Dictionary    key=longitude    type=float    required=${None}
        ${latitude}=     Create Dictionary    key=latitude     type=float    required=${None}
        ${accuracy}=     Create Dictionary    key=accuracy     type=float    required=${None}
    ELSE
        ${longitude}=    Create Dictionary    key=longitude    type=float    required=${True}
        ${latitude}=     Create Dictionary    key=latitude     type=float    required=${True}
        ${accuracy}=     Create Dictionary    key=accuracy     type=float    required=${False}
    END
    FOR    ${exp}    IN    ${longitude}    ${latitude}    ${accuracy}
        FOR    ${item}    IN    @{Model}[dataTypes][typedDicts][0][items]
            IF    $exp['key'] == $item['key']
                Dictionaries Should Be Equal    ${item}    ${exp}
                Exit For Loop
            END
        END
    END

Enum
    ${Model}[dataTypes][enums][0][name]    AssertionOperator
    ${Model}[dataTypes][enums][0][type]    Enum
    ${Model}[dataTypes][enums][0][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>

Enum Members
    [Template]    NONE
    ${exp_list}    Evaluate    [{"name": "equal","value": "=="},{"name": "==","value": "=="},{"name": "<","value": "<"},{"name": ">","value": ">"},{"name": "<=","value": "<="},{"name": ">=","value": ">="}]
    FOR   ${cur}    ${exp}    IN ZIP    ${Model}[dataTypes][enums][0][members]    ${exp_list}
        Run Keyword And Continue On Failure    Dictionaries Should Be Equal    ${cur}    ${exp}
    END

*** Keywords ***
Verify Argument Models
    [Arguments]    ${arg_models}    @{expected_reprs}
    Should Be True    len($arg_models) == len($expected_reprs)
    FOR    ${arg_model}    ${expected_repr}    IN ZIP    ${arg_models}    ${expected_reprs}
       Run Keyword And Continue On Failure   Verify Argument Model    ${arg_model}    ${expected_repr}    json=True
    END
