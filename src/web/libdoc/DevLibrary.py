"""Library used to generate the development fixture for the Libdoc frontend.

Run `npm run testdata` in `src/web` to regenerate `testdata.ts` from this file.
The dev server started by `npm start` does it automatically on every save.
"""

from datetime import timedelta
from enum import Enum, IntEnum
from subprocess import Popen
from typing import Literal, TypedDict

from robot.api.deco import library

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

    Run `npm run testdata` to regenerate `testdata.ts` from this file. The dev
    server does it for you whenever this file is saved.

    # What is covered

    Type | Where to look
    ---- | -------------
    Type aliases | [Click], [Connect To Browser], [Evaluate Json], [Box Value],
        [Close All Browsers]
    Nested type aliases | [Scroll To Element]
    Long argument documentation | [Attach To Session]
    Enums | [Click], [Set Log Level]
    TypedDicts | [Save Page As Pdf], [Set Viewport Size]
    Custom types | [Parse Selector], [Set Credentials]
    Argument kinds | [All Argument Kinds]

    > [!NOTE]
    > Documentation is written in Markdown, so this text also covers the Markdown
    > features the frontend has to render.

    > [!TIP] Admonitions have optional titles
    > And they nest:
    >
    > > [!WARNING]
    > > Do not add cases here that a real library could not produce.

    # Formatting examples

    Basic formatting such as **bold**, *italics* and `code` works, and so do links
    to keywords like [Get Text], to types like [int] and to sections like
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
        Click    id=submit    button=right
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
            browser: browser to open.
            timeout: default timeout for keywords that wait.
            options: extra options passed to the browser.
        """

    def click(
        self,
        selector: Locator,
        button: MouseButton = MouseButton.left,
        *,
        modifiers: Modifier | None = None,
    ):
        """Clicks the element matching `selector`.

        Args:
            selector: element to click. Uses a type alias of a standard type.
            button: which mouse button to use. Uses an enum.
            modifiers: modifier key to hold down. Uses an alias of an enum.

        Tags:
            action, mouse
        """

    def get_text(self, selector: Locator) -> str:
        """Returns the text of the element matching `selector`.

        The `selector` argument uses the same alias as [Click], so the alias is
        used by more than one keyword.

        Args:
            selector: element to read.

        Returns:
            Text of the element.

        Raises:
            ValueError: if the element does not exist.
            TypeError: if the selector is not a string.

        Tags:
            getter
        """
        return ""

    def highlight_elements(
        self,
        selectors: list[Locator],
        duration: timedelta = timedelta(seconds=2),
    ) -> int:
        """Highlights all elements matching the given selectors.

        Args:
            selectors: elements to highlight. The alias is nested inside a
                generic type.
            duration: how long the highlight is shown.

        Returns:
            How many elements were highlighted.

        Tags:
            action
        """
        return 0

    def scroll_to_element(
        self,
        target: WebElement | str | list[WebElement | str | list[Locator]],
        smooth: bool = True,
    ):
        """Scrolls to the given element.

        Args:
            target: element to scroll to. Aliases nested inside other types and
                inside each other, which is the deepest type the UI renders.
            smooth: whether the scrolling is animated.

        Tags:
            action
        """

    def save_page_as_pdf(self, path: str, margins: Margins, scale: float = 1.0):
        """Saves the current page as a PDF file.

        Args:
            path: where the PDF is written.
            margins: page margins. Uses an alias of a TypedDict.
            scale: scale of the rendered page.

        Tags:
            action
        """

    def set_viewport_size(self, size: ViewportSize) -> ViewportSize:
        """Sets the viewport size.

        Args:
            size: new size. Uses a TypedDict directly.

        Returns:
            The previous size.

        Tags:
            setter
        """
        return {"width": 800, "height": 600}

    def set_log_level(self, level: LogLevel = LogLevel.INFO) -> LogLevel:
        """Sets the log level.

        Args:
            level: new level. Uses an enum with integer values.

        Returns:
            The previous level.

        Tags:
            setter
        """
        return LogLevel.INFO

    def select_strategy(self, strategy: Literal["css", "xpath", "text", 1, True]):
        """Selects the strategy used to find elements.

        Args:
            strategy: strategy to use. Uses a literal with mixed member types.

        Tags:
            setter
        """

    def connect_to_browser(self, handle: Handle = None) -> Handle:
        """Connects to an already running browser.

        Args:
            handle: browser to connect to. Uses an alias of a union, which has
                no single type to document.

        Returns:
            The previous handle.

        Tags:
            action
        """
        return None

    def attach_to_session(self, session: str = ""):
        """Attaches to an already running browser session.

        Args:
            session: session to attach to. Must be a session id returned by
                [Connect To Browser], or the name of a session stored in the
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
                    Attach To Session    ${session}
                ```

                Leaving the argument empty attaches to the session that was
                used last.

        Tags:
            action
        """

    def box_value(self, value: Boxed[str] = None) -> Boxed[int]:
        """Boxes a value.

        Args:
            value: value to box. Uses a parameterized alias.

        Returns:
            The boxed value, using the same alias with other parameters.
        """
        return None

    def evaluate_json(self, data: Json) -> Json:
        """Evaluates JSON data.

        Args:
            data: data to evaluate. Uses a recursive alias.

        Returns:
            The evaluated data.
        """
        return data

    def parse_selector(self, selector: SelectorSpec) -> SelectorSpec:
        """Parses a selector.

        Args:
            selector: selector to parse. Uses a custom type whose converter
                method is documented.

        Returns:
            The parsed selector.
        """
        return selector

    def set_credentials(self, credential: Credential):
        """Sets the credentials used with basic authentication.

        Args:
            credential: credentials to use. Uses a custom type documented by
                the class itself.

        Tags:
            setter
        """

    def set_options(
        self,
        options: dict[str, list[int]] | None = None,
    ) -> dict[str, list[int]]:
        """Sets extra options.

        Args:
            options: options to set. Uses a nested generic type.

        Returns:
            The previous options.

        Tags:
            setter
        """
        return {}

    def all_argument_kinds(self, a, /, b, c="d", *e, f, g="h", **i):
        """Has every kind of argument there is.

        Args:
            a: positional-only argument.
            b: normal argument, whose documentation
                continues on the next line.
            c: normal argument with a default value.
            *e: free positional arguments.
            f: named-only argument without a default value.
            g: named-only argument with a default value.
            **i: free named arguments.
        """

    def close_browser(self):
        """Closes the current browser.

        Takes no arguments at all.

        Tags:
            action
        """

    def close_all_browsers(self) -> Nothing:
        """Closes every browser.

        Returns an alias of `None`. A keyword returning plain `None` shows no
        return type at all, because every Python function returns `None`
        implicitly, but this alias was declared and annotated on purpose.

        Tags:
            action
        """

    def open_browser_in_headless_mode(self, url: str, *, headless: bool = True):
        """*DEPRECATED* Use [Click] instead.

        Deprecated keywords are shown with a strike-through in the keyword list.

        Args:
            url: address to open.
            headless: whether to hide the browser window.

        Tags:
            action
        """
