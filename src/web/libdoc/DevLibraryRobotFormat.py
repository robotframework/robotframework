"""Library used to generate the ROBOT-format development fixture.

Run `npm run testdata` in `src/web` to regenerate `testdata-robot.ts` from this
file. The dev server started by `npm start` does it automatically on every save,
and serves this fixture at `localhost:1234/?fixture=robot`.
"""

from robot.api.deco import library


@library(version="1.2.3", scope="GLOBAL", doc_format="ROBOT", auto_keywords=True)
class DevLibraryRobotFormat:
    """Library for developing the Libdoc HTML frontend against the ROBOT format.

    = Purpose =

    This library is the counterpart of ``DevLibrary.py``, which uses Markdown. It
    exists for one reason: documentation tables render the same whatever format
    produced them, but the ROBOT format is where the awkward cases come from, and
    nothing else in the fixture produces them.

    Tables are also the one part of library documentation whose content is
    entirely up to the library author, so the styling has to survive shapes the
    frontend never chose. Every keyword here documents one such shape.

    = Two uses of the same syntax =

    The ROBOT format has no fenced code blocks, so a table is also the only way
    to lay Robot data out in columns. That gives ``| ... |`` two quite different
    jobs, and a change that suits one can easily ruin the other.

    == Genuine tabular data ==

    Short keys against prose. Column widths are decided by the content, and the
    reader is looking things up rather than reading across.

    | = Name = | = Explanation = |
    | shell | Whether to run the command in a shell or not. |
    | cwd | Directory where to run the command. |
    | env | Environment variables as a dictionary. |
    | stdout | Path to a file where to write standard output. |

    == Robot data laid out in columns ==

    Here the table is a code sample, not data. Columns carry the meaning: the
    reader scans down them to see which argument is which, so anything that
    makes a cell wrap breaks the example.

    | `Run Process` | ${tools}${/}prog.py | argument | second arg with spaces |
    | `Run Process` | java | -jar | ${jars}${/}example.jar | --option | value |
    | ${result} = | `Run Process` | program | stdout=${TEMPDIR}/stdout.txt |

    Tables like these are common in third-party libraries, because ROBOT is the
    default documentation format. They are wide to begin with, which is what
    bounds how much the cells can be padded.
    """

    def data_table_with_header_row(self, name: str, value: str = ""):
        """Documents a table whose first row is a header.

        Header cells are written as ``= Name =``, which is the only way the ROBOT
        format marks them. Authors usually pad the source so the pipes line up,
        and that padding is lost in HTML, so the rendered header cannot rely on
        it.

        | = Setting = | = Default = | = Explanation = |
        | timeout | 10 seconds | How long to wait before giving up. |
        | retries | 3 | How many times to try again after a failure. |
        | encoding | UTF-8 | Encoding used when reading command output. |
        """

    def robot_data_layout_table(self, command: str, *arguments: str):
        """Documents a wide table used to lay Robot data out in columns.

        This is the shape that bounds cell padding: it is already close to the
        width available in a default window, and wrapping a cell destroys the
        column alignment that makes the example readable.

        | ${result} = | `Run Process` | program | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt |
        | `Log Many` | stdout: ${result.stdout} | stderr: ${result.stderr} |
        | ${result} = | `Run Process` | program | stderr=STDOUT |

        Tags:
            table
        """

    def ragged_table(self, rows: int = 3):
        """Documents a table whose rows do not all have the same number of cells.

        Nothing stops an author writing one, and Libdoc pads the short rows with
        empty cells rather than rejecting them. The padding cells are what this
        case is here to show: they are real cells and they take the same borders
        and background as any other.

        | = Kind = | = Note = |
        | One cell |
        | Two cells | second |
        | Three cells | second | third |
        | Four cells | second | third | fourth |

        Tags:
            table
        """

    def table_wider_than_the_page(self, *columns: str):
        """Documents a table too wide for the documentation column.

        There is no way for an author to know how wide the reader's window is,
        so tables that overflow are inevitable. This one overflows on purpose,
        which is how the frontend's handling of it stays visible while it is
        being worked on.

        | = Column one = | = Column two = | = Column three = | = Column four = | = Column five = | = Column six = |
        | ${VALUE_ONE} | ${VALUE_TWO} | ${VALUE_THREE} | ${VALUE_FOUR} | ${VALUE_FIVE} | ${VALUE_SIX} |
        | a rather long cell value | another rather long cell value | a third rather long value | a fourth rather long value | a fifth rather long value | a sixth rather long value |

        Tags:
            table
        """

    def inline_formatting(self, text: str):
        """Documents the inline formatting the ROBOT format supports.

        Text can be *bold*, _italic_, and ``code``. URLs such as
        http://robotframework.org are linked automatically, and so are links
        written as [http://robotframework.org|a labelled link].

        Keyword names in backticks link to the keyword, like `Ragged Table`, and
        the same syntax inside a table cell has to keep working.

        | = Written as = | = Renders as = |
        | ``*bold*`` | *bold* |
        | ``_italic_`` | _italic_ |
        | double backticks | ``code`` |
        """

    def headings_and_lists(self, items: list):
        """Documents the block formatting the ROBOT format supports.

        == A heading inside a keyword ==

        Headings are written with ``=`` signs around them, one to three deep.

        - An unordered item.
        - Another item, long enough to show what happens when the text is wider
          than the column it is set in and has to wrap onto a second line.

        ---

        The ruler above is three or more hyphens on a line of their own.
        """

    def plain_keyword_with_arguments(self, first, second="default", *rest, **config):
        """Takes several kinds of argument and documents none of them.

        Most keywords in most libraries look like this. The fixture needs a few
        so that the pages it renders have the proportions of real documentation
        rather than those of a test harness.
        """

    def keyword_with_return_value(self, name: str) -> str:
        """Returns a value, so the return table is rendered.

        Tags:
            getter
        """
        return ""
