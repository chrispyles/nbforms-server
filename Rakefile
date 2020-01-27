require 'rubygems'
require 'sinatra/activerecord'
require 'sinatra/activerecord/rake'
require './app'
require 'csv'

# heroku config tasks
require 'config_env/rake_tasks'
ConfigEnv.init("#{__dir__}/config/env.rb")

namespace :attendance do

	desc 'Open attendance checks' 
	task :open, [:notebook] do |t, args|
		notebook = Notebook.where(identifier: args.notebook).first_or_create
		notebook.update!(attendance_open: true)
	end

	desc 'Close attendance checks' 
	task :close, [:notebook] do |t, args|
		notebook = Notebook.where(identifier: args.notebook).first_or_create
		notebook.update!(attendance_open: false)
	end

	desc "Get a report of a notebook's attendance"
	task :report, [:notebook] do |t, args|
		if !args.notebook.nil?
			notebook = Notebook.where(identifier: args.notebook.to_s).first_or_create
			subs = AttendanceSubmission.where(notebook_id: notebook.id)
		end
		csv_string = AttendanceSubmission.to_csv subs, args.notebook.nil?
		puts csv_string
	end

end

namespace :lock do

	desc 'Lock a question from being queried'
	task :question, [:notebook, :question] do |t, args|
		q = Question.where(notebook_id: args.notebook.to_s, identifier: args.question.to_s).first
		q.update!(locked: true)
	end

	desc 'Lock a notebook from being queried'
	task :notebook, [:notebook] do |t, args|
		notebook = Notebook.where(identifier: args.notebook.to_s).first_or_create
		notebook.questions.each do |q|
			q.update!(locked: true)
		end
	end

end

namespace :unlock do

	desc 'Unlock a question from being queried'
	task :question, [:notebook, :question] do |t, args|
		q = Question.where(notebook_id: args.notebook.to_s, identifier: args.question.to_s).first
		q.update!(locked: false)
	end

	desc 'Unlock a notebook from being queried'
	task :notebook, [:notebook] do |t, args|
		notebook = Notebook.where(identifier: args.notebook.to_s).first_or_create
		notebook.questions.each do |q|
			q.update!(locked: false)
		end
	end

end

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

	desc "Clear all submissions for a notebook"
	task :notebook, [:notebook] do |t, args|
		nb = Notebook.where(identifier: args.notebook.to_s).first
		nb.questions.destroy_all
	end

end

namespace :reports do

	desc 'Generates a CSV of all responses to notebook'
	task :responses, [:id, :out_path] do |t, args|
		notebook = Notebook.where(identifier: args.id.to_s).first
		questions = Question.get_all_notebook_questions notebook, true
		csv_string = rows_hash_to_csv_string questions
		if args.out_path
			File.open(args.out_path, 'w+') do |f|
				f.write csv_string
			end
		else
			puts csv_string
		end
	end

	desc 'Generates a detailed list of notebooks and their attributes'
	task :notebooks do
		csv = CSV.generate do |csv|
			csv << Notebook.attribute_names
			Notebook.order(:id).each do |nb|
				csv << nb.attributes.values
			end
		end
		puts csv
	end

end
