public class MandatoryArgs {
    private String args;

    public MandatoryArgs(Object mandatory1, Object mandatory2) {
	args = mandatory1 + " & " +  mandatory2;
    }

    public String getArgs() {
	return args;
    }

}