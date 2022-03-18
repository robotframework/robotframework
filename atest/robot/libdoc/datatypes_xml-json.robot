*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/DataTypesLibrary.xml
Test Template     Should Be Equal Multiline

*** Test Cases ***
Documentation
    ${MODEL}[doc]    <p>This Library has Data Types.</p>
    ...   <p>It has some in <code>__init__</code> and others in the <a href=\"#Keywords\" class=\"name\">Keywords</a>.</p>
    ...   <p>The DataTypes are the following that should be linked. <span class=\"name\">HttpCredentials</span> , <a href=\"#type-GeoLocation\" class=\"name\">GeoLocation</a> , <a href=\"#type-Small\" class=\"name\">Small</a> and <a href=\"#type-AssertionOperator\" class=\"name\">AssertionOperator</a>.</p>

Init Arguments
    [Template]    Verify Argument Models
    ${MODEL}[inits][0][args]     credentials: Small = one

Init docs
    ${MODEL}[inits][0][doc]     <p>This is the init Docs.</p>
    ...   <p>It links to <a href=\"#Set%20Location\" class=\"name\">Set Location</a> keyword and to <a href=\"#type-GeoLocation\" class=\"name\">GeoLocation</a> data type.</p>

Keyword Arguments
    [Template]    Verify Argument Models
    ${MODEL}[keywords][0][args]     value    operator: AssertionOperator | None = None    exp: str = something?
    ${MODEL}[keywords][1][args]     arg: CustomType    arg2: CustomType2    arg3: CustomType
    ${MODEL}[keywords][2][args]     funny: bool | int | float | str | AssertionOperator | Small | GeoLocation | None = equal
    ${MODEL}[keywords][3][args]     location: GeoLocation
    ${MODEL}[keywords][4][args]     list_of_str: List[str]    dict_str_int: Dict[str, int]    whatever: Any    *args: List[Any]

TypedDict
    ${MODEL}[dataTypes][typedDicts][0][name]    GeoLocation
    ${MODEL}[dataTypes][typedDicts][0][type]    TypedDict
    ${MODEL}[dataTypes][typedDicts][0][doc]    <p>Defines the geolocation.</p>
    ...    <ul>
    ...    <li><code>latitude</code> Latitude between -90 and 90.</li>
    ...    <li><code>longitude</code> Longitude between -180 and 180.</li>
    ...    <li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0.</li>
    ...    </ul>
    ...    <p>Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></p>
    ${MODEL}[typedocs][6][type]    TypedDict
    ${MODEL}[typedocs][6][name]    GeoLocation
    ${MODEL}[typedocs][6][doc]     <p>Defines the geolocation.</p>
    ...    <ul>
    ...    <li><code>latitude</code> Latitude between -90 and 90.</li>
    ...    <li><code>longitude</code> Longitude between -180 and 180.</li>
    ...    <li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0.</li>
    ...    </ul>
    ...    <p>Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></p>

TypedDict Items
    [Template]    NONE
    ${longitude}=    Create Dictionary    key=longitude    type=float    required=${True}
    ${latitude}=     Create Dictionary    key=latitude     type=float    required=${True}
    ${accuracy}=     Create Dictionary    key=accuracy     type=float    required=${False}
    FOR    ${exp}    IN    ${longitude}    ${latitude}    ${accuracy}
        FOR    ${item}    IN    @{Model}[dataTypes][typedDicts][0][items]
            IF    $exp['key'] == $item['key']
                Dictionaries Should Be Equal    ${item}    ${exp}
                BREAK
            END
        END
    END

