/**
 * Library for `libdoc.py` testing purposes.
 *
 * This library is only used in an example and it doesn't do anything useful.
 *
 */
public class Example {
    public static final String ROBOT_LIBRARY_VERSION = "1.0";
    public static final String ROBOT_LIBRARY_SCOPE = "GLOBAL";

    /**
     * Creates new Example test library 1
     */
    public Example() {
    }

    /**
     * Creates new Example test library 2
     */
    public Example(String arg) {
    }

    /**
     * Creates new Example test library 3
     */
    public Example(int i) {
    }

    /**
     * Should not be visible in library documentation
     */
    private Example(String[] args) {
    }

    /**
     * Does nothing & <doc> has "stuff" to 'escape'!!
     *     and ignored indentation
     */
    public void myKeyword() {
    }

    /**
     * Takes one `arg` and *does nothing* with it.
     *
     * Example:
     * | Your Keyword | xxx |
     * | Your Keyword | yyy |
     *
     * See `My Keyword` for no more information.
     */
    public void keyword(String arg) {
    }

    /**
     * Hyv\u00e4\u00e4 y\u00f6t\u00e4.
     *
     * \u0421\u043f\u0430\u0441\u0438\u0431\u043e!
     */
    public void nonAsciiDoc() {
    }

    /**
     * Should not be visible in library documentation
     */
    private void notAKeyword(String foobar) {
    }
}
