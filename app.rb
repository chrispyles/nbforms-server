##############################################
##### Sinatra Handler for nbforms Server #####
#####           by Chris Pyles           #####
##############################################

require 'sinatra'
require 'sinatra/flash'
require 'sinatra/activerecord'
require 'csv'
require 'json'

if Sinatra::Base.development?
	require 'byebug'
	require 'better_errors'
	configure :development do
	  use BetterErrors::Middleware
	  BetterErrors.application_root = File.expand_path('..', __FILE__)
	end
end

# load the config environment
require 'config_env'
ConfigEnv.init("config/env.rb")

# load auth helpers
require_relative './helpers/auth.rb'

# load the models
current_dir = Dir.pwd
Dir["#{current_dir}/models/*.rb"].each { |file| require file }

def rows_hash_to_csv_string rows
	csv_string = ""
	rows.each do |idx, row|
		csv_string += row.to_csv
	end
	csv_string
end

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

	# route to access custom JavaScript
	get "/assets/core.js" do
		content_type "text/javascript"
		File.read("./assets/core.js")
	end

	# route to authenticate
	post "/auth" do
		@user = User.where(username: params[:username]).first_or_initialize
		if @user.password_hash.nil?
			@user.password_hash = User.hash_password params[:password]
			@user.save
		end
		if @user.test_password params[:password]
			@user.set_api_key
		else
			"INVALID USERNAME"
		end
	end

	get '/login' do
		redirect auth_authorize_link
	end

	get '/logout' do
	  auth_sign_out
	end

	get '/auth/callback' do
	  @user = auth_process_code params[:code]
	  @user.set_api_key
	  erb :api_key
	end

	# route to submit form
	post "/submit" do
		begin
			@user = User.where(api_key: params[:api_key]).first
			@notebook = Notebook.where(identifier: params[:notebook]).first_or_create
			@question = Question.get_or_create_user_submission @user, @notebook, params[:identifier].to_s
			@question.response = params[:response]
			# @question.timestamp = Time.now
			@question.save!
			"SUBMISSION SUCCESSFUL"
		rescue
			"SUBMISSION UNSUCCESSFUL"
		end
	end

	# route to check in for attendance
	post "/attendance" do
		# begin
		@notebook = Notebook.where(identifier: params[:notebook]).first_or_create
		@user = User.where(api_key: params[:api_key]).first
		@sub = AttendanceSubmission.create!(
			user_id: @user.id, 
			submitted: DateTime.now, 
			notebook_id: @notebook.id,
			was_open: @notebook.attendance_open
		)
		"ATTENDANCE RECORDED"
		# rescue
		# 	raise 
		# 	"ATTENDANCE NOT RECORDED"
		# end
	end

	# route to extract data from questions
	get "/data" do
		@questions = params[:questions].split(',')
		@user_hashes = params[:user_hashes] == "1"
		@notebook = Notebook.where(identifier: params[:notebook]).first_or_create
		@rows = Question.to_2d_array @notebook, @questions, @user_hashes, false
		content_type 'text/csv'
		erb :csv
	end

	# route to generate a config file
	get "/config" do
		config_hash = params.slice(:server_url, :notebook, :questions)
		config_hash[:questions] = config_hash[:questions].values
		@json = JSON.pretty_generate config_hash
		erb :config_return_page
	end

end

if __FILE__ == $0
	# run app
	run App.run!
end