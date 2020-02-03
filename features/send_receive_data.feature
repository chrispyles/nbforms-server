Feature: Users should be able to send and receive responses

    Scenario: Send a response
    When I send "yes" for question "q1" in notebook "1"
    Then I should have a successful subimssion