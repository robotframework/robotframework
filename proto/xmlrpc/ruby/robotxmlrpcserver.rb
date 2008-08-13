require 'xmlrpc/server'
require 'stringio'

class RobotXmlRpcServer<XMLRPC::Server
  
  def initialize(library, port=8080)
    @library = library
	@supported_types = [Date, Integer, Float, Fixnum, TrueClass, 
                        FalseClass, String, Hash, Array]
	super(port, 'localhost')
    add_handler('robotframework', self)
    serve
  end

  def stop
    shutdown
  end

  def get_keyword_names
    # TODO: We should only return methods implemented by @library, and possibly
    # by its parents, but not all implicit methods like to_s.
    lib_methods = @library.methods
    obj_methods = Object.new.methods
    lib_methods.reject {|x| obj_methods.index(x) }
  end

  def get_keyword_arguments(name)
    args = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    begin
      @library.send(name, args)
    rescue => exception
      puts exception.message
      1
    end
  end

  def get_keyword_documentation(name)
    ''
  end

  def run_keyword(name, args)
    redirect_stdout()
    result = {'status'=>'PASS', 'return'=>'', 'message'=>'',  'output'=>''}
    begin
      return_value = @library.send(name, *args)
      result['return'] = convert_value_for_xmlrpc(return_value)
    rescue => exception
      result['status'] = 'FAIL'
      result['message'] = exception.message
    end
    result['output'] = restore_stdout()
    return result
  end
  
  def convert_value_for_xmlrpc(return_value)
    # Because ruby's xmlrpc does not support sending nil values, 
    # those have to be converter to empty strings
    if return_value == nil
      return ''
    end
    if @supported_types.include?(return_value.class)
      return return_value
    else
      return return_value.to_s
    end
  end

  def redirect_stdout
    $original_stdout = $stdout.dup
    @output = ''
    $stdout = StringIO.new(@output)
  end
  
  def restore_stdout
    $save_for_close = $stdout
    $stdout = $original_stdout
    $save_for_close.close
    return @output
  end
    
end
