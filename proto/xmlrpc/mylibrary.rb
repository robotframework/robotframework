class MyLibrary
  
  def divide(a, b)
    return Float(a) / Float(b)
  end
  
  def raise_failure(message)
    raise message
  end
  
  def logging(message, level='INFO')
    puts '*'+ level + '* ' + message
  end
  
  def return_nothing()
    return nil
  end
  
  def return_multiple_values(value1, value2)
    return value1, value2
  end
  
  def check_argument_is_boolean_type_true(arg)
    arguments_type_should_be(arg, TrueClass)
    return arg
  end
  
  def return_true()
    return true
  end

  def check_argument_is_string_type(arg)
    arguments_type_should_be(arg, String)
    return arg
  end

  def arguments_type_should_be(arg, type)
    if not arg.class == type
      raise Exception, 'Arguments type should be '+ type.to_s() +' but was ' + arg.class.to_s()
    end    
  end
  
  def should_be_list(arg)
    if arg != ['a','b','c'] 
      raise Exception, "Given list is not ['a', 'b', 'c']"
    end
    return arg
  end
  
  def should_be_dictionary(arg)
    if arg != {'a'=> 1, 'b'=>'Hello', 'c' => ['a', 1]}
      raise Exception, "Given argument is not {'a'=> 1, 'b'=>'Hello', 'c' => ['a', 1]}"
    end
    return arg
  end
  
  def return_object()
    return MyObject.new
  end
end

class MyObject
  def to_s()
    return "String representation of MyObject"
  end
end



#METHODS FOR STARTING THE LIBRARY FROM COMMAND LINE

def start(port)
  $: << File.expand_path(File.dirname(__FILE__))
  require "robotxmlrpcserver"
  r = RobotXmlRpcServer.new(MyLibrary.new, port)
  r.add_handler("robot", r)
  r.serve
end

def help
  print "
  Usage: #{__FILE__} port
"
end

if ARGV.size != 1
  help
else
  start(ARGV[0])
end
exit


