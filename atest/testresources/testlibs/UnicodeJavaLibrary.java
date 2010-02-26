import java.util.Iterator;
import java.util.Arrays;

public class UnicodeJavaLibrary {

    private String[] messages = { 
        "Circle is 360\u00B0",
        "Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4",
        "\u0989\u09C4 \u09F0 \u09FA \u099F \u09EB \u09EA \u09B9" 
    };
    private String message = null;

    public UnicodeJavaLibrary() {
        this.message = this.messages[0];
        for (int i=1; i < this.messages.length; i++) {
            this.message += ", " + this.messages[i];
        }
    }

    public void printUnicodeStrings() {
        for (int i=0; i < this.messages.length; i++) {
            System.out.println("*INFO* " + this.messages[i]);
        }
    }
    
    public JavaObject printAndReturnUnicodeObject() {
        JavaObject object = new JavaObject(this.message);
        System.out.println(object);
        return object;
    }

    public JavaObject[] javaObjectArray() {
        return new JavaObject[]{ new JavaObject(this.messages[0]), new JavaObject(this.messages[1]) };
    }

    public Iterator javaIterator() {
        return Arrays.asList(messages).iterator();
    }

    public void raiseUnicodeError() {
        throw new AssertionError(this.message);
    }

}
