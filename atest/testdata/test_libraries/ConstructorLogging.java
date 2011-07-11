public class ConstructorLogging {
    private static int called = 0;

    public ConstructorLogging() {
        called++;
        System.out.println("*WARN* Warning via stdout in constructor "+called);
        System.err.println("Info via stderr in constructor "+called);
    }

    public void keyword() {
    }
}
