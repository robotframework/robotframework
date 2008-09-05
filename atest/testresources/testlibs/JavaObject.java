import java.util.HashMap;

public class JavaObject {

    private String name;
    public String publicString;
    public int publicInt;

    public JavaObject() {
        this.name = "";
        this.publicString = "";
        this.publicInt = 42;
    }

    public JavaObject(String name) {
        this.name = name;
        this.publicString = name;
        this.publicInt = 42;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return this.name;
    }

    public String toString() {
        return this.name;
    }
    
    public void exception() {
        new HashMap(-1);
    }
}
