class RubyLibraryExample

  def do_nothing()
  end
  
  def failure(message)
    raise message
  end
  
  def logging(message, level='INFO')
    puts '*'+ level + '* ' + message
  end

  def one_argument(arg)
    puts 'arg: ' + arg
  end

  def two_arguments(arg1, arg2)
    puts 'arg1: ' + arg1
    puts 'arg2: ' + arg2
  end

  def arguments_with_default_values(arg1, arg2='default value', arg3=nil)
    puts 'arg1: ' + arg1
    puts 'arg2: ' + arg2
    puts 'arg3: ' + arg3
  end

  def argument_should_be_boolean_true(arg)
    argument_type_should_be(arg, TrueClass)
  end
  
  def argument_should_be_string(arg)
    argument_type_should_be(arg, String)
  end

  def argument_type_should_be(arg, type)
    if not arg.class == type
      raise Exception, 'Argument type should be '+ type.to_s() +' but was ' + arg.class.to_s()
    end    
  end

  def return_string()
    return 'Hello, world!'
  end
  
  def return_object()
    return MyObjectToReturn.new
  end

  def return_true()
    return true
  end

  def return_multiple_values(given)
    return 'first', 2, given
  end
  
  def divide(a, b)
    return Float(a) / Float(b)
  end
    
end


class MyObjectToReturn
  def to_s()
    return "String representation of MyObject"
  end
end


if ARGV.size == 1
  require "robotxmlrpcserver"
  RobotXmlRpcServer.new(RubyLibraryExample.new, ARGV[0])
else
  puts "Usage: #{__FILE__} port"
end

exit
