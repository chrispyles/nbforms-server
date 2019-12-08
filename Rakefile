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

