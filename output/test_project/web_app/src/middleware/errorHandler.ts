/**
 * Global error handling middleware for Express
 */
import { Request, Response, NextFunction } from 'express';
import { ApiResponse, ErrorResponse } from '../types';

export class ApplicationError extends Error {
  status: number;
  errors?: Record<string, string[]>;
  
  constructor(message: string, status = 500, errors?: Record<string, string[]>) {
    super(message);
    this.name = this.constructor.name;
    this.status = status;
    this.errors = errors;
    
    // Capturing stack trace, excluding constructor call from it
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends ApplicationError {
  constructor(message: string, errors: Record<string, string[]>) {
    super(message, 400, errors);
  }
}

export class NotFoundError extends ApplicationError {
  constructor(resource: string) {
    super(`${resource} not found`, 404);
  }
}

export class UnauthorizedError extends ApplicationError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

export class ForbiddenError extends ApplicationError {
  constructor(message = 'Forbidden') {
    super(message, 403);
  }
}

export function errorHandler(
  err: Error | ApplicationError,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  next: NextFunction
): void {
  console.error(err);
  
  const status = err instanceof ApplicationError ? err.status : 500;
  const errorResponse: ErrorResponse = {
    status,
    message: err.message || 'Something went wrong',
    timestamp: new Date(),
    path: req.path
  };
  
  if (err instanceof ApplicationError && err.errors) {
    errorResponse.errors = err.errors;
  }
  
  // In production, don't expose internal server errors
  if (status === 500 && process.env.NODE_ENV === 'production') {
    errorResponse.message = 'Internal Server Error';
  }
  
  const response: ApiResponse<null> = {
    success: false,
    error: errorResponse,
    meta: {
      timestamp: new Date(),
      requestId: req.headers['x-request-id'] as string || 'unknown'
    }
  };
  
  res.status(status).json(response);
}