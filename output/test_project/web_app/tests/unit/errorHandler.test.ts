/**
 * Unit tests for error handler middleware
 */
import { NextFunction, Request, Response } from 'express';
import { 
  errorHandler, 
  ApplicationError, 
  ValidationError, 
  NotFoundError, 
  UnauthorizedError, 
  ForbiddenError 
} from '../../src/middleware/errorHandler';

describe('Error Handler Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;
  
  beforeEach(() => {
    mockRequest = {
      path: '/test-path',
      headers: {
        'x-request-id': 'test-request-id'
      }
    };
    
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    
    nextFunction = jest.fn();
  });
  
  it('should handle ApplicationError correctly', () => {
    const error = new ApplicationError('Test error message', 400);
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 400,
        message: 'Test error message',
        path: '/test-path'
      })
    }));
  });
  
  it('should handle ValidationError correctly', () => {
    const errors = { field1: ['Error 1'], field2: ['Error 2'] };
    const error = new ValidationError('Validation failed', errors);
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 400,
        message: 'Validation failed',
        errors
      })
    }));
  });
  
  it('should handle NotFoundError correctly', () => {
    const error = new NotFoundError('Resource');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(404);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 404,
        message: 'Resource not found'
      })
    }));
  });
  
  it('should handle UnauthorizedError correctly', () => {
    const error = new UnauthorizedError();
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 401,
        message: 'Unauthorized'
      })
    }));
  });
  
  it('should handle ForbiddenError correctly', () => {
    const error = new ForbiddenError('Custom forbidden message');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 403,
        message: 'Custom forbidden message'
      })
    }));
  });
  
  it('should handle generic Error as 500 Internal Server Error', () => {
    const error = new Error('Generic error');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(500);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 500,
        message: 'Generic error'
      })
    }));
  });
  
  it('should mask internal server errors in production', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';
    
    const error = new Error('Sensitive error message');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.status).toHaveBeenCalledWith(500);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: expect.objectContaining({
        status: 500,
        message: 'Internal Server Error'
      })
    }));
    
    // Restore environment
    process.env.NODE_ENV = originalEnv;
  });
  
  it('should include request ID in response meta', () => {
    const error = new Error('Test error');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      meta: expect.objectContaining({
        requestId: 'test-request-id'
      })
    }));
  });
  
  it('should use "unknown" as request ID if not provided', () => {
    mockRequest.headers = {};
    const error = new Error('Test error');
    
    errorHandler(error, mockRequest as Request, mockResponse as Response, nextFunction);
    
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      meta: expect.objectContaining({
        requestId: 'unknown'
      })
    }));
  });
});