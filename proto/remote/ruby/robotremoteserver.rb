require 'xmlrpc/server'
require 'xmlrpc/utils'
require 'stringio'

class RobotRemoteServer<XMLRPC::Server
  
  def initialize(library, port=8270)
    @library = library
	super(port, 'localhost')
    add_handler('get_keyword_names') { get_keyword_names }
    add_handler('run_keyword') { |name,args| run_keyword(name, args) }
    add_handler('get_keyword_arguments') { |name| get_keyword_arguments(name) }
    add_handler('get_keyword_documentation') { |name| get_keyword_documentation(name) }
    add_handler('stop_remote_server') { shutdown }
    serve
  end

  def get_keyword_names
    # Would be better to include all methods actually implemeted by @library
    lib_methods = @library.methods
    obj_methods = Object.new.methods
    lib_methods.reject {|x| obj_methods.index(x) }
  end

  def run_keyword(name, args)
    redirect_stdout()
    result = {'status'=>'PASS', 'return'=>'', 'message'=>'',  'output'=>''}
    begin
      return_value = @library.send(name, *args)
      result['return'] = handle_return_value(return_value)
    rescue => exception
      result['status'] = 'FAIL'
      result['message'] = exception.message
    end
    result['output'] = restore_stdout
    return result
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

  private

  def handle_return_value(return_value)
    if [String, Integer, Fixnum, Float, TrueClass, FalseClass].include?(return_value.class)
      return return_value
    elif return_value.class == Hash
      return return_value
    elif return_value.class == Array
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
