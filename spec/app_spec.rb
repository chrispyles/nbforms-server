# spec/app_spec.rb
require File.expand_path '../spec_helper.rb', __FILE__

describe "My Sinatra Application" do
  it "should allow you to post a response" do 
  	post "/submit", {identifier: 'q1', user_hash: '123', response: 'a'}
  	puts last_response.status
  	expect(last_response).to be_ok
  	expect(Question.all.length).to eq(1)
  end
end