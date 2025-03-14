/**
 * Unit tests for configuration module
 */
import config from '../../src/config';

describe('Configuration', () => {
  const originalEnv = process.env;
  
  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });
  
  afterAll(() => {
    process.env = originalEnv;
  });
  
  it('should load default configuration values', () => {
    // Clear environment variables that might affect the test
    delete process.env.PORT;
    delete process.env.NODE_ENV;
    delete process.env.LOG_LEVEL;
    
    // Re-import config to get fresh values
    jest.resetModules();
    const freshConfig = require('../../src/config').default;
    
    // Check default values
    expect(freshConfig.port).toBe(3000);
    expect(freshConfig.env).toBe('development');
    expect(freshConfig.logLevel).toBe('info');
    expect(freshConfig.apiPrefix).toBe('/api/v1');
    expect(freshConfig.jwtExpiresIn).toBe('1d');
  });
  
  it('should override defaults with environment variables', () => {
    // Set environment variables
    process.env.PORT = '4000';
    process.env.NODE_ENV = 'production';
    process.env.LOG_LEVEL = 'error';
    process.env.API_PREFIX = '/api/v2';
    process.env.JWT_EXPIRES_IN = '2h';
    process.env.CORS_ORIGINS = 'https://example.com,https://test.com';
    
    // Re-import config to get fresh values
    jest.resetModules();
    const freshConfig = require('../../src/config').default;
    
    // Check that environment variables override defaults
    expect(freshConfig.port).toBe(4000);
    expect(freshConfig.env).toBe('production');
    expect(freshConfig.logLevel).toBe('error');
    expect(freshConfig.apiPrefix).toBe('/api/v2');
    expect(freshConfig.jwtExpiresIn).toBe('2h');
    expect(freshConfig.corsOrigins).toEqual(['https://example.com', 'https://test.com']);
  });
  
  it('should parse numeric environment variables correctly', () => {
    // Set environment variables
    process.env.PORT = '5000';
    process.env.RATE_LIMIT_WINDOW_MS = '60000';
    process.env.RATE_LIMIT_MAX = '50';
    process.env.CACHE_TTL = '30';
    process.env.CACHE_CHECK_PERIOD = '60';
    
    // Re-import config to get fresh values
    jest.resetModules();
    const freshConfig = require('../../src/config').default;
    
    // Check that numeric values are parsed correctly
    expect(freshConfig.port).toBe(5000);
    expect(freshConfig.rateLimit.windowMs).toBe(60000);
    expect(freshConfig.rateLimit.max).toBe(50);
    expect(freshConfig.cache.ttl).toBe(30000); // Converted to milliseconds
    expect(freshConfig.cache.checkPeriod).toBe(60000); // Converted to milliseconds
  });
  
  it('should have proper default CORS origins', () => {
    delete process.env.CORS_ORIGINS;
    
    // Re-import config to get fresh values
    jest.resetModules();
    const freshConfig = require('../../src/config').default;
    
    expect(Array.isArray(freshConfig.corsOrigins)).toBe(true);
    expect(freshConfig.corsOrigins).toContain('http://localhost:3000');
  });
  
  describe('in test environment', () => {
    it('should not validate config when NODE_ENV is test', () => {
      process.env.NODE_ENV = 'test';
      
      // This should not throw an error even with default JWT secret
      jest.resetModules();
      require('../../src/config').default;
      
      // No assertions needed - if it doesn't throw, the test passes
    });
  });
  
  // Note: We can't easily test the process.exit() case without mocking process.exit
  // which is challenging and not recommended. In a real environment, you might use
  // a custom exit handler that you can mock instead of directly calling process.exit().
});