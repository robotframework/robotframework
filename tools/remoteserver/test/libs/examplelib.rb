class RubyLibraryExample

  def get_server_language
    'ruby'
  end

  # Basic communication

  def passing
  end
  
  def failing(message)
    raise message
  end

  def logging(message, level='INFO')
    puts "*#{level}* #{message}"
  end

  def returning
    'returned string'
  end

  # Logging

  def one_message_without_level
	puts 'Hello, world!'
  end	 

  def multiple_messages_with_different_levels
		puts 'Info message'
		puts '*DEBUG* Debug message'
		puts '*INFO* Second info'
		puts 'this time with two lines'
		puts '*INFO* Third info'
		puts '*TRACE* This is ignored'
		puts '*WARN* Warning'
  end
  
  def logging_and_failing
		puts '*INFO* This keyword will fail!'
    puts '*WARN* Run for your lives!!'
    raise RuntimeError, 'Too slow'
	end

	def logging_and_returning
		puts 'Logged message'
    'Returned value'
	end

	def log_control_char
  	puts "\x01"
	end
	
  # Failures

  def base_exception
    raise Exception, 'My message'
  end

  def exception_without_message
	raise Exception
  end

  def runtime_error
	raise RuntimeError, 'Error message'
  end
 
  def name_error
    non_existing
  end

  def attribute_error
    ''.non_existing
  end

  def zero_division
    1/0
  end

  def custom_exception
    raise MyException, 'My message'
  end

  def failure_deeper(rounds=10)
    if rounds == 1
      raise RuntimeError, 'Finally failing'
	end
	failure_deeper(rounds-1)
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

  # Argument types

  def string_as_argument(arg)
    should_be_equal(arg, return_string)
  end

  def unicode_string_as_argument(arg)
    should_be_equal(arg, return_unicode_string)
  end

  def empty_string_as_argument(arg)
    should_be_equal(arg, '')
  end

  def integer_as_argument(arg)
    should_be_equal(arg, return_integer)
  end

  def negative_integer_as_argument(arg)
    should_be_equal(arg, return_negative_integer)
  end

  def float_as_argument(arg)
    should_be_equal(arg, return_float)
  end

  def negative_float_as_argument(arg)
    should_be_equal(arg, return_negative_float)
  end

  def zero_as_argument(arg)
    should_be_equal(arg, 0)
  end

  def boolean_true_as_argument(arg)
    should_be_equal(arg, true, 1)
  end

  def boolean_false_as_argument(arg)
    should_be_equal(arg, false, 0)
  end

  def none_as_argument(arg)
    should_be_equal(arg, '')
  end

  def object_as_argument(arg)
    should_be_equal(arg, '<MyObject>')
  end

  def list_as_argument(arg)
    should_be_equal(arg, ['One', -2, false], ['One', -2, 0])
  end

  def empty_list_as_argument(arg)
    should_be_equal(arg, [])
  end

  def list_containing_none_as_argument(arg)
    should_be_equal(arg, [''])
  end

  def list_containing_objects_as_argument(arg)
    should_be_equal(arg, ['<MyObject1>', '<MyObject2>'])
  end

  def nested_list_as_argument(arg)
     exp = [ [true, false], [[1, '', '<MyObject>', {}]] ]
     exp2 = [ [1, 0], [[1, '', '<MyObject>', {}]] ]
    should_be_equal(arg, exp, exp2)
  end

  def dictionary_as_argument(arg)
    should_be_equal(arg, {'one'=>1, 'spam'=>'eggs'})
  end

  def empty_dictionary_as_argument(arg)
    should_be_equal(arg, {})
  end

  def dictionary_with_non_string_keys_as_argument(arg)
    should_be_equal(arg, {'1'=>2, ''=>true}, {'1'=>2, ''=>1})
  end

  def dictionary_containing_none_as_argument(arg)
    should_be_equal(arg, {'As value'=>'', ''=>'As key'})
  end

  def dictionary_containing_objects_as_argument(arg)
    should_be_equal(arg, {'As value'=>'<MyObject1>', '<MyObject2>'=>'As key'})
  end

  def nested_dictionary_as_argument(arg)
    exp = { '1'=>{''=>false},
            '2'=>{'A'=>{'n'=>''}, 'B'=>{'o'=>'<MyObject>', 'e'=>{}}} }
    exp2 = { '1'=>{''=>0},
            '2'=>{'A'=>{'n'=>''}, 'B'=>{'o'=>'<MyObject>', 'e'=>{}}} }
    should_be_equal(arg, exp, exp2)
  end

  # Return values

  def return_string
    'Hello, world!'
  end

  def return_empty_string
    ''
  end

  def return_symbol
    :symbol
  end

  def return_integer
    42
  end
  
  def return_negative_integer
    -1
  end
  
  def return_float
    3.14
  end

  def return_negative_float
    -0.5
  end

  def return_zero
    0
  end
  
  def return_boolean_true
    true
  end

  def return_boolean_false
    false
  end

  def return_nothing
  end
  
  def return_object
    MyObject.new
  end

  def return_list
    [:One, -2, false]
  end

  def return_empty_list
    []
  end

  def return_list_containing_none
    [nil]
  end

  def return_list_containing_objects
    [MyObject.new(1), MyObject.new(2)]
  end

  def return_nested_list
    [ [true, false], [[1, nil, MyObject.new, {}]] ]
  end
        
  def return_dictionary
    {'one'=>1, :spam=>:eggs}
  end

  def return_empty_dictionary
    {}
  end

  def return_dictionary_with_non_string_keys
    {1=>2, false=>true}
  end

  def return_dictionary_containing_none
    {'As value'=>nil, nil=>'As key'}
  end

  def return_dictionary_containing_objects
    {'As value'=>MyObject.new(1), MyObject.new(2)=>'As key'}
  end

  def return_nested_dictionary
    { 1=>{true=>false},
      2=>{'A'=>{'n'=>nil}, 'B'=>{'o'=>MyObject.new, 'e'=>{}}} }
  end

	def return_control_char
  	"\x01"
	end
	
  @@attribute = "Not keyword"

  private 

  def private_method
  end

  def should_be_equal(arg, exp, exp2=nil)
		# exp2 is used because true/false are converted to 1/0 with Jython2.2
    if arg != exp and arg !=exp2
      raise "#{arg} != #{exp}"
    end    
  end

end


class MyObject
  def initialize(index='')
    @index = index
  end
  def to_s
    "<MyObject#{@index}>"
  end
end

class MyException<Exception
end

require "robotremoteserver"
RobotRemoteServer.new(RubyLibraryExample.new, *ARGV)

