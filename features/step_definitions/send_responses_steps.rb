When /^user "(.+)" sends "(.+)" to "(.+)"$/ do |user, response, question|
	post "/submit?identifier=#{question}&user_hash=#{user}&response=#{response}"
end

