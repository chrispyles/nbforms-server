Feature: Send responses to server

Scenario: Send a single response
	When user "123" sends "4" to "q1"
	Then user "123" should have 1 response
	And user "123" shoud have "4" for "q1"

Scenario: Send multiple responses
	When user "123" sends "4" to "q1"
	And user "123" sends "3" to "q2"
	Then user "123" should have 1 response
	And user "123" shoud have "4" for "q1"
	And user "123" shoud have "3" for "q2"

Scenario: Send an overwriting response
	When user "123" sends "4" to "q1"
	And user "123" sends "3" to "q2"
	And user "123" sends "2" to "q2"
	Then user "123" should have 1 response
	And user "123" shoud have "2" for "q1"
	And user "123" shoud have "3" for "q2"

Scenario: Multiple users sending multiple responses
	When user "123" sends "4" to "q1"
	And user "123" sends "3" to "q2"
	And user "123" sends "2" to "q2"
	And user "098" sends "2" to "q2"
	And user "098" sends "9" to "q2"
	Then user "123" should have 1 response
	And user "123" shoud have "2" for "q1"
	And user "123" shoud have "3" for "q2"
	And user "098" shoud have "9" for "q2"
	And user "098" should not have a response for "q1"
