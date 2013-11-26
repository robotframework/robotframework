import java.util.*;

public class ArgDocDynamicJavaLibraryWithKwargsSupport extends ArgDocDynamicJavaLibrary {

    public String[] getKeywordNames() {
        List<String> names = new ArrayList<String>(Arrays.asList(super.getKeywordNames()));
        names.add("Java Kwargs");
        names.add("Java Varargs and Kwargs");
        return names.toArray(new String[0]);
    }

    public Object runKeyword(String name, List<Object> args, Map<String, Object> kwargs) {
        List<Object> superArgs = new ArrayList<Object>(args);
        for (String key: kwargs.keySet())
            superArgs.add(key+":"+kwargs.get(key).toString());
        return super.runKeyword(name, superArgs.toArray());
    }

    public String[] getKeywordArguments(String name) {
        if (name.equals("Java Kwargs"))
            return new String[] {"**kwargs"};
        if (name.equals("Java Varargs and Kwargs"))
            return new String[] {"*args", "**kwargs"};
        return super.getKeywordArguments(name);
    }
}
