class RubyLibraryExample

  # Basic communication

  def passing
  end
  
  def failing(message)
    raise message
  end

  def logging(message, level='INFO')
    puts '*'+ level + '* ' + message
  end

  def returning
    'returned string'
  end

  # Argument counts

  def no_arguments
    'no arguments'
  end

  def one_argument(arg)
    arg
  end

  def two_arguments(arg1, arg2)
    arg1 + ' ' + arg2
  end

  def seven_arguments(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
    "#{arg1} #{arg2} #{arg3} #{arg4} #{arg5} #{arg6} #{arg7}"
  end

  def arguments_with_default_values(arg1, arg2='2', arg3=3)
     "#{arg1} #{arg2} #{arg3}"
  end

  def variable_number_of_arguments(*args)
    args.join(' ')
  end

  def required_defaults_and_varargs(required, default='world', *varargs)
    args = [required, default] + varargs
    args.join(' ')
  end

  # Argument types (TODO)

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

  # Return values

  def return_string()
    return 'Hello, world!'
  end

  def return_empty_string()
    return ''
  end

  def return_integer()
    return 42
  end
  
  def return_negativeinteger()
    return -1
  end
  
  def return_float()
    return 3.14
  end

  def return_negative_float()
    return -0.5
  end

  def return_zero()
    return 0
  end
  
  def return_boolean_true()
    return true
  end

  def return_boolean_false()
    return false
  end

  def return_nothing()
  end
  
  def return_object()
    return MyObject.new
  end

  def return_list()
    ['One', -2, false]
  end

  def return_empty_list()
    []
  end

  def return_list_containing_none()
    [nil]
  end

  def return_list_containing_objects()
    [MyObject.new(1), MyObject.new(2)]
  end


  private 
  def private_method
  end

end


class MyObject
  def initialize(index='')
    @index = index
  end
  def to_s()
    return "<MyObject#{@index}>"
  end
end


require "ruby/robotremoteserver"
RobotRemoteServer.new(RubyLibraryExample.new, *ARGV)

