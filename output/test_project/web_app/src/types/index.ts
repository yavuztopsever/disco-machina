/**
 * Type definitions for the calculator web application
 */

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'user' | 'admin';
  createdAt: Date;
}

export interface CalculationRequest {
  operation: 'add' | 'subtract' | 'multiply' | 'divide' | 'power' | 'sqrt' | 'evaluate';
  values: number[];
  expression?: string;
}

export interface ErrorResponse {
  status: number;
  message: string;
  timestamp: Date;
  path?: string;
  errors?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ErrorResponse;
  meta?: {
    timestamp: Date;
    requestId: string;
  };
}

export interface CalculationStat {
  operation: string;
  count: number;
  averageOperandCount: number;
  mostFrequentInput?: number;
}

export interface UserSession {
  userId: string;
  username: string;
  role: string;
  expiresAt: Date;
}

export interface CacheOptions {
  ttl?: number; // time to live in seconds
  refresh?: boolean; // whether to refresh the TTL on access
}

export interface LogMessage {
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  timestamp: Date;
  context?: Record<string, unknown>;
}

export interface RequestContext {
  requestId: string;
  user?: UserSession;
  startTime: Date;
}