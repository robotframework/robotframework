require 'xmlrpc/server'
require 'stringio'


class RobotXmlRpcServer<XMLRPC::Server
  
  def initialize(library, port=8080)
    @library = library
	super(port, 'localhost')
	@supported_types = [Date, Integer, Float, Fixnum, TrueClass, 
                        FalseClass, String, Hash, Array]
  end

  def get_keyword_names
    # TODO: We should only return methods implemented by this lib and possible
    # it's parents but not all implicit methods like to_s.
    return @library.methods
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

  def redirect_stdout()
    $original_stdout = $stdout.dup
    @output = ''
    $stdout = StringIO.new(@output)
  end
  
  def restore_stdout()
    $save_for_close = $stdout
    $stdout = $original_stdout
    $save_for_close.close
    return @output
  end
  
  def stop()
    shutdown
  end
  
end
