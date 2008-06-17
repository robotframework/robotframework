#!ruby
require 'rubygems' # required to make gem-finding work. must be a better way
require 'test/unit'
require 'flexmock/test_unit'
require 'src/auth'

class TestPassword < Test::Unit::TestCase
  def test_validate_password_returns_true_when_all_conventions_met
    password = Password.new "a0!aaa"
	  assert password.valid?
  end
  
  def test_validate_password_returns_false_when_password_less_than_6_chars
    password = Password.new "a0!aa"
    assert !password.valid?
  end
  
  def test_validate_password_returns_false_when_password_too_long
    password = Password.new "a0!aaaaaaaaaa"
    assert !password.valid?
  end
  
  def test_validate_password_returns_false_when_password_missing_punctuation
    password = Password.new "aaaaa0"
    assert !password.valid?
  end
  
  def test_validate_password_returns_false_when_password_missing_letter
    password = Password.new "!!!!00"
    assert !password.valid?
  end
  
  def test_validate_password_returns_false_when_password_missing_number
    password = Password.new "!!!!!A"
    assert !password.valid?
  end
end

class TestAuth < Test::Unit::TestCase  
  
  attr :auth
  
  def setup
    # using mocks to avoid polluting real pwds file with test data
    pwd_file = flexmock("passwordfile")
    pwd_file.should_receive(:get_users).and_return({})
    pwd_file.should_receive(:save).and_return({})
    @auth = Authentication.new(pwd_file)
  end
  
  def test_valid_user_can_log_in
    @auth.create("sam", "a0!aaa")
    return_code = @auth.login("sam", "a0!aaa")
    assert @auth.get_user("sam").logged_in?, "Expected user should be logged in"
    assert_equal :logged_in, return_code
  end
  
  def test_auth_return_code_is_access_denied_if_login_fails
    return_code = @auth.login("aasdjfj", "")
    assert_equal :access_denied, return_code
  end
  
  def test_account_exists_returns_true_if_account_exists_with_username
    @auth.create("fred", "f0!ble")
    assert @auth.account_exists?("fred")
  end
  
  def test_account_exists_returns_false_if_no_account_with_username
    assert !@auth.account_exists?("foo")
  end
  
  def test_create_user_adds_new_user_to_list_with_user_data_and_returns_success
    assert !@auth.account_exists?("newacc")
    return_code = @auth.create("newacc", "d3f!lt")
    assert @auth.account_exists?("newacc")
    assert_equal :success, return_code
  end
  
end

class TestCmd < Test::Unit::TestCase
  attr :auth
  
  def setup
    @auth = flexmock("Authentication")
  end

  def test_command_sent_to_auth_object
    @auth.should_receive(:create).once
    return_code = CommandLine.CalledWith(@auth, ["create"])
  end
  
  def test_undefined_command_returns_error_message
    return_code = CommandLine.CalledWith(@auth, ["nosuchcommand"])
    assert_equal "Auth Server: unknown command 'nosuchcommand'", return_code
  end
end

class TestErrs < Test::Unit::TestCase
  def test_can_retrieve_messages
    assert_equal "SUCCESS", Messages.lookup(:success)
  end
end


