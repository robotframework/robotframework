/** 
 * Library for `libdoc.py` testing purposes.
 *
 * This library is only used in an example and it does't do anything useful.
 */
public class NoArgConstructor {

    public NoArgConstructor() {
    }

    private NoArgConstructor(String foo) {
    }

    /**
     * Does nothing 
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
