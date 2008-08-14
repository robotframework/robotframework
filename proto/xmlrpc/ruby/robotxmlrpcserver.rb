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
    # Would be better to include all methods actually implemeted by @library
    lib_methods = @library.methods
    obj_methods = Object.new.methods
    lib_methods.reject {|x| obj_methods.index(x) }
  end

  def get_keyword_arguments(name)
    # This algorithm doesn't return correct number of maximum arguments when 
    # args have default values. It seems that there's no easy way to get that
    # in formation in Ruby, see e.g. http://www.ruby-forum.com/topic/147614.
    # Additionally it would be much better to return real argument names 
    # because that information could be used to create librart documentation. 
    arity = @library.method(name).arity
    if arity >= 0
      return ['arg'] * arity
    else
      return ['arg'] * (arity.abs - 1) + ['*args']
    end
  end

  def get_keyword_documentation(name)
    # Is there a way to implement this? Would mainly allow creating a library
    # documentation, but if real argument names are not got that's probably
    # not so relevant.
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
    result['output'] = restore_stdout
    return result
  end
  
  private

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
