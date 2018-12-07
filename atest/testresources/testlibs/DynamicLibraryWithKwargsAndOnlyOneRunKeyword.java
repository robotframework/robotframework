import java.util.*;

public class DynamicLibraryWithKwargsAndOnlyOneRunKeyword {

    public String[] getKeywordNames() {
        List<String> names = new ArrayList<String>();
        names.add("Defaults");
        names.add("All arg types");
        return names.toArray(new String[0]);
    }

    public Object runKeyword(String name, List<Object> args, Map<String, Object> kwargs) {
        String result = name + ":";
        for (Object arg : args) {
            result += " " + arg;
        }
        for (String key: kwargs.keySet())
            result += " " + key + ":" + kwargs.get(key);
        return result;
    }

    public String[] getKeywordArguments(String name) {
        if (name.equals("Defaults"))
            return new String[] {"a=1", "b=2", "c=3"};
        if (name.equals("All arg types"))
            return new String[] {"arg", "*args", "**kwargs"};
        return new String[0];
    }
}
