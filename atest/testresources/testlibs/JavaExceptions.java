import java.io.IOException;

public class JavaExceptions {

    /* base class is java.lang.Error */
    public void throwAssertionError(String msg) {
        if (msg == null) {
            throw new AssertionError();
        }
        else {
            throw new AssertionError(msg);
        }
    }

    /* base class is java.lang.RuntimeException */
    public void throwArithmeticException(String msg) {
        if (msg == null) {
            throw new ArithmeticException();
        }
        else {
            throw new ArithmeticException(msg);
        }
    }

    public void throwRuntimeException(String msg) {
        if (msg == null) {
            throw new RuntimeException();
        }
        else {
            throw new RuntimeException(msg);
        }
    }

    /* base class is java.lang.Exception */
    public void throwIOException(String msg) throws IOException {
        if (msg == null) {
            throw new IOException();
        }
        else {
            throw new IOException(msg);
        }
    }

    public void throwExitOnFailure() {
        throw new FatalCatastrophyException();
    }

}
