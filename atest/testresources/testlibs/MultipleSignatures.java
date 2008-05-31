import java.util.Hashtable;

/**
 * Library with handlers having multiple implementations.
 */
public class MultipleSignatures {

    public int handler_count = 3;


    public void string_and_integer(String s) {
    }

    public void string_and_integer(int i) {
    }

    // This version should be excluded but not cause problems
    public void string_and_integer(Hashtable h) {
    }
    
    
    public void char_boolean_and_double_float_and_integer_integerarray(char c, Boolean b) {
    }

    public void char_boolean_and_double_float_and_integer_integerarray(Double d, float f) {
    }

    public void char_boolean_and_double_float_and_integer_integerarray(int i, int[] ia) {
    }


    public void empty_and_string_and_string_string() {
    }

    public void empty_and_string_and_string_string(String s) {
    }

    public void empty_and_string_and_string_string(String s1, String s2) {
    }


}
