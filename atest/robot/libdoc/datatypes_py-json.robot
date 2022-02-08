*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/DataTypesLibrary.py
Test Template     Should Be Equal Multiline

*** Test Cases ***
Documentation
    ${MODEL}[doc]    <p>This Library has Data Types.</p>
    ...   <p>It has some in <code>__init__</code> and others in the <a href="#Keywords" class="name">Keywords</a>.</p>
    ...   <p>The DataTypes are the following that should be linked. <span class="name">HttpCredentials</span> , <a href="#GeoLocation" class="name">GeoLocation</a> , <a href="#Small" class="name">Small</a> and <a href="#AssertionOperator" class="name">AssertionOperator</a>.</p>

Init Arguments
    [Template]    Verify Argument Models
    ${MODEL}[inits][0][args]     credentials: Small = one

Init docs
    ${MODEL}[inits][0][doc]     <p>This is the init Docs.</p>
    ...   <p>It links to <a href="#Set%20Location" class="name">Set Location</a> keyword and to <a href="#GeoLocation" class="name">GeoLocation</a> data type.</p>

Keyword Arguments
    [Tags]        require-py3.7
    [Template]    Verify Argument Models
    ${MODEL}[keywords][0][args]     value    operator: AssertionOperator | None = None    exp: str = something?
    ${MODEL}[keywords][1][args]     arg: CustomType    arg2: CustomType2    arg3: CustomType
    ${MODEL}[keywords][2][args]     funny: bool | int | float | str | AssertionOperator | Small | GeoLocation | None = equal
    ${MODEL}[keywords][3][args]     location: GeoLocation
    ${MODEL}[keywords][4][args]     list_of_str: List[str]    dict_str_int: Dict[str, int]    Whatever: Any    *args: List[typing.Any]

TypedDict
    ${MODEL}[dataTypes][typedDicts][0][type]    TypedDict
    ${MODEL}[dataTypes][typedDicts][0][name]    GeoLocation
    ${MODEL}[dataTypes][typedDicts][0][doc]     <p>Defines the geolocation.</p>
    ...    <ul>
    ...    <li><code>latitude</code> Latitude between -90 and 90.</li>
    ...    <li><code>longitude</code> Longitude between -180 and 180.</li>
    ...    <li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0.</li>
    ...    </ul>
    ...    <p>Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></p>
    ${MODEL}[types][6][type]    TypedDict
    ${MODEL}[types][6][name]    GeoLocation
    ${MODEL}[types][6][doc]     <p>Defines the geolocation.</p>
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
    ${MODEL}[dataTypes][enums][0][type]    Enum
    ${MODEL}[dataTypes][enums][0][name]    AssertionOperator
    ${MODEL}[dataTypes][enums][0][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>
    ${MODEL}[types][0][type]    Enum
    ${MODEL}[types][0][name]    AssertionOperator
    ${MODEL}[types][0][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>

Enum Members
    [Template]    NONE
    ${exp_list}    Evaluate    [{"name": "equal","value": "=="},{"name": "==","value": "=="},{"name": "<","value": "<"},{"name": ">","value": ">"},{"name": "<=","value": "<="},{"name": ">=","value": ">="}]
    FOR   ${cur}    ${exp}    IN ZIP    ${MODEL}[dataTypes][enums][0][members]    ${exp_list}
        Dictionaries Should Be Equal    ${cur}    ${exp}
    END
    FOR   ${cur}    ${exp}    IN ZIP    ${MODEL}[types][0][members]    ${exp_list}
        Dictionaries Should Be Equal    ${cur}    ${exp}
    END

Custom types
    ${Model}[types][2][type]    Custom
    ${Model}[types][2][name]    CustomType
    ${Model}[types][2][doc]     <p>Converter method doc is used when defined.</p>
    ${Model}[types][3][type]    Custom
    ${Model}[types][3][name]    CustomType2
    ${Model}[types][3][doc]     <p>Class doc is used when converter method has no doc.</p>

Standard types
    ${Model}[types][1][type]    Standard
    ${Model}[types][1][name]    boolean
    ${Model}[types][1][doc]     <p>Strings <code>TRUE</code>, <code>YES</code>,   start=True

Usages
    ${MODEL}[types][1][type]      Standard
    ${MODEL}[types][1][usages]    [{'kw': 'Funny Unions', 'args': ['funny']}]
    ${MODEL}[types][2][type]      Custom
    ${MODEL}[types][2][usages]    [{'kw': 'Custom', 'args': ['arg', 'arg3']}]
    ${MODEL}[types][6][type]      TypedDict
    ${MODEL}[types][6][usages]    [{'kw': 'Funny Unions', 'args': ['funny']}, {'kw': 'Set Location', 'args': ['location']}]
    ${MODEL}[types][10][type]     Enum
    # With Python 3.6 `typing.get_type_hints` ignores `Small`.
    # Apparently because it is based on `int` args also have `int`.
    IF    $INTERPRETER.version_info >= (3, 7)
        ${MODEL}[types][10][usages]    [{'kw': '__init__', 'args': ['credentials']}, {'kw': 'Funny Unions', 'args': ['funny']}]
    END

*** Keywords ***
Verify Argument Models
    [Arguments]    ${arg_models}    @{expected_reprs}
    [Tags]    robot:continue-on-failure
    Should Be True    len($arg_models) == len($expected_reprs)
    FOR    ${arg_model}    ${expected_repr}    IN ZIP    ${arg_models}    ${expected_reprs}
         Verify Argument Model    ${arg_model}    ${expected_repr}    json=True
    END
