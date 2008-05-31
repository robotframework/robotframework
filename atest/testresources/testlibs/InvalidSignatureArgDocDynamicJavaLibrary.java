public class InvalidSignatureArgDocDynamicJavaLibrary {

    public String[] getKeywordNames() {
        return new String[] {"keyword"};
    }

    public Object runKeyword(String name, Object[] args) {
        return null;
    }

    public String getKeywordDocumentation(String name, Object invalid) {
        return "foo";
    }

    public String[] getKeywordArguments(String name, Object invalid) {
        return new String[0];
    }
}
