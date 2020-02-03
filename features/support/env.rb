# codecov:
require 'simplecov'
SimpleCov.start

require 'codecov'
SimpleCov.formatter = SimpleCov::Formatter::Codecov

# NOTE: change the filename on this line to match yours!
require File.join(File.dirname(__FILE__), *%w[.. .. app.rb])

# NOTE: I deleted lines related to 'app_file'

require 'rspec/expectations'
require 'rack/test'
require 'webrat'
require 'capybara'
require 'capybara/cucumber'
require 'capybara-screenshot/cucumber'
require 'capybara/poltergeist'

Capybara.javascript_driver = :poltergeist
Capybara.server = :webrick
Capybara.save_path = "./tmp"

Webrat.configure do |config|
  config.mode = :rack
end

class MyWorld
  include Rack::Test::Methods
  include Webrat::Methods
  include Webrat::Matchers

  Webrat::Methods.delegate_to_session :response_code, :response_body

  def app
    Sinatra::Application
  end

  Capybara.app = App

end

World{MyWorld.new; Capybara.app = App}