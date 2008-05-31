import java.util.HashMap;

public class JavaObject {

    private String name;

    public JavaObject() {
        this.name = "";
    }

    public JavaObject(String name) {
        this.name = name;
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
