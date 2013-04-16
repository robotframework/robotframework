public class ArgTypeCoercion {

    public int myInt;
    public boolean myBool;

    public ArgTypeCoercion(int myInt, boolean myBool) {
        this.myInt = myInt;
        this.myBool = myBool;
    }

    public void noArgument() {}

    public void intArgument(int arg) {
        String judgement = "";
        if (arg > 0) judgement = "greater than 0.";
        else if (arg == 0) judgement = "0.";
        else judgement = "smaller than 0.";
        System.out.println("Number " + arg + " is " + judgement);
    }

    public void booleanArgument(boolean arg) {
        if (arg)
            System.out.println("It is true!");
        else
            System.out.println("It is false!");
    }

    public void doubleArgument(double arg) {
        if (arg > 0)
            System.out.println("Got a positive argument");
    }

    public void floatArgument(float arg) {
        if (arg > 0)
            System.out.println("Got a positive argument");
    }

    public String coercableKeyword(double arg1) {
        return coercableKeyword(arg1, 0, false);
    }

    public String coercableKeyword(double arg1, int arg2) {
        return coercableKeyword(arg1, arg2, false);
    }

    public String coercableKeyword(double arg1, int arg2, boolean arg3) {
        doubleArgument(arg1);
        intArgument(arg2);
        booleanArgument(arg3);
        return "Got: " + arg1 + " and " + arg2 + " and " + arg3;
    }

    public void coercableKeywordWithCompatibleTypes(int arg1, Short arg2, Boolean arg3, float arg4) {}

    public void coercableKeywordWithCompatibleTypes(byte arg1, Long arg2, boolean arg3, Float arg4) {}

    public void coercableKeywordWithCompatibleTypes(Integer arg1, long arg2, boolean arg3, Double arg4) {}

    public void unCoercableKeyword(int arg1, boolean arg2) {}

    public void unCoercableKeyword(boolean arg1, int arg2) {}

    public void coercableAndUnCoercableArgs(boolean arg1, boolean arg2, Long arg3, String arg4) {}

    public void coercableAndUnCoercableArgs(String arg1, boolean arg2, Long arg3, String arg4) {}

    public void coercableAndUnCoercableArgs(int arg1, boolean arg2, Long arg3) {}

    public void coercableAndUnCoercableArgs(int arg1, boolean arg2, Long arg3, boolean arg4) {}

    public void primitiveAndArray(int arg1, int[] arg2) {}

}
