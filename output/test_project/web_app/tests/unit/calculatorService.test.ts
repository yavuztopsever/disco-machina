/**
 * Unit tests for the Calculator Service
 */
import { CalculatorService } from '../../src/services/calculatorService';
import { ApplicationError } from '../../src/middleware/errorHandler';

describe('CalculatorService', () => {
  let calculatorService: CalculatorService;

  beforeEach(() => {
    calculatorService = new CalculatorService();
  });

  describe('performCalculation', () => {
    it('should perform addition correctly', () => {
      const request = { operation: 'add', values: [2, 3] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(5);
      expect(result.operation).toBe('add');
    });

    it('should perform subtraction correctly', () => {
      const request = { operation: 'subtract', values: [5, 3] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(2);
      expect(result.operation).toBe('subtract');
    });

    it('should perform multiplication correctly', () => {
      const request = { operation: 'multiply', values: [2, 3, 4] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(24);
      expect(result.operation).toBe('multiply');
    });

    it('should perform division correctly', () => {
      const request = { operation: 'divide', values: [6, 3] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(2);
      expect(result.operation).toBe('divide');
    });

    it('should perform power operation correctly', () => {
      const request = { operation: 'power', values: [2, 3] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(8);
      expect(result.operation).toBe('power');
    });

    it('should perform square root correctly', () => {
      const request = { operation: 'sqrt', values: [9] };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(3);
      expect(result.operation).toBe('sqrt');
    });

    it('should evaluate expressions correctly', () => {
      const request = { operation: 'evaluate', expression: '2 + 3 * 4' };
      const result = calculatorService.performCalculation(request);
      expect(result.result).toBe(14);
      expect(result.operation).toBe('evaluate');
    });

    it('should throw an error for unsupported operations', () => {
      const request = { operation: 'unknown' as any, values: [2, 3] };
      expect(() => calculatorService.performCalculation(request)).toThrow(ApplicationError);
    });

    it('should throw an error when subtraction has wrong number of values', () => {
      const request = { operation: 'subtract', values: [5, 3, 2] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Subtraction requires exactly 2 values');
    });

    it('should throw an error when division has wrong number of values', () => {
      const request = { operation: 'divide', values: [6, 3, 2] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Division requires exactly 2 values');
    });

    it('should throw an error when power operation has wrong number of values', () => {
      const request = { operation: 'power', values: [2, 3, 4] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Power operation requires exactly 2 values');
    });

    it('should throw an error when square root has wrong number of values', () => {
      const request = { operation: 'sqrt', values: [9, 16] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Square root operation requires exactly 1 value');
    });

    it('should throw an error when evaluation has no expression', () => {
      const request = { operation: 'evaluate', values: [] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Expression is required for evaluation');
    });

    it('should pass through errors from the calculator', () => {
      const request = { operation: 'divide', values: [5, 0] };
      expect(() => calculatorService.performCalculation(request)).toThrow('Division by zero is not allowed');
    });
  });

  describe('getHistory and clearHistory', () => {
    it('should return calculation history', () => {
      calculatorService.performCalculation({ operation: 'add', values: [2, 3] });
      calculatorService.performCalculation({ operation: 'multiply', values: [2, 4] });
      
      const history = calculatorService.getHistory();
      expect(history.length).toBe(2);
      expect(history[0].operation).toBe('add');
      expect(history[1].operation).toBe('multiply');
    });

    it('should clear calculation history', () => {
      calculatorService.performCalculation({ operation: 'add', values: [2, 3] });
      calculatorService.clearHistory();
      
      const history = calculatorService.getHistory();
      expect(history.length).toBe(0);
    });
  });

  describe('getStats', () => {
    it('should return operation statistics', () => {
      calculatorService.performCalculation({ operation: 'add', values: [2, 3] });
      calculatorService.performCalculation({ operation: 'add', values: [1, 4] });
      calculatorService.performCalculation({ operation: 'multiply', values: [2, 3] });
      
      const stats = calculatorService.getStats();
      expect(stats.length).toBe(2);
      
      const addStats = stats.find(stat => stat.operation === 'add');
      expect(addStats).toBeDefined();
      expect(addStats!.count).toBe(2);
      expect(addStats!.averageOperandCount).toBe(2);
      
      const multiplyStats = stats.find(stat => stat.operation === 'multiply');
      expect(multiplyStats).toBeDefined();
      expect(multiplyStats!.count).toBe(1);
    });

    it('should identify the most frequent input', () => {
      calculatorService.performCalculation({ operation: 'add', values: [2, 3] });
      calculatorService.performCalculation({ operation: 'add', values: [2, 4] });
      calculatorService.performCalculation({ operation: 'multiply', values: [2, 5] });
      
      const stats = calculatorService.getStats();
      const addStats = stats.find(stat => stat.operation === 'add');
      
      expect(addStats!.mostFrequentInput).toBe(2);
    });

    it('should handle empty statistics correctly', () => {
      const stats = calculatorService.getStats();
      expect(stats.length).toBe(0);
    });
  });

  describe('createResponse', () => {
    it('should create a properly formatted API response', () => {
      const data = { testValue: 123 };
      const response = calculatorService.createResponse(data);
      
      expect(response.success).toBe(true);
      expect(response.data).toBe(data);
      expect(response.meta).toBeDefined();
      expect(response.meta!.timestamp).toBeInstanceOf(Date);
      expect(typeof response.meta!.requestId).toBe('string');
    });
  });
});