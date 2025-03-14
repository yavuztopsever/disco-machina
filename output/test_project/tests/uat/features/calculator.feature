Feature: Calculator Operations
  As a user of the calculator application
  I want to perform basic arithmetic operations
  So that I can get accurate calculation results

  Scenario: Adding two numbers
    Given I have a calculator
    When I add 5 and 3
    Then the result should be 8

  Scenario: Subtracting a number
    Given I have a calculator
    When I subtract 4 from 10
    Then the result should be 6

  Scenario: Multiplying two numbers
    Given I have a calculator
    When I multiply 6 by 7
    Then the result should be 42

  Scenario: Dividing two numbers
    Given I have a calculator
    When I divide 20 by 5
    Then the result should be 4

  Scenario: Dividing by zero
    Given I have a calculator
    When I try to divide 10 by 0
    Then I should get a division by zero error

  Scenario Outline: Performing various calculations
    Given I have a calculator
    When I perform "<operation>" with <first> and <second>
    Then the result should be <expected>

    Examples:
      | operation | first | second | expected |
      | add       | 10    | 5      | 15       |
      | subtract  | 15    | 7      | 8        |
      | multiply  | 3     | 4      | 12       |
      | divide    | 12    | 3      | 4        |