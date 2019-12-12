require 'bcrypt'
require 'digest'

class User < ActiveRecord::Base
	has_many :questions
	validates :api_key, uniqueness: true

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

	def set_api_key
		self.api_key = Digest::SHA256.hexdigest "#{email || username}#{Time.now}"
		self.save!
		self.api_key
	end

end