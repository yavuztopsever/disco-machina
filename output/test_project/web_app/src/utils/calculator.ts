/**
 * Calculator utility functions for the web application.
 * Provides arithmetic operations and expression parsing.
 */

export interface CalculationResult {
  result: number;
  expression?: string;
  operation?: string;
  operands?: number[];
  timestamp: Date;
}

export interface CalculatorMemory {
  value: number;
  history: CalculationResult[];
  lastOperation?: string;
}

/**
 * Calculator class that provides arithmetic operations and memory functions.
 */
export class Calculator {
  private memory: CalculatorMemory = {
    value: 0,
    history: [],
  };

  /**
   * Adds two or more numbers together.
   * @param numbers - The numbers to add
   * @returns The result of the addition
   */
  add(...numbers: number[]): CalculationResult {
    if (numbers.length < 2) {
      throw new Error('At least two numbers are required for addition');
    }
    
    const result = numbers.reduce((sum, num) => sum + num, 0);
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'add',
      operands: numbers,
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'add';
    
    return calculationResult;
  }

  /**
   * Subtracts the second number from the first.
   * @param a - The first number
   * @param b - The number to subtract
   * @returns The result of the subtraction
   */
  subtract(a: number, b: number): CalculationResult {
    const result = a - b;
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'subtract',
      operands: [a, b],
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'subtract';
    
    return calculationResult;
  }

  /**
   * Multiplies two or more numbers together.
   * @param numbers - The numbers to multiply
   * @returns The result of the multiplication
   */
  multiply(...numbers: number[]): CalculationResult {
    if (numbers.length < 2) {
      throw new Error('At least two numbers are required for multiplication');
    }
    
    const result = numbers.reduce((product, num) => product * num, 1);
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'multiply',
      operands: numbers,
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'multiply';
    
    return calculationResult;
  }

  /**
   * Divides the first number by the second.
   * @param a - The dividend
   * @param b - The divisor
   * @returns The result of the division
   * @throws Error if divisor is zero
   */
  divide(a: number, b: number): CalculationResult {
    if (b === 0) {
      throw new Error('Division by zero is not allowed');
    }
    
    const result = a / b;
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'divide',
      operands: [a, b],
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'divide';
    
    return calculationResult;
  }

  /**
   * Raises a number to a power.
   * @param base - The base number
   * @param exponent - The exponent
   * @returns The result of the power operation
   */
  power(base: number, exponent: number): CalculationResult {
    const result = Math.pow(base, exponent);
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'power',
      operands: [base, exponent],
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'power';
    
    return calculationResult;
  }

  /**
   * Calculates the square root of a number.
   * @param number - The number to calculate the square root of
   * @returns The square root of the number
   * @throws Error if the number is negative
   */
  sqrt(number: number): CalculationResult {
    if (number < 0) {
      throw new Error('Cannot calculate square root of a negative number');
    }
    
    const result = Math.sqrt(number);
    
    const calculationResult: CalculationResult = {
      result,
      operation: 'sqrt',
      operands: [number],
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'sqrt';
    
    return calculationResult;
  }

  /**
   * Evaluates a mathematical expression string.
   * @param expression - The expression to evaluate
   * @returns The result of the evaluation
   * @throws Error for invalid or unsafe expressions
   */
  evaluateExpression(expression: string): CalculationResult {
    // Clean and validate the expression
    const cleanExpression = expression.trim();
    
    // Validate that only allowed characters are used
    const validChars = /^[0-9\s\+\-\*\/\(\)\.\^\%]+$/;
    if (!validChars.test(cleanExpression)) {
      throw new Error('Expression contains invalid characters');
    }
    
    // Evaluate in a secure way using a sandboxed approach
    // For security reasons, we use a limited set of JavaScript math operations
    // rather than using eval() which could introduce security vulnerabilities
    
    // This is a simplified implementation for demonstration
    // In a real app, you would use a proper expression parser like math.js
    
    let result: number;
    try {
      // Convert ^ to Math.pow for exponentiation
      const preparedExpression = cleanExpression.replace(/(\d+|\))\s*\^\s*(\d+|\()/g, 'Math.pow($1, $2)');
      
      // Use Function constructor instead of eval for slightly better security
      // Still not 100% secure, but better than direct eval()
      const calculate = new Function(`
        'use strict';
        // Only allow these Math methods for security
        const Math = {
          pow: window.Math.pow,
          sqrt: window.Math.sqrt,
          abs: window.Math.abs,
          round: window.Math.round,
          floor: window.Math.floor,
          ceil: window.Math.ceil,
          sin: window.Math.sin,
          cos: window.Math.cos,
          tan: window.Math.tan,
          PI: window.Math.PI,
          E: window.Math.E
        };
        return ${preparedExpression};
      `);
      
      result = calculate();
    } catch (error) {
      throw new Error(`Failed to evaluate expression: ${error instanceof Error ? error.message : String(error)}`);
    }
    
    if (!Number.isFinite(result)) {
      throw new Error('Expression resulted in an invalid number');
    }
    
    const calculationResult: CalculationResult = {
      result,
      expression: cleanExpression,
      operation: 'evaluate',
      timestamp: new Date()
    };
    
    this.memory.history.push(calculationResult);
    this.memory.lastOperation = 'evaluate';
    
    return calculationResult;
  }
  
  /**
   * Stores a value in memory.
   * @param value - The value to store
   */
  memorySave(value: number): void {
    this.memory.value = value;
  }
  
  /**
   * Adds a value to the memory.
   * @param value - The value to add to memory
   */
  memoryAdd(value: number): void {
    this.memory.value += value;
  }
  
  /**
   * Subtracts a value from the memory.
   * @param value - The value to subtract from memory
   */
  memorySubtract(value: number): void {
    this.memory.value -= value;
  }
  
  /**
   * Retrieves the value stored in memory.
   * @returns The value stored in memory
   */
  memoryRecall(): number {
    return this.memory.value;
  }
  
  /**
   * Clears the memory value.
   */
  memoryClear(): void {
    this.memory.value = 0;
  }
  
  /**
   * Gets the calculation history.
   * @returns Array of past calculations
   */
  getHistory(): CalculationResult[] {
    return [...this.memory.history];
  }
  
  /**
   * Clears the calculation history.
   */
  clearHistory(): void {
    this.memory.history = [];
  }

  /**
   * Gets the last operation performed.
   * @returns The name of the last operation
   */
  getLastOperation(): string | undefined {
    return this.memory.lastOperation;
  }
}