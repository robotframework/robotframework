public class ArgTypeCoercion {

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

    public void coercableKeyword(String arg1) {
        coercableKeyword(arg1, 0, false);
    }

    public void coercableKeyword(String arg1, int arg2) {
        coercableKeyword(arg1, arg2, false);
    }

    public void coercableKeyword(String arg1, int arg2, boolean arg3) {
        System.out.println("Got: " + arg1 + " and " + arg2 + " and " + arg3);
        intArgument(arg2);
        booleanArgument(arg3);
    }

    public void coercableKeywordWithCompatibleTypes(int arg1, Short arg2, Boolean arg3) {}

    public void coercableKeywordWithCompatibleTypes(byte arg1, Long arg2, boolean arg3) {}

    public void coercableKeywordWithCompatibleTypes(Integer arg1, long arg2, boolean arg3) {}

    public void unCoercableKeyword(int arg1, boolean arg2) {}

    public void unCoercableKeyword(boolean arg1, int arg2) {}

    public void coercableAndUnCoercableArgs(boolean arg1, boolean arg2, Long arg3, String arg4) {}

    public void coercableAndUnCoercableArgs(int arg1, boolean arg2, Long arg3) {}

    public void coercableAndUnCoercableArgs(int arg1, boolean arg2, Long arg3, boolean arg4) {}

}