Enum
    ${MODEL}[dataTypes][enums][0][type]    Enum
    ${MODEL}[dataTypes][enums][0][name]    AssertionOperator
    ${MODEL}[dataTypes][enums][0][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>
    ${MODEL}[typedocs][0][type]    Enum
    ${MODEL}[typedocs][0][name]    AssertionOperator
    ${MODEL}[typedocs][0][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>

Enum Members
    [Template]    NONE
    ${exp_list}    Evaluate    [{"name": "equal","value": "=="},{"name": "==","value": "=="},{"name": "<","value": "<"},{"name": ">","value": ">"},{"name": "<=","value": "<="},{"name": ">=","value": ">="}]
    FOR   ${cur}    ${exp}    IN ZIP    ${MODEL}[dataTypes][enums][0][members]    ${exp_list}
        Dictionaries Should Be Equal    ${cur}    ${exp}
    END
    FOR   ${cur}    ${exp}    IN ZIP    ${MODEL}[typedocs][0][members]    ${exp_list}
        Dictionaries Should Be Equal    ${cur}    ${exp}
    END

Custom types
    ${MODEL}[typedocs][2][type]    Custom
    ${MODEL}[typedocs][2][name]    CustomType
    ${MODEL}[typedocs][2][doc]     <p>Converter method doc is used when defined.</p>
    ${MODEL}[typedocs][3][type]    Custom
    ${MODEL}[typedocs][3][name]    CustomType2
    ${MODEL}[typedocs][3][doc]     <p>Class doc is used when converter method has no doc.</p>

Standard types
    ${MODEL}[typedocs][1][type]    Standard
    ${MODEL}[typedocs][1][name]    boolean
    ${MODEL}[typedocs][1][doc]     <p>Strings <code>TRUE</code>, <code>YES</code>,   start=True

Accepted types
    ${MODEL}[typedocs][1][type]       Standard
    ${MODEL}[typedocs][1][accepts]    ['string', 'integer', 'float', 'None']
    ${MODEL}[typedocs][2][type]       Custom
    ${MODEL}[typedocs][2][accepts]    ['string', 'integer']
    ${MODEL}[typedocs][3][type]       Custom
    ${MODEL}[typedocs][3][accepts]    []
    ${MODEL}[typedocs][6][type]       TypedDict
    ${MODEL}[typedocs][6][accepts]    ['string']
    ${MODEL}[typedocs][0][type]       Enum
    ${MODEL}[typedocs][0][accepts]    ['string']
    ${MODEL}[typedocs][10][type]      Enum
    ${MODEL}[typedocs][10][accepts]   ['string', 'integer']

Usages
    ${MODEL}[typedocs][1][type]       Standard
    ${MODEL}[typedocs][1][usages]     ['Funny Unions']
    ${MODEL}[typedocs][2][type]       Custom
    ${MODEL}[typedocs][2][usages]     ['Custom']
    ${MODEL}[typedocs][6][type]       TypedDict
    ${MODEL}[typedocs][6][usages]     ['Funny Unions', 'Set Location']
    ${MODEL}[typedocs][10][type]      Enum
    ${MODEL}[typedocs][10][usages]    ['__init__', 'Funny Unions']

Typedoc links in arguments
    ${MODEL}[keywords][0][args][1][typedocs]    {'AssertionOperator': 'AssertionOperator', 'None': 'None'}
    ${MODEL}[keywords][0][args][2][typedocs]    {'str': 'string'}
    ${MODEL}[keywords][1][args][0][typedocs]    {'CustomType': 'CustomType'}
    ${MODEL}[keywords][1][args][1][typedocs]    {'CustomType2': 'CustomType2'}
    ${MODEL}[keywords][2][args][0][typedocs]    {'bool': 'boolean', 'int': 'integer', 'float': 'float', 'str': 'string', 'AssertionOperator': 'AssertionOperator', 'Small': 'Small', 'GeoLocation': 'GeoLocation', 'None': 'None'}
    ${MODEL}[keywords][4][args][0][typedocs]    {'List[str]': 'list'}
    ${MODEL}[keywords][4][args][1][typedocs]    {'Dict[str, int]': 'dictionary'}
    ${MODEL}[keywords][4][args][2][typedocs]    {}
    ${MODEL}[keywords][4][args][3][typedocs]    {'List[Any]': 'list'}

*** Keywords ***
Verify Argument Models
    [Arguments]    ${arg_models}    @{expected_reprs}
    [Tags]    robot:continue-on-failure
    Should Be True    len($arg_models) == len($expected_reprs)
    FOR    ${arg_model}    ${expected_repr}    IN ZIP    ${arg_models}    ${expected_reprs}
        Verify Argument Model    ${arg_model}    ${expected_repr}    json=True
    END
