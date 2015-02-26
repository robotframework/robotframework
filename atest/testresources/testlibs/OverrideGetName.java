public class OverrideGetName {

    // Overrides the default getName class method, which causes TypeError
    // when OverrideGetName.getName() is called on Jython.
    public String getName() {
        return "xxx";
    }

    public void doNothing() {
    }
}
