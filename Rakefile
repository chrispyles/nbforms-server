require 'rubygems'
# require 'cucumber'
# require 'cucumber/rake/task'
require 'sinatra/activerecord'
require 'sinatra/activerecord/rake'
require './app'

# Cucumber::Rake::Task.new(:features) do |t|
#   # t.cucumber_opts = "features --format pretty"
#   t.cucumber_opts = "features --format html > features.html"
# end

desc 'Clear the database'
task :clear do
  Question.destroy_all
end

namespace :clear do

	desc 'Clear the database'
	task :all do
		Question.destroy_all
	end

	desc "Clear a user's responses"
	task :user, [:username] do |t, args|
		user = User.where(username: args.username).first
		user.questions.destroy_all
	end

end

namespace :reports do

	desc 'Generates a CSV of all responses to notebook'
	task :notebook, [:id] do |t, args|
		questions = Question.get_all_notebook_questions args.notebook, true
		puts questions
	end

end
