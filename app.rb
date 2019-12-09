##############################################
##### Sinatra Handler for nbforms Server #####
#####           by Chris Pyles           #####
##############################################

require 'sinatra'
require 'sinatra/flash'
require 'sinatra/activerecord'
require 'csv'

# load the models
current_dir = Dir.pwd
Dir["#{current_dir}/models/*.rb"].each { |file| require file }

# app class for Sinatra
class App < Sinatra::Base

	# route to access homepage
	get "/" do
		page = erb :index
		page
	end

	# route to access CSS
	get "/assets/style.css" do
		content_type "text/css"
		File.read("./assets/style.css")
	end

	# route to authenticate
	post "/auth" do
		@user = User.where(username: params[:username]).first_or_initialize
		if @user.password_hash.nil?
			@user.password_hash = User.hash_password params[:password]
			@user.save
		end
		if @user.test_password params[:password]
			@user.api_key = User.generate_key
			@user.save
			@user.api_key
		else
			"INVALID USERNAME"
		end
	end

	# route to submit form
	post "/submit" do
		@user = User.where(username: params[:username]).first
		if @user.api_key == params[:api_key]
			@question = Question.get_or_create_user_submission @user, params[:notebook], params[:identifier]
			@question.response = params[:response]
			@question.save!
		end
	end

	# route to extract data from questions
	get "/data" do
		@questions = params[:questions].split(',')
		@user_hashes = params[:user_hashes] == "1"
		@rows = Question.to_2d_array params[:notebook], @questions, @user_hashes, false
		content_type 'text/csv'
		erb :csv
	end

end

if __FILE__ == $0
	# run app
	run App.run!
end