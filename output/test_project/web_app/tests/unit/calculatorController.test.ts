/**
 * Unit tests for Calculator Controller
 */
import { Request, Response } from 'express';
import { CalculatorController } from '../../src/api/calculatorController';
import { CalculatorService } from '../../src/services/calculatorService';
import { ValidationError } from '../../src/middleware/errorHandler';

// Mock CalculatorService
jest.mock('../../src/services/calculatorService');

describe('CalculatorController', () => {
  let calculatorController: CalculatorController;
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: jest.Mock;
  
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup controller with mocked service
    calculatorController = new CalculatorController();
    
    // Mock request and response
    mockRequest = {
      body: {}
    };
    
    mockResponse = {
      json: jest.fn()
    };
    
    mockNext = jest.fn();
    
    // Mock CalculatorService methods
    const mockCalculatorService = CalculatorService.prototype;
    mockCalculatorService.performCalculation = jest.fn().mockImplementation((request) => {
      if (request.operation === 'divide' && request.values[1] === 0) {
        throw new Error('Division by zero is not allowed');
      }
      return {
        result: 5,
        operation: request.operation,
        timestamp: new Date()
      };
    });
    
    mockCalculatorService.getHistory = jest.fn().mockReturnValue([
      { result: 5, operation: 'add', timestamp: new Date() }
    ]);
    
    mockCalculatorService.clearHistory = jest.fn();
    
    mockCalculatorService.getStats = jest.fn().mockReturnValue([
      { operation: 'add', count: 2, averageOperandCount: 2 }
    ]);
    
    mockCalculatorService.createResponse = jest.fn().mockImplementation((data) => ({
      success: true,
      data,
      meta: {
        timestamp: new Date(),
        requestId: 'test-id'
      }
    }));
  });
  
  describe('calculate', () => {
    it('should return calculation result for valid request', async () => {
      mockRequest.body = {
        operation: 'add',
        values: [2, 3]
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(CalculatorService.prototype.performCalculation).toHaveBeenCalledWith({
        operation: 'add',
        values: [2, 3]
      });
      
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.objectContaining({
          result: 5,
          operation: 'add'
        })
      }));
    });
    
    it('should handle validation errors for missing operation', async () => {
      mockRequest.body = {
        values: [2, 3]
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(expect.any(ValidationError));
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
    
    it('should handle validation errors for invalid operation', async () => {
      mockRequest.body = {
        operation: 'invalid',
        values: [2, 3]
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(expect.any(ValidationError));
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
    
    it('should handle validation errors for missing values', async () => {
      mockRequest.body = {
        operation: 'add'
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(expect.any(ValidationError));
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
    
    it('should handle validation errors for missing expression in evaluate operation', async () => {
      mockRequest.body = {
        operation: 'evaluate'
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(expect.any(ValidationError));
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
    
    it('should allow expression for evaluate operation without values', async () => {
      mockRequest.body = {
        operation: 'evaluate',
        expression: '2 + 3'
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(CalculatorService.prototype.performCalculation).toHaveBeenCalledWith({
        operation: 'evaluate',
        expression: '2 + 3'
      });
      
      expect(mockResponse.json).toHaveBeenCalled();
    });
    
    it('should pass service errors to next middleware', async () => {
      mockRequest.body = {
        operation: 'divide',
        values: [5, 0]
      };
      
      await calculatorController.calculate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(expect.objectContaining({
        message: 'Division by zero is not allowed'
      }));
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
  });
  
  describe('getHistory', () => {
    it('should return calculation history', async () => {
      await calculatorController.getHistory(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(CalculatorService.prototype.getHistory).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({
            result: 5,
            operation: 'add'
          })
        ])
      }));
    });
    
    it('should pass service errors to next middleware', async () => {
      const error = new Error('History error');
      CalculatorService.prototype.getHistory = jest.fn().mockImplementation(() => {
        throw error;
      });
      
      await calculatorController.getHistory(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(error);
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
  });
  
  describe('clearHistory', () => {
    it('should clear calculation history', async () => {
      await calculatorController.clearHistory(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(CalculatorService.prototype.clearHistory).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.objectContaining({
          message: 'History cleared successfully'
        })
      }));
    });
    
    it('should pass service errors to next middleware', async () => {
      const error = new Error('Clear history error');
      CalculatorService.prototype.clearHistory = jest.fn().mockImplementation(() => {
        throw error;
      });
      
      await calculatorController.clearHistory(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(error);
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
  });
  
  describe('getStats', () => {
    it('should return operation statistics', async () => {
      await calculatorController.getStats(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(CalculatorService.prototype.getStats).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({
            operation: 'add',
            count: 2
          })
        ])
      }));
    });
    
    it('should pass service errors to next middleware', async () => {
      const error = new Error('Stats error');
      CalculatorService.prototype.getStats = jest.fn().mockImplementation(() => {
        throw error;
      });
      
      await calculatorController.getStats(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      
      expect(mockNext).toHaveBeenCalledWith(error);
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
  });
});