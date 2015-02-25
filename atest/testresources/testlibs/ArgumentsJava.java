import java.util.*;

public class ArgumentsJava {

    public ArgumentsJava(String arg, String[] varargs) {
    }

    public String a_0() {
        return "a_0";
    }

    public String a_1(String arg) {
        return "a_1: " + arg;
    }

    public String a_3(String arg1, String arg2, String arg3) {
        return "a_3: " + arg1 + " " + arg2 + " " + arg3;
    }

    public String a_0_1() {
        return a_0_1("default");
    }

    public String a_0_1(String arg) {
        return "a_0_1: " + arg;
    }

    public String a_1_3(String arg1) {
        return a_1_3(arg1, "default");
    }

    public String a_1_3(String arg1, String arg2) {
        return a_1_3(arg1, arg2, "default");
    }

    public String a_1_3(String arg1, String arg2, String arg3) {
        return "a_1_3: " + arg1 + " " + arg2 + " " + arg3;
    }

    public String a_0_n(String[] args) {
        String ret = "a_0_n:";
        for (int i=0; i < args.length; i++) {
            ret += " " + args[i];
        }
        return ret;
    }

    public String a_1_n(String arg, String[] args) {
        String ret = "a_1_n: " + arg;
        for (int i=0; i < args.length; i++) {
            ret += " " + args[i];
        }
        return ret;
    }

    public Map<String, Object> getJavaMap(Map<String, Object> kwargs) {
        return new HashMap<String, Object>(kwargs);
    }

    public String javaVarargs(String... args) {
        String ret = "javaVarArgs:";
        for (String arg: args)
            ret += " " + arg;
        return ret;
    }

    public String javaKWArgs(Map<String,Object> kwargs) {
        String ret = "javaKWArgs:";
        SortedSet<String> keys = new TreeSet<String>(kwargs.keySet());
        for (String key: keys)
            ret += " " + key + ":" + kwargs.get(key);
        return ret;
    }

    public String javaNormalAndKWArgs(String arg, Map<String,Object> kwargs) {
        String ret = "javaNormalAndKWArgs: "+arg;
        SortedSet<String> keys = new TreeSet<String>(kwargs.keySet());
        for (String key: keys)
            ret += " " + key + ":" + kwargs.get(key);
        return ret;
    }

    public String javaVarArgsAndKWArgs(List<String> varargs, Map<String,Object> kwargs) {
        String ret = "javaVarArgsAndKWArgs:";
        for (String arg: varargs)
            ret += " " + arg;
        SortedSet<String> keys = new TreeSet<String>(kwargs.keySet());
        for (String key: keys)
            ret += " " + key + ":" + kwargs.get(key);
        return ret;
    }

    public String javaAllArgs(String arg, String[] varargs, Map<String,Object> kwargs) {
        String ret = "javaAllArgs: "+arg;
        for (String a: varargs)
            ret += " " + a;
        SortedSet<String> keys = new TreeSet<String>(kwargs.keySet());
        for (String key: keys)
            ret += " " + key + ":" + kwargs.get(key);
        return ret;
    }

    public String javaManyNormalArgs(String arg, String arg2, Map<String,Object> kwargs) {
        String ret = "javaManyNormalArgs: "+arg+" "+arg2;
        SortedSet<String> keys = new TreeSet<String>(kwargs.keySet());
        for (String key: keys)
            ret += " " + key + ":" + kwargs.get(key);
        return ret;
    }

    public String hashmapArg(HashMap<String, Object> map) {
        String ret = "hashmapArg:";
        SortedSet<String> keys = new TreeSet<String>(map.keySet());
        for (String key: keys)
            ret += " " + key + ":" + map.get(key);
        return ret;
    }
}
