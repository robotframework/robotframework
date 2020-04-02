import java.util.*;


public class DynamicJava {

    public String[] getKeywordNames() {
        return new String[] {"Java Types"};
    }

    public String[] getKeywordArguments(String name) {
        return new String[] {"first", "second", "third"};
    }

    public String[] getKeywordTypes(String name) {
        return new String[] {"int", "double", "list"};
    }

    @SuppressWarnings("unchecked")
    public void runKeyword(String name, Object[] args) {
        int first = (int) args[0];
        double second = (double) args[1];
        List<Integer> third = (List<Integer>) args[2];

        if (first != 42)
            throw new RuntimeException("First: " + first + " != '42'");
        if (second != 3.14)
            throw new RuntimeException("Second: " + second + " != 3.14");
        if (third.size() != 3 || third.get(0) != 1 || third.get(1) != 2 || third.get(2) != 3)
            throw new RuntimeException("Third: " + third + " != [1, 2, 3]");
    }
}
