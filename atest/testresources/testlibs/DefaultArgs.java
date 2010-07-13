public class DefaultArgs {
    private String args;

    public DefaultArgs(String mandatory) {
	args = mandatory;
    }

    public DefaultArgs(String mandatory, String default1) {
	args = mandatory + " & " + default1;
    }

    public DefaultArgs(String mandatory, String default1, String default2) {
	args = mandatory + " & " + default1 + " & " + default2;
    }

    public String getArgs() {
	return args;
    }
}
