public class ArgDocDynamicJavaLibrary {

    public ArgDocDynamicJavaLibrary() {}

    public ArgDocDynamicJavaLibrary(String name) {}

    public String[] getKeywordNames() {
        return new String[] {"Java No Arg",
                             "Java One Arg",
                             "Java One or Two Args",
                             "Java Many Args",
                             "Invalid Java Args",
                             "Invalid Java Doc"};
    }

    public Object runKeyword(String name, Object[] args) {
        System.out.println("Executed keyword " + name + " with arguments " + args);
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
        if (name.equals("Invalid Java Args"))
            throw new RuntimeException("Get args failure");
        return null;
    }
}
