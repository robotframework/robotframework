import java.util.*;

public class JavaSuiteAndTestCountListener {
    public static final String ROBOT_LISTENER_API_VERSION = "2";
    private final Map<String, int[]>  data = new HashMap<String, int[]>() {{
        put("Subsuites & Subsuites 2", new int[] {0,2,4});
        put("Subsuites", new int[] {0,2,2});
        put("Sub 1", new int[] {1,0,1});
        put("Sub 2", new int[] {1,0,1});
        put("Subsuites 2", new int[] {0,1,2});
        put("Subsuite 3", new int[] {2,0,2});
    }};
    
    public void startSuite(String name, Map attrs) {
        int[] expCounts = data.get(name);
        checkCount(expCounts[0], getActual(attrs, "testcount"));
        checkCount(expCounts[1], getActual(attrs, "suitecount"));
        checkCount(expCounts[2], getActual(attrs, "totaltests"));
    }

    private int getActual(Map attrs, String key) {
        return ((Integer) attrs.get(key)).intValue();
    }

    private void checkCount(int expected, int actual) {
        if (actual != expected) {
            throw new RuntimeException("Counts differ");
        }
    }
}
