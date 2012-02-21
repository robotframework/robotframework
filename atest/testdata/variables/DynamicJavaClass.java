import java.util.Map;
import java.util.HashMap;

public class DynamicJavaClass {

    public Map<String, Object> getVariables(String arg1, String arg2) {
        HashMap<String, Object> vars = new HashMap<String, Object>();
        String[] array = {arg1, arg2};
        vars.put("dynamic java string", arg1 + " " + arg2);
        vars.put("LIST__dynamic java list", array);
        return vars;
    }
}
