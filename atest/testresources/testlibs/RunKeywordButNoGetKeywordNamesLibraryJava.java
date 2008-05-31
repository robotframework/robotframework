public class RunKeywordButNoGetKeywordNamesLibraryJava {
    
    public String runKeyword(String name) {
        return name;
    }
    public String runKeyword(String name, Object arg) {
        return name + " " + (String)arg;
    }
    public String runKeyword(String name, Object arg1, Object arg2) {
        return name + " " + (String)arg1 + " " + (String)arg2;
    }
        
    public String someOtherKeyword(String arg1, String arg2) {
        return arg1 + " " + arg2;
    }
}
