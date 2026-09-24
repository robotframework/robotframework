"""Library used to generate the development fixture for the Libdoc frontend.

Run `npm run testdata` in `src/web` to regenerate `testdata.ts` from this file.
The dev server started by `npm start` does it automatically on every save.
"""

from datetime import timedelta
from enum import Enum, IntEnum
from subprocess import Popen
from typing import Literal, TypedDict

from robot.api.deco import keyword, library

type Locator = str
"""Element locator, an alias of a standard type."""

type Modifier = KeyboardModifier
"""Alias of an enum."""

type Margins = PdfMargins
"""Alias of a TypedDict."""

type Handle = Popen | str | None
"""Alias of a union, like the example in issue #5760."""

type Boxed[T] = T | None
"""Parameterized alias, rendered with its parameters like `Boxed[str]`."""

type Json = str | int | list[Json]
"""Recursive alias."""

type Nothing = None
"""Alias of `None`, the only alias whose name a keyword could lose."""

type WebElement = SelectorSpec
"""Alias of a custom type, used nested inside other types."""


class MouseButton(Enum):
    """Mouse button to click with.

    Members have string values, so no value is shown next to the name.
    """

    left = "left"
    middle = "middle"
    right = "right"


class KeyboardModifier(Enum):
    """Modifier keys to press while doing other actions."""

    Alt = "Alt"
    Control = "Control"
    Meta = "Meta"
    Shift = "Shift"


class LogLevel(IntEnum):
    """Severity of a log message.

    Members have integer values, which are shown next to the names.
    """

    TRACE = 0
    DEBUG = 10
    INFO = 20
    WARN = 30


class _RequiredMargins(TypedDict):
    top: str
    bottom: str


class PdfMargins(_RequiredMargins, total=False):
    """Margins of the generated PDF.

    Only `top` and `bottom` are required. The optional keys are declared by a
    `total=False` subclass, because `NotRequired` would leak into the rendered
    key type.
    """

    left: str
    right: str


class ViewportSize(TypedDict):
    """Size of the browser viewport in pixels."""

    width: int
    height: int


class SelectorSpec:
    """This documentation is not used, because the converter has its own."""

    def __init__(self, strategy: str, value: str):
        self.strategy = strategy
        self.value = value

    @classmethod
    def parse(cls, value: str | int):
        """Selector in the `strategy=value` format, for example `id=submit`."""
        strategy, _, rest = str(value).partition("=")
        return cls(strategy, rest)


class Credential:
    """Username and password, given as `user:password`.

    The class itself is the converter, so this documentation is used.
    """

    def __init__(self, value):
        self.user, _, self.password = value.partition(":")


