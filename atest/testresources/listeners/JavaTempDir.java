public class JavaTempDir {
    public static String getTempDir() {
        String tmp = System.getenv("TEMP");
        if (tmp == null)
            tmp = System.getProperty("java.io.tmpdir");
        return tmp;
    }
}