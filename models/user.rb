require 'bcrypt'
require 'securerandom'
require 'digest'

class User < ActiveRecord::Base
	has_many :questions

	def hash_username
		hashed = Digest::SHA1.hexdigest(username)
		digits = []
		15.times do
			digits << hashed[rand(hashed.length)]		
		end
		digits.join("")
	end

	def self.hash_password(password)
	  BCrypt::Password.create(password).to_s
	end

	def test_password(password)
	  BCrypt::Password.new(password_hash) == password
	end

	def self.generate_key
		api_key = SecureRandom.urlsafe_base64
		iter = 0
		while User.pluck(:api_key).uniq.include? api_key && iter < 100
			api_key = SecureRandom.urlsafe_base64
			iter += 1
		end
		api_key
	end

end