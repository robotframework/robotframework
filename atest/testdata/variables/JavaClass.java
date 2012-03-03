public class JavaClass {
    public static String javaString = "hi";
    public int javaInteger;
    public static String[] LIST__javaList = {"x", "y", "z"};
    private String javaProperty;

    public JavaClass() {
        javaInteger = -1;
        javaProperty = "default";
    }

    public void javaMethod() {}

    public String getJavaProperty() {
        return javaProperty;
    }

    public void setJavaProperty(String value) {
        javaProperty = value;
    }
}
