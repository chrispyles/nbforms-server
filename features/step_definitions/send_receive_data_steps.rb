When /^I send "(.+)" for question "(.+)" in notebook "(.+)"/ do |res, q, n|
	post "/submit", {"identifier": q, "response": res, "notebook": n}
	expect(response.text).to eq("")