import java.util.*;
import org.python.core.PyList;

public class JavaSuiteAndTestCountListener {
    public static final String ROBOT_LISTENER_API_VERSION = "2";
    private final Map<String, int[]>  data = new HashMap<String, int[]>() {{
        put("Subsuites & Subsuites2", new int[] {0,2,5});
        put("Subsuites", new int[] {0,2,2});
        put("Sub1", new int[] {1,0,1});
        put("Sub2", new int[] {1,0,1});
        put("Subsuites2", new int[] {0,2,3});
        put("Subsuite3", new int[] {2,0,2});
        put("Sub.Suite.4", new int[] {1, 0, 1});
    }};
    
    public void startSuite(String name, Map attrs) {
        int[] expCounts = data.get(name);
        checkCount(name, expCounts[0], getActual(attrs, "tests"));
        checkCount(name, expCounts[1], getActual(attrs, "suites"));
        checkCount(name, expCounts[2], getActual(attrs, "totaltests"));
    }

    private int getActual(Map attrs, String key) {
        Object item = attrs.get(key);
        try {
            return ((PyList) item).size();
        } catch (ClassCastException e) {
            return ((Integer) attrs.get(key)).intValue();
        }
    }

    private void checkCount(String name, int expected, int actual) {
        if (actual != expected) {
            throw new RuntimeException("Counts differ in "+name+" ( "+expected+" != "+actual+" )");
        }
    }
}
