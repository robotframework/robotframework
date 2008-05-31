public class RunKeywordLibraryJava {

    String passKwName = "Run Keyword That Passes";
    String failKwName = "Run Keyword That Fails";
    private String[] kwNames = { passKwName, failKwName };
    
    public String[] getKeywordNames() {
        return this.kwNames;
    }

    public Object runKeyword(String name, Object[] args) {
        if (name.equals(passKwName)) {
            return this.passKw(args);
        }
        else if (name.equals(failKwName)) {
            this.failKw(args);
        }
        else {
            throw new RuntimeException("Invalid keyword name: " + name);
        }
        return null;
    }

    private String passKw(Object[] args) {
        String ret = "";
        for (int i=0; i<args.length; i++) {
            ret += (String)args[i];
        }
        return ret;
    }

    private void failKw(Object[] args) {
        String err = "Failure";
        if (args.length > 0) {
            err += ": ";
            for (int i=0; i<args.length; i++) {
                err += (String)args[i];
            }
        }
        throw new AssertionError(err);
    }

}

