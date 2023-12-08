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
    ${MODEL}[keywords][1][args]     arg: CustomType    arg2: CustomType2    arg3: CustomType    arg4: Unknown
    ${MODEL}[keywords][2][args]     funny: bool | int | float | str | AssertionOperator | Small | GeoLocation | None = equal
    ${MODEL}[keywords][3][args]     location: GeoLocation
    ${MODEL}[keywords][4][args]     list_of_str: List[str]    dict_str_int: Dict[str, int]    whatever: Any    *args: List[Any]
    ${MODEL}[keywords][5][args]     arg: Literal[1, 'xxx', b'yyy', True, None, one]

TypedDict
    ${MODEL}[typedocs][7][type]    TypedDict
    ${MODEL}[typedocs][7][name]    GeoLocation
    ${MODEL}[typedocs][7][doc]     <p>Defines the geolocation.</p>
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
        FOR    ${item}    IN    @{Model}[typedocs][7][items]
            IF    $exp['key'] == $item['key']
                Dictionaries Should Be Equal    ${item}    ${exp}
                BREAK
            END
        END
    END

Enum
    ${MODEL}[typedocs][1][type]    Enum
    ${MODEL}[typedocs][1][name]    AssertionOperator
    ${MODEL}[typedocs][1][doc]     <p>This is some Doc</p>
    ...   <p>This has was defined by assigning to __doc__.</p>

Enum Members
    [Template]    NONE
    ${exp_list}    Evaluate    [{"name": "equal","value": "=="},{"name": "==","value": "=="},{"name": "<","value": "<"},{"name": ">","value": ">"},{"name": "<=","value": "<="},{"name": ">=","value": ">="}]
    FOR   ${cur}    ${exp}    IN ZIP    ${MODEL}[typedocs][1][members]    ${exp_list}
        Dictionaries Should Be Equal    ${cur}    ${exp}
    END

Custom types
    ${MODEL}[typedocs][3][type]       Custom
    ${MODEL}[typedocs][3][name]       CustomType
    ${MODEL}[typedocs][3][doc]        <p>Converter method doc is used when defined.</p>
    ${MODEL}[typedocs][4][type]       Custom
    ${MODEL}[typedocs][4][name]       CustomType2
    ${MODEL}[typedocs][4][doc]        <p>Class doc is used when converter method has no doc.</p>

Standard types
    ${MODEL}[typedocs][0][type]       Standard
    ${MODEL}[typedocs][0][name]       Any
    ${MODEL}[typedocs][0][doc]        <p>Any value is accepted. No conversion is done.</p>
    ${MODEL}[typedocs][2][type]       Standard
    ${MODEL}[typedocs][2][name]       boolean
    ${MODEL}[typedocs][2][doc]        <p>Strings <code>TRUE</code>, <code>YES</code>,   start=True
    ${MODEL}[typedocs][10][name]      Literal
    ${MODEL}[typedocs][10][doc]       <p>Only specified values are accepted.    start=True

Standard types with generics
    ${MODEL}[typedocs][5][type]       Standard
    ${MODEL}[typedocs][5][name]       dictionary
    ${MODEL}[typedocs][5][doc]        <p>Strings must be Python <a    start=True
    ${MODEL}[typedocs][9][type]       Standard
    ${MODEL}[typedocs][9][name]       list
    ${MODEL}[typedocs][9][doc]        <p>Strings must be Python <a    start=True

Accepted types
    ${MODEL}[typedocs][0][type]       Standard
    ${MODEL}[typedocs][0][accepts]    ['Any']
    ${MODEL}[typedocs][2][type]       Standard
    ${MODEL}[typedocs][2][accepts]    ['string', 'integer', 'float', 'None']
    ${MODEL}[typedocs][10][type]      Standard
    ${MODEL}[typedocs][10][accepts]   ['Any']
    ${MODEL}[typedocs][3][type]       Custom
    ${MODEL}[typedocs][3][accepts]    ['string', 'integer']
    ${MODEL}[typedocs][4][type]       Custom
    ${MODEL}[typedocs][4][accepts]    []
    ${MODEL}[typedocs][7][type]       TypedDict
    ${MODEL}[typedocs][7][accepts]    ['string', 'Mapping']
    ${MODEL}[typedocs][1][type]       Enum
    ${MODEL}[typedocs][1][accepts]    ['string']
    ${MODEL}[typedocs][12][type]      Enum
    ${MODEL}[typedocs][12][accepts]   ['string', 'integer']

