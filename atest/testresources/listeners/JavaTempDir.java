public class JavaTempDir {
    public static String getTempDir() {
        return System.getenv("TEMPDIR");
    }
}
