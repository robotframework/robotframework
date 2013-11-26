import java.util.List;
import java.util.Arrays;


public class DynamicJavaLibraryWithLists {

    public String[] getKeywordNames() {
        return new String[] {"Keyword Using Lists"};
    }

    public String runKeyword(String name, List args) {
        String result = "";
        for (Object arg : args) {
            result += " " + arg;
        }
        return result.trim();
    }

    public List getKeywordArguments(String name) {
        return Arrays.asList("first=foo", "second=bar");
    }
}
