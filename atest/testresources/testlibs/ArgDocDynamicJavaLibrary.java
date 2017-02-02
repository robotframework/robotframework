public class ArgDocDynamicJavaLibrary {

    public ArgDocDynamicJavaLibrary() {}

    public ArgDocDynamicJavaLibrary(String name) {}

    public String[] getKeywordNames() {
        return new String[] {"Java No Arg",
                             "Java One Arg",
                             "Java One or Two Args",
                             "Java Many Args",
                             "Unsupported Java Kwargs",
                             "Invalid Java Args",
                             "Invalid Java Doc"};
    }

    public Object runKeyword(String name, Object[] args) {
        System.out.print("Executed keyword " + name + " with ");
        if (args.length == 0) {
            System.out.print("no ");
        }
        System.out.print("arguments");
        for (Object arg : args) {
            System.out.print(' ' + (String)arg);
        }
        System.out.println();
        return null;
    }

    public String getKeywordDocumentation(String name) {
        if (name.equals("Invalid Java Doc"))
            throw new RuntimeException("Get doc failure");
        if (name.equals("__intro__"))
            return "Dynamic Java intro doc.";
        else if (name.equals("__init__"))
            return "Dynamic Java init doc.";
        return "Keyword documentation for " + name;
    }

    public String[] getKeywordArguments(String name) {
        if (name.equals("Java No Arg"))
            return new String[0];
        if (name.equals("Java One Arg"))
            return new String[] {"arg"};
        if (name.equals("Java One or Two Args"))
            return new String[] {"arg", "default=default"};
        if (name.equals("Java Many Args"))
            return new String[] {"*args"};
        if (name.equals("Unsupported Java Kwargs"))
            // Must raise a DataError,
            // because runKeyword has no kwargs support:
            return new String[] {"**kwargs"};
        if (name.equals("Invalid Java Args"))
            throw new RuntimeException("Get args failure");
        return null;
    }

    public String[] getKeywordTags(String name) {
        return new String[] {"tag", name};
    }
}
