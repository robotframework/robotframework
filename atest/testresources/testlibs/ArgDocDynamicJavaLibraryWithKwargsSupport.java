import java.util.*;
import org.apache.commons.lang.*;

import org.python.core.*;


public class ArgDocDynamicJavaLibraryWithKwargsSupport
  extends ArgDocDynamicJavaLibrary {

    public String[] getKeywordNames() {
        return (String[])ArrayUtils.addAll
          (super.getKeywordNames(), new String[] {
            "Java Kwargs",
            "Java Varargs and Kwargs",
          });
    }

    public Object runKeyword
      (String name, Object[] args, PyDictionary kwargs ) {

        int index = args.length;
        Object[] superArgs = Arrays.copyOf(args, index + kwargs.size());
        for (PyObject obj : kwargs.iteritems().asIterable()) {
            PyTuple item = (PyTuple)obj;
            superArgs[index++]
              = item.get(0).toString() + ':' + item.get(1).toString();
        }
        return super.runKeyword(name, superArgs);
    }

    public String[] getKeywordArguments(String name) {
        if (name.equals("Java Kwargs"))
            return new String[] {"**kwargs"};
        if (name.equals("Java Varargs and Kwargs"))
            return new String[] {"*args", "**kwargs"};
        return super.getKeywordArguments(name);
    }
}
