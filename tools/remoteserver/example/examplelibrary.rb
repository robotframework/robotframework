class ExampleRemoteLibrary

  def count_items directory
    Dir.entries(directory).find_all{|i| not i.match('^\.')}.length
  end 

  def strings_should_be_equal str1, str2
    puts "Comparing '#{str1}' to '#{str2}'"
    if str1 != str2
      raise RuntimeError, "Given strings are not equal"
    end
  end

end


if __FILE__ == $0
  require "robotremoteserver"
  RobotRemoteServer.new(ExampleRemoteLibrary.new, *ARGV)
end

