class RubyLibraryExample

  def do_nothing
  end
  
  def failure(message)
    raise message
  end

  def error
    1/0
  end
  
  def logging(message, level='INFO')
    puts '*'+ level + '* ' + message
  end

  def one_argument(arg)
    puts 'arg: ' + arg
  end

  def two_arguments(arg1, arg2)
    puts '*INFO* arg1: ' + arg1
    puts '*INFO* arg2: ' + arg2
  end

  def arguments_with_default_values(arg1, arg2='two', arg3=42)
    puts "#{arg1} | #{arg2} | #{arg3}"
  end

  def argument_should_be_string(arg)
    argument_type_should_be(arg, String)
  end

  def argument_should_be_integer(arg)
    argument_type_should_be(arg, Fixnum)
  end

  def argument_should_be_float(arg)
    argument_type_should_be(arg, Float)
  end

  def argument_should_be_boolean(arg)
    argument_type_should_be(arg, TrueClass)
  end
  
  def argument_type_should_be(arg, type)
    if not arg.class == type
      raise Exception, 'Argument type should be '+ type.to_s() +' but was ' + arg.class.to_s()
    end    
  end

  def return_string()
    return 'Hello, world!'
  end

  def return_integer()
    return 42
  end
  
  def return_float()
    return -0.5
  end
  
  def return_boolean()
    return true
  end

  def return_multiple_values(given)
    return 'first', 2, -3.14, given
  end
  
  def return_object()
    return MyObjectToReturn.new
  end

  private 
  def private_method
  end

end


class MyObjectToReturn
  def to_s()
    return "String representation of MyObjectToReturn"
  end
end


if ARGV.size == 1
  require "robotxmlrpcserver"
  RobotXmlRpcServer.new(RubyLibraryExample.new, ARGV[0])
else
  puts "Usage: #{__FILE__} port"
end

exit
