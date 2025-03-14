/**
 * Unit tests for the Calculator utility
 */
import { Calculator } from '../../src/utils/calculator';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add two numbers correctly', () => {
      const result = calculator.add(2, 3);
      expect(result.result).toBe(5);
      expect(result.operation).toBe('add');
      expect(result.operands).toEqual([2, 3]);
    });

    it('should add multiple numbers correctly', () => {
      const result = calculator.add(1, 2, 3, 4, 5);
      expect(result.result).toBe(15);
      expect(result.operation).toBe('add');
      expect(result.operands).toEqual([1, 2, 3, 4, 5]);
    });

    it('should throw an error if less than two numbers are provided', () => {
      expect(() => calculator.add(1)).toThrow('At least two numbers are required for addition');
    });
    
    it('should handle decimal numbers correctly', () => {
      const result = calculator.add(1.5, 2.5);
      expect(result.result).toBe(4);
    });
    
    it('should handle negative numbers correctly', () => {
      const result = calculator.add(-5, 3);
      expect(result.result).toBe(-2);
    });
  });

  describe('subtract', () => {
    it('should subtract the second number from the first', () => {
      const result = calculator.subtract(5, 3);
      expect(result.result).toBe(2);
      expect(result.operation).toBe('subtract');
      expect(result.operands).toEqual([5, 3]);
    });
    
    it('should handle negative results correctly', () => {
      const result = calculator.subtract(3, 5);
      expect(result.result).toBe(-2);
    });
    
    it('should handle decimal numbers correctly', () => {
      const result = calculator.subtract(5.5, 2.2);
      expect(result.result).toBe(3.3);
    });
  });

  describe('multiply', () => {
    it('should multiply two numbers correctly', () => {
      const result = calculator.multiply(2, 3);
      expect(result.result).toBe(6);
      expect(result.operation).toBe('multiply');
      expect(result.operands).toEqual([2, 3]);
    });

    it('should multiply multiple numbers correctly', () => {
      const result = calculator.multiply(2, 3, 4);
      expect(result.result).toBe(24);
    });

    it('should throw an error if less than two numbers are provided', () => {
      expect(() => calculator.multiply(2)).toThrow('At least two numbers are required for multiplication');
    });
    
    it('should handle multiplication by zero correctly', () => {
      const result = calculator.multiply(5, 0, 3);
      expect(result.result).toBe(0);
    });
    
    it('should handle negative numbers correctly', () => {
      const result = calculator.multiply(-2, 3);
      expect(result.result).toBe(-6);
      
      const result2 = calculator.multiply(-2, -3);
      expect(result2.result).toBe(6);
    });
  });

  describe('divide', () => {
    it('should divide the first number by the second', () => {
      const result = calculator.divide(6, 3);
      expect(result.result).toBe(2);
      expect(result.operation).toBe('divide');
      expect(result.operands).toEqual([6, 3]);
    });

    it('should throw an error when dividing by zero', () => {
      expect(() => calculator.divide(5, 0)).toThrow('Division by zero is not allowed');
    });
    
    it('should handle decimal results correctly', () => {
      const result = calculator.divide(5, 2);
      expect(result.result).toBe(2.5);
    });
    
    it('should handle negative numbers correctly', () => {
      const result = calculator.divide(-6, 3);
      expect(result.result).toBe(-2);
      
      const result2 = calculator.divide(6, -3);
      expect(result2.result).toBe(-2);
      
      const result3 = calculator.divide(-6, -3);
      expect(result3.result).toBe(2);
    });
  });

  describe('power', () => {
    it('should raise the base to the power of the exponent', () => {
      const result = calculator.power(2, 3);
      expect(result.result).toBe(8);
      expect(result.operation).toBe('power');
      expect(result.operands).toEqual([2, 3]);
    });
    
    it('should handle zero exponent correctly', () => {
      const result = calculator.power(5, 0);
      expect(result.result).toBe(1);
    });
    
    it('should handle negative exponent correctly', () => {
      const result = calculator.power(2, -2);
      expect(result.result).toBe(0.25);
    });
    
    it('should handle fractional exponent correctly', () => {
      const result = calculator.power(4, 0.5);
      expect(result.result).toBe(2);
    });
  });

  describe('sqrt', () => {
    it('should calculate the square root of a number', () => {
      const result = calculator.sqrt(9);
      expect(result.result).toBe(3);
      expect(result.operation).toBe('sqrt');
      expect(result.operands).toEqual([9]);
    });

    it('should throw an error for negative numbers', () => {
      expect(() => calculator.sqrt(-4)).toThrow('Cannot calculate square root of a negative number');
    });
    
    it('should handle decimal inputs correctly', () => {
      const result = calculator.sqrt(2);
      expect(result.result).toBeCloseTo(1.414213, 5);
    });
    
    it('should return 0 for square root of 0', () => {
      const result = calculator.sqrt(0);
      expect(result.result).toBe(0);
    });
  });

  describe('evaluateExpression', () => {
    it('should evaluate a simple addition expression', () => {
      const result = calculator.evaluateExpression('2 + 3');
      expect(result.result).toBe(5);
      expect(result.operation).toBe('evaluate');
      expect(result.expression).toBe('2 + 3');
    });
    
    it('should evaluate expressions with parentheses', () => {
      const result = calculator.evaluateExpression('(2 + 3) * 4');
      expect(result.result).toBe(20);
    });
    
    it('should throw an error for invalid expressions', () => {
      expect(() => calculator.evaluateExpression('2 + + 3')).toThrow();
    });
    
    it('should throw an error for expressions with invalid characters', () => {
      expect(() => calculator.evaluateExpression('2 + alert("hack")')).toThrow('Expression contains invalid characters');
    });
  });

  describe('memory operations', () => {
    it('should store and recall values from memory', () => {
      calculator.memorySave(5);
      expect(calculator.memoryRecall()).toBe(5);
    });

    it('should add to memory', () => {
      calculator.memorySave(5);
      calculator.memoryAdd(3);
      expect(calculator.memoryRecall()).toBe(8);
    });

    it('should subtract from memory', () => {
      calculator.memorySave(5);
      calculator.memorySubtract(3);
      expect(calculator.memoryRecall()).toBe(2);
    });

    it('should clear memory', () => {
      calculator.memorySave(5);
      calculator.memoryClear();
      expect(calculator.memoryRecall()).toBe(0);
    });
  });

  describe('history', () => {
    it('should track calculation history', () => {
      calculator.add(2, 3);
      calculator.multiply(2, 4);
      
      const history = calculator.getHistory();
      expect(history.length).toBe(2);
      expect(history[0].operation).toBe('add');
      expect(history[1].operation).toBe('multiply');
    });

    it('should clear history', () => {
      calculator.add(2, 3);
      calculator.clearHistory();
      
      const history = calculator.getHistory();
      expect(history.length).toBe(0);
    });
    
    it('should return a copy of the history array', () => {
      calculator.add(2, 3);
      const history = calculator.getHistory();
      history.push({
        result: 999,
        timestamp: new Date(),
        operation: 'fake'
      });
      
      const actualHistory = calculator.getHistory();
      expect(actualHistory.length).toBe(1);
    });
  });
  
  describe('getLastOperation', () => {
    it('should return the last operation performed', () => {
      calculator.add(2, 3);
      expect(calculator.getLastOperation()).toBe('add');
      
      calculator.multiply(2, 4);
      expect(calculator.getLastOperation()).toBe('multiply');
    });
    
    it('should return undefined if no operation has been performed', () => {
      expect(calculator.getLastOperation()).toBeUndefined();
    });
  });
});