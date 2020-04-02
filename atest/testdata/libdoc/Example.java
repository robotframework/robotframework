import java.util.*;

/**
 * Library for `libdoc.py` testing purposes.
 *
 * This library is only used in an example and it doesn't do anything useful.
 *
 */
public class Example {
    public static final String ROBOT_LIBRARY_VERSION = "1.0 <alpha>";
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
    private Example(double dontShowMe) {
    }

    /**
     * Does nothing & <doc> has "stuff" to 'escape'!!
     *     We also got some
     *         indentation
     *         here.
     * Back in the normal indentation level.
     *
     * Tags: foo, bar
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
     * Creating varargs using `type[]`.
     */
    public void varargs1(String[] varargs) {
    }

    /**
     * Creating varargs using `type...`.
     */
    public void varargs2(int normal, int... varargs) {
    }

    /**
     * Creating varargs using `List`.
     */
    public void varargsList(List<String> varargsList) {
    }

    /**
     * Only last array or list is kwargs.
     */
    public void varargsLast(String[] normalArray, String[] varargs) {
    }

    /**
     * Only last arguments overrides.
     */
    public void lastArgument(String[] normalArray, Map<String, Object> normalMap, String normal) {
    }

    /**
     * Creating kwargs.
     */
    public void kwargs(int normal, String[] varargs, Map<String, Object> kwargs) {
    }

    /**
     * Only last map is kwargs.
     */
    public void kwargsLast(Map<String, Object> normal, Map<String, Object> kwargs) {
    }

    /**
     * Hyv\u00e4\u00e4 y\u00f6t\u00e4.
     *
     * \u0421\u043f\u0430\u0441\u0438\u0431\u043e!
     */
    public void nonAsciiDoc() {
    }

    /**
     * *DEPRECATED!?!?!!*
     */
    public void deprecation() {
    }

    /**
     * Should not be visible in library documentation
     */
    private void notAKeyword(String foobar) {
    }
}