@library(
    version="1.2.3",
    scope="GLOBAL",
    doc_format="MARKDOWN",
    auto_keywords=True,
    converters={SelectorSpec: SelectorSpec.parse, Credential: Credential},
)
class DevLibrary:
    """Library for developing the Libdoc HTML frontend.

    %TOC%

    # Purpose

    This library exists only to produce the development fixture rendered by
    `npm start`. It is not shipped and it is not used by any test. Every keyword
    here earns its place by exercising something the frontend renders, so adding a
    keyword is how you add a case to the fixture.

    Keywords are named after the case they present rather than after anything a
    browser library would do. The library is not pretending to be a real one, and
    a name that says what is being rendered is easier to find when a rendering
    bug needs reproducing. What the keywords *accept and return* is a different
    matter: do not add types, argument kinds or documentation structures that a
    real library could not produce, because the point is to render what Libdoc
    actually receives.

    Run `npm run testdata` to regenerate `testdata.ts` from this file. The dev
    server does it for you whenever this file is saved.

    `DevLibraryRobotFormat.py` is the counterpart of this library for the ROBOT
    documentation format, and covers the documentation tables only that format
    produces.

    # What is covered

    Case | Keywords
    ---- | --------
    Type aliases | [Alias Inside Generic Type], [Alias Of None], [Alias Of Union], [Deeply Nested Aliases], [Parameterized Alias], [Recursive Alias]
    Enums | [Enum Arguments], [Enum With Integer Values]
    Literals | [Literal With Mixed Types]
    TypedDicts | [Alias Of TypedDict], [TypedDict Argument And Return]
    Custom types | [Custom Type Documented By Class], [Custom Type With Converter Method]
    Generics | [Nested Generic Type]
    Argument kinds | [All Argument Kinds], [No Arguments]
    Argument documentation | [Long Argument Documentation]
    Returns and raises | [Returns And Raises]
    Deprecation | [Deprecated Keyword]

    > [!NOTE]
    > Documentation is written in Markdown, so this text also covers the Markdown
    > features the frontend has to render. Each row of the table above is one
    > source line: a row wrapped onto a second line becomes a second row.

    > [!TIP] Admonitions have optional titles
    > And they nest:
    >
    > > [!WARNING]
    > > Do not add cases here that a real library could not produce.

    > [!IMPORTANT] Admonitions hold more than paragraphs
    > Everything that can appear in documentation can appear inside one, and
    > each kind has to clear the border on its own.
    >
    > - A list item.
    >     - A nested one.
    >
    > Kind | Clears the border
    > ---- | -----------------
    > Lists | yes
    > Tables | yes
    > Code blocks | yes
    >
    >     *** Test Cases ***
    >     Example
    >         No Arguments
    >
    > The code block above is indented rather than fenced. Python-Markdown
    > supports fenced blocks only at the document root level, so one written
    > inside an admonition is not recognized.

    # Formatting examples

    Basic formatting such as **bold**, *italics* and `code` works, and so do links
    to keywords like [Returns And Raises], to types like [int] and to sections like
    [Purpose].

    ## Lists

    - Unordered item.
        - Nested item.
        - Another nested item.
    - Item with an ordered sublist.
        1. First.
        2. Second.

    ## Code blocks

    ```robotframework
    *** Test Cases ***
    Example
        Enum Arguments    id=submit    button=right
    ```
    """

    def __init__(
        self,
        browser: MouseButton | str = "chromium",
        timeout: timedelta = timedelta(seconds=10),
        options: dict[str, str] | None = None,
    ):
        """Configures the library when it is imported.

        Args:
            browser: a union of an enum and a standard type.
            timeout: a type Libdoc renders with a converter of its own.
            options: an optional generic type.
        """

    def enum_arguments(
        self,
        selector: Locator,
        button: MouseButton = MouseButton.left,
        *,
        modifiers: Modifier | None = None,
    ):
        """Takes an enum, an alias of an enum, and an alias of a standard type.

        The enum members have string values, so no value is shown next to the
        name. Tags are rendered as well.

        Args:
            selector: uses a type alias of a standard type.
            button: uses an enum.
            modifiers: uses an alias of an enum.

        Tags:
            arguments, enums
        """

    def returns_and_raises(self, selector: Locator) -> str:
        """Documents a return value and two exceptions.

        The `selector` argument uses the same alias as [Enum Arguments], so the
        alias is used by more than one keyword.

        Args:
            selector: element to read.

        Returns:
            Text of the element.

        Raises:
            ValueError: if the element does not exist.
            TypeError: if the selector is not a string.

        Tags:
            returns
        """
        return ""

    def alias_inside_generic_type(
        self,
        selectors: list[Locator],
        duration: timedelta = timedelta(seconds=2),
    ) -> int:
        """Takes an alias nested inside a generic type.

        Args:
            selectors: the alias is nested inside `list`.
            duration: a type Libdoc renders with a converter of its own.

        Returns:
            How many elements matched.

        Tags:
            aliases
        """
        return 0

    def deeply_nested_aliases(
        self,
        target: WebElement | str | list[WebElement | str | list[Locator]],
        smooth: bool = True,
    ):
        """Takes aliases nested inside other types and inside each other.

        This is the deepest type the UI renders.

        Args:
            target: aliases nested inside other types and inside each other.
            smooth: a plain boolean, for contrast.

        Tags:
            aliases
        """

    @keyword("Alias Of TypedDict")
    def alias_of_typeddict(self, path: str, margins: Margins, scale: float = 1.0):
        """Takes an alias of a TypedDict.

        The name is set with `@keyword`, because the one derived from the method
        name would lose the capital `D`.

        Args:
            path: a plain string.
            margins: uses an alias of a TypedDict.
            scale: a plain float.

        Tags:
            aliases, typeddicts
        """

    @keyword("TypedDict Argument And Return")
    def typeddict_argument_and_return(self, size: ViewportSize) -> ViewportSize:
        """Takes and returns a TypedDict directly, without an alias.

        The name is set with `@keyword`, as in [Alias Of TypedDict].

        Args:
            size: uses a TypedDict directly.

        Returns:
            The previous size, using the same TypedDict.

        Tags:
            typeddicts
        """
        return {"width": 800, "height": 600}

    def enum_with_integer_values(self, level: LogLevel = LogLevel.INFO) -> LogLevel:
        """Takes and returns an enum whose members have integer values.

        The values are shown next to the names, unlike the string-valued enum in
        [Enum Arguments].

        Args:
            level: uses an enum with integer values.

        Returns:
            The previous level.

        Tags:
            enums
        """
        return LogLevel.INFO

    def literal_with_mixed_types(
        self, strategy: Literal["css", "xpath", "text", 1, True]
    ):
        """Takes a literal whose members are not all of the same type.

        Args:
            strategy: uses a literal with mixed member types.

        Tags:
            literals
        """

    def alias_of_union(self, handle: Handle = None) -> Handle:
        """Takes and returns an alias of a union.

        A union has no single type to document, which is what this case is here
        to show.

        Args:
            handle: uses an alias of a union.

        Returns:
            The previous handle.

        Tags:
            aliases
        """
        return None

    def long_argument_documentation(self, session: str = ""):
        """Documents one argument at length, with code blocks inside it.

        Args:
            session: session to attach to. Must be a session id returned by
                another keyword, or the name of a session stored in the
                `sessions` mapping of the library.

                A session id can be read from Python, which is how another
                library hands one over:

                ```python
                from robot.libraries.BuiltIn import BuiltIn

                def get_browser_session():
                    library = BuiltIn().get_library_instance("DevLibrary")
                    return library.sessions.current
                ```

                The id is then given to this keyword in a test:

                ```robotframework
                *** Settings ***
                Library    DevLibrary
                Library    ${CURDIR}/browser_session.py

                *** Test Cases ***
                Example
                    ${session} =    Get Browser Session
                    Long Argument Documentation    ${session}
                ```

                Leaving the argument empty attaches to the session that was
                used last.

        Tags:
            arguments
        """

    def parameterized_alias(self, value: Boxed[str] = None) -> Boxed[int]:
        """Takes and returns a parameterized alias, with different parameters.

        Args:
            value: uses a parameterized alias.

        Returns:
            The boxed value, using the same alias with other parameters.

        Tags:
            aliases
        """
        return None

    def recursive_alias(self, data: Json) -> Json:
        """Takes and returns an alias that refers to itself.

        Args:
            data: uses a recursive alias.

        Returns:
            The evaluated data.

        Tags:
            aliases
        """
        return data

    def custom_type_with_converter_method(self, selector: SelectorSpec) -> SelectorSpec:
        """Takes a custom type whose converter method is documented.

        The documentation comes from `SelectorSpec.parse` rather than from the
        class, because the converter is registered separately.

        Args:
            selector: uses a custom type documented by its converter.

        Returns:
            The parsed selector.

        Tags:
            custom types
        """
        return selector

    def custom_type_documented_by_class(self, credential: Credential):
        """Takes a custom type documented by the class itself.

        The class is its own converter here, so its documentation is used.

        Args:
            credential: uses a custom type documented by its class.

        Tags:
            custom types
        """

    def nested_generic_type(
        self,
        options: dict[str, list[int]] | None = None,
    ) -> dict[str, list[int]]:
        """Takes and returns a generic type nested inside another.

        Args:
            options: uses a nested generic type.

        Returns:
            The previous options.

        Tags:
            generics
        """
        return {}

    def all_argument_kinds(self, a, /, b, c="d", *e, f, g="h", **i):
        """Has every kind of argument there is.

        No real keyword has all of them at once, which is why this one is named
        for the case rather than for anything it could plausibly do.

        Args:
            a: positional-only argument.
            b: normal argument, whose documentation
                continues on the next line.
            c: normal argument with a default value.
            *e: free positional arguments.
            f: named-only argument without a default value.
            g: named-only argument with a default value.
            **i: free named arguments.

        Tags:
            arguments
        """

    def no_arguments(self):
        """Takes no arguments at all, so no argument table is rendered.

        Tags:
            arguments
        """

    def alias_of_none(self) -> Nothing:
        """Returns an alias of `None`.

        A keyword returning plain `None` shows no return type at all, because
        every Python function returns `None` implicitly, but this alias was
        declared and annotated on purpose.

        Tags:
            aliases, returns
        """

    def deprecated_keyword(self, url: str, *, headless: bool = True):
        """*DEPRECATED* Use [Enum Arguments] instead.

        Deprecated keywords are shown with a strike-through in the keyword list.

        Args:
            url: a plain string.
            headless: a named-only boolean.

        Tags:
            deprecation
        """
