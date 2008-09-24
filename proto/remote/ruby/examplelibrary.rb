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

  # Errors

  def name_error
    non_existing
  end

  def attribute_error
    @non_existing
  end

  def index_error
    [][0]
  end

  def zero_division
    1/0
  end

  def custom_exception
    raise MyException, 'My message'
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
    should_be_equal(arg, true)
  end

  def boolean_false_as_argument(arg)
    should_be_equal(arg, false)
  end

  def none_as_argument(arg)
    should_be_equal(arg, '')
  end

  def object_as_argument(arg)
    should_be_equal(arg, '<MyObject>')
  end

  def list_as_argument(arg)
    should_be_equal(arg, ['One', -2, false])
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
    should_be_equal(arg, exp)
  end

  def dictionary_as_argument(arg)
    should_be_equal(arg, {'one'=>1, 'spam'=>'eggs'})
  end

  def empty_dictionary_as_argument(arg)
    should_be_equal(arg, {})
  end

  def dictionary_with_non_string_keys_as_argument(arg)
    should_be_equal(arg, {'1'=>2, 'False'=>true})
  end

  def dictionary_containing_none_as_argument(arg)
    should_be_equal(arg, {'As value'=>'', ''=>'As key'})
  end

  def dictionary_containing_objects_as_argument(arg)
    should_be_equal(arg, {'As value'=>'<MyObject1>', '<MyObject2>'=>'As key'})
  end

  def nested_dictionary_as_argument(arg)
    exp = { '1'=>{'True'=>false},
            '2'=>{'A'=>{'n'=>''}, 'B'=>{'o'=>'<MyObject>', 'e'=>{}}} }
    should_be_equal(arg, exp)
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

  @@attribute = "Not keyword"

  private 

  def private_method
  end

  def should_be_equal(arg, exp)
    if arg != exp
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

require "ruby/robotremoteserver"
RobotRemoteServer.new(RubyLibraryExample.new, *ARGV)

