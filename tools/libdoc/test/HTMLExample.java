/** 
 * Library for <a
 * href="http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool"
 * style="color: red; font-variant: small-caps; letter-spacing: 0.1em">
 * libdoc.py</a> testing purposes.
 *
 * This library is only used in an example containing
 * <b><blink>HTML</blink></b> and it does't do anything useful.
 */
public class HTMLExample {

    /**
     * Creates new <i>HTMLExample</i> test library 
     */
    public HTMLExample() {
    }


    /**
     * Doesn't do anytying useful but has <b>HTML</b> in the doc.
     *
     * <pre>
     * Some pre-formatted
     * ----- text -------
     * </pre>
     *
     * <i>Formatting</i> and <a href="http://foo.bar">links</a>.
     * <p>
     * <b><i>Examples:</i></b>
     * <table>
     *   <tr><td>HTML Keyword</td><td>something</td></tr>
     *   <tr><td>HTML Keyword</td><td>whatever</td></tr>
     * </table>
     */
    public void htmlKeyword(String arg) {
    }

    /**
     * <b>Should not</b> be visible in library documentation
     */
    private void notAKeyword(String foobar) {
    }
}
