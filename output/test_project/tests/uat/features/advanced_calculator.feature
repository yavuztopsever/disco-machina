Feature: Advanced Calculator Operations
  As a power user of the calculator application
  I want to perform complex arithmetic operations and use memory features
  So that I can perform sophisticated calculations efficiently

  Scenario: Raising a number to a power
    Given I have a calculator
    When I set the initial value to 2.0
    And I raise it to the power of 3
    Then the result should be 8

  Scenario: Taking a square root
    Given I have a calculator
    When I set the initial value to 16.0
    And I take the square root
    Then the result should be 4

  Scenario: Working with memory functions
    Given I have a calculator
    When I set the initial value to 10.0
    And I store the result in memory
    And I clear the result
    And I add the memory value to the result
    Then the result should be 10

  Scenario: Evaluating a complex expression
    Given I have a calculator
    When I evaluate the expression "2 + 3 * 4"
    Then the result should be 14

  Scenario: Handling calculation errors
    Given I have a calculator
    When I set the initial value to -4.0
    Then taking the square root should give an error
    
  Scenario: Using interactive mode commands
    Given I am using the calculator in interactive mode
    When I enter command "+ 5"
    And I enter command "* 3"
    And I enter command "- 2"
    Then the final result should be 13

  Scenario Outline: Performing advanced operations
    Given I have a calculator
    When I set the initial value to <initial>
    And I perform "<operation>" with value <operand>
    Then the result should be <expected>

    Examples:
      | initial | operation | operand | expected |
      | 2.0     | power     | 3.0     | 8        |
      | 16.0    | sqrt      | 0.0     | 4        |
      | 10.0    | multiply  | 1.5     | 15       |
      | 20.0    | divide    | 4.0     | 5        |

  Scenario: Chaining multiple operations
    Given I have a calculator
    When I perform the following operations
      | operation | value |
      | add       | 10.0  |
      | multiply  | 2.0   |
      | subtract  | 5.0   |
      | divide    | 3.0   |
    Then the result should be 5