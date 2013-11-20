import java.util.*;

import org.python.core.*;


public class RunKeywordLibraryJavaWithKwargsSupport
  extends RunKeywordLibraryJava {

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
}
