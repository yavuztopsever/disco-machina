/**
 * Application configuration
 */
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

interface Config {
  env: string;
  port: number;
  logLevel: string;
  apiPrefix: string;
  corsOrigins: string[];
  jwtSecret: string;
  jwtExpiresIn: string;
  rateLimit: {
    windowMs: number;
    max: number;
  };
  cache: {
    ttl: number;
    checkPeriod: number;
  };
}

// Default configuration values
const config: Config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  logLevel: process.env.LOG_LEVEL || 'info',
  apiPrefix: process.env.API_PREFIX || '/api/v1',
  corsOrigins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['http://localhost:3000'],
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10), // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10) // 100 requests per windowMs
  },
  cache: {
    ttl: parseInt(process.env.CACHE_TTL || '60', 10) * 1000, // 60 seconds
    checkPeriod: parseInt(process.env.CACHE_CHECK_PERIOD || '120', 10) * 1000 // 120 seconds
  }
};

// Validate required configuration variables
function validateConfig() {
  const requiredVars = ['jwtSecret'];
  
  for (const rv of requiredVars) {
    if (!process.env[rv.toUpperCase()] && config.env === 'production') {
      console.warn(`WARNING: Required environment variable ${rv.toUpperCase()} is not set`);
    }
  }
  
  if (config.env === 'production' && config.jwtSecret === 'your-secret-key') {
    console.error('ERROR: Using default JWT secret in production environment!');
    process.exit(1);
  }
}

// Only validate in server environments, not during testing
if (process.env.NODE_ENV !== 'test') {
  validateConfig();
}

export default config;