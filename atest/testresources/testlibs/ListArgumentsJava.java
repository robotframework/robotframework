import java.util.*;


public class ListArgumentsJava {

    public ListArgumentsJava(String arg, List<String> varargs) {
    }

    public String a_0_list(List<String> args) {
        String ret = "a_0_list:";
        for (String s : args) {
            ret += " " + s;
        }
        return ret;
    }

    public String a_1_list(String arg, List<String> args) {
        String ret = "a_1_list: " + arg;
        for (String s : args) {
            ret += " " + s;
        }
        return ret;
    }
}