Usages
    ${MODEL}[typedocs][2][type]       Standard
    ${MODEL}[typedocs][2][usages]     ['Funny Unions', 'Set Location']
    ${MODEL}[typedocs][5][type]       Standard
    ${MODEL}[typedocs][5][usages]     ['Typing Types']
    ${MODEL}[typedocs][3][type]       Custom
    ${MODEL}[typedocs][3][usages]     ['Custom']
    ${MODEL}[typedocs][7][type]       TypedDict
    ${MODEL}[typedocs][7][usages]     ['Funny Unions', 'Set Location']
    ${MODEL}[typedocs][12][type]      Enum
    ${MODEL}[typedocs][12][usages]    ['__init__', 'Funny Unions']

Typedoc links in arguments
    ${MODEL}[keywords][0][args][1][type][name]                  Union
    ${MODEL}[keywords][0][args][1][type][typedoc]               None
    ${MODEL}[keywords][0][args][1][type][nested][0][name]       AssertionOperator
    ${MODEL}[keywords][0][args][1][type][nested][0][typedoc]    AssertionOperator
    ${MODEL}[keywords][0][args][1][type][nested][1][name]       None
    ${MODEL}[keywords][0][args][1][type][nested][1][typedoc]    None
    ${MODEL}[keywords][0][args][2][type][name]                  str
    ${MODEL}[keywords][0][args][2][type][typedoc]               string
    ${MODEL}[keywords][1][args][0][type][name]                  CustomType
    ${MODEL}[keywords][1][args][0][type][typedoc]               CustomType
    ${MODEL}[keywords][1][args][1][type][name]                  CustomType2
    ${MODEL}[keywords][1][args][1][type][typedoc]               CustomType2
    ${MODEL}[keywords][1][args][2][type][name]                  CustomType
    ${MODEL}[keywords][1][args][2][type][typedoc]               CustomType
    ${MODEL}[keywords][1][args][3][type][name]                  Unknown
    ${MODEL}[keywords][1][args][3][type][typedoc]               None
    ${MODEL}[keywords][2][args][0][type][name]                  Union
    ${MODEL}[keywords][2][args][0][type][typedoc]               None
    ${MODEL}[keywords][2][args][0][type][nested][0][name]       bool
    ${MODEL}[keywords][2][args][0][type][nested][0][typedoc]    boolean
    ${MODEL}[keywords][2][args][0][type][nested][1][name]       int
    ${MODEL}[keywords][2][args][0][type][nested][1][typedoc]    integer
    ${MODEL}[keywords][2][args][0][type][nested][2][name]       float
    ${MODEL}[keywords][2][args][0][type][nested][2][typedoc]    float
    ${MODEL}[keywords][2][args][0][type][nested][3][name]       str
    ${MODEL}[keywords][2][args][0][type][nested][3][typedoc]    string
    ${MODEL}[keywords][2][args][0][type][nested][4][name]       AssertionOperator
    ${MODEL}[keywords][2][args][0][type][nested][4][typedoc]    AssertionOperator
    ${MODEL}[keywords][2][args][0][type][nested][5][name]       Small
    ${MODEL}[keywords][2][args][0][type][nested][5][typedoc]    Small
    ${MODEL}[keywords][2][args][0][type][nested][6][name]       GeoLocation
    ${MODEL}[keywords][2][args][0][type][nested][6][typedoc]    GeoLocation
    ${MODEL}[keywords][2][args][0][type][nested][7][name]       None
    ${MODEL}[keywords][2][args][0][type][nested][7][typedoc]    None
    ${MODEL}[keywords][4][args][0][type][name]                  List
    ${MODEL}[keywords][4][args][0][type][typedoc]               list
    ${MODEL}[keywords][4][args][0][type][nested][0][name]       str
    ${MODEL}[keywords][4][args][0][type][nested][0][typedoc]    string
    ${MODEL}[keywords][4][args][1][type][name]                  Dict
    ${MODEL}[keywords][4][args][1][type][typedoc]               dictionary
    ${MODEL}[keywords][4][args][1][type][nested][0][name]       str
    ${MODEL}[keywords][4][args][1][type][nested][0][typedoc]    string
    ${MODEL}[keywords][4][args][1][type][nested][1][name]       int
    ${MODEL}[keywords][4][args][1][type][nested][1][typedoc]    integer
    ${MODEL}[keywords][4][args][2][type][name]                  Any
    ${MODEL}[keywords][4][args][2][type][typedoc]               Any
    ${MODEL}[keywords][4][args][3][type][name]                  List
    ${MODEL}[keywords][4][args][3][type][typedoc]               list
    ${MODEL}[keywords][4][args][3][type][nested][0][name]       Any
    ${MODEL}[keywords][4][args][3][type][nested][0][typedoc]    Any

*** Keywords ***
Verify Argument Models
    [Arguments]    ${arg_models}    @{expected_reprs}
    [Tags]    robot:continue-on-failure
    FOR    ${arg_model}    ${expected_repr}    IN ZIP    ${arg_models}    ${expected_reprs}    mode=strict
        Verify Argument Model    ${arg_model}    ${expected_repr}    json=True
    END
