/** 
 * Library for `libdoc.py` testing purposes.
 *
 * This library is only used in an example and it does't do anything useful.
 */
public class Example {

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
    public void yourKeyword(String arg) {
    }

    /**
     * Should not be visible in library documentation
     */
    private void notAKeyword(String foobar) {
    }
}
