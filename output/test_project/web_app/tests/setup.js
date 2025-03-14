/**
 * Jest setup file for test configuration
 */

// Set timeout to 10 seconds for all tests
jest.setTimeout(10000);

// Set environment variables for testing
process.env.NODE_ENV = 'test';
process.env.PORT = '3001';
process.env.LOG_LEVEL = 'error';
process.env.JWT_SECRET = 'test-jwt-secret';

// Mock console methods to keep test output clean
// Comment these out if you need to debug tests
global.console = {
  ...console,
  log: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};

// Keep error and warn for debugging
// global.console.error = jest.fn();
// global.console.warn = jest.fn();