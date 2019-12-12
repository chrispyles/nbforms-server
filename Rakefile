require 'rubygems'
require 'sinatra/activerecord'
require 'sinatra/activerecord/rake'
require './app'

# heroku config tasks
require 'config_env/rake_tasks'
ConfigEnv.init("#{__dir__}/config/env.rb")

namespace :clear do

	desc 'Clear the database'
	task :all do
		Question.destroy_all
	end

	desc "Clear a user's responses"
	task :user, [:username] do |t, args|
		user = User.where(username: args.username).first
		if user.nil?
			user = User.where(email: args.username).first
		end
		user.questions.destroy_all
	end

end

namespace :reports do

	desc 'Generates a CSV of all responses to notebook'
	task :notebook, [:id, :out_path] do |t, args|
		questions = Question.get_all_notebook_questions args.id.to_s, true
		csv_string = rows_hash_to_csv_string questions
		if args.out_path
			File.open(args.out_path, 'w+') do |f|
				f.write csv_string
			end
		else
			puts csv_string
		end
	end

end
