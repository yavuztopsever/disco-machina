# Calculator Web Application

A modern web API for calculator operations built with Node.js, TypeScript, and Express.

## Features

- RESTful API for calculator operations
- Advanced arithmetic operations (addition, subtraction, multiplication, division)
- Power and square root functions
- Expression evaluation with security protections
- Memory operations for storing interim results
- Operation history tracking and statistics
- Comprehensive testing suite (unit, integration, end-to-end)
- TypeScript for type safety
- Error handling and validation

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm (v8 or higher)

### Installation

1. Clone the repository
2. Install dependencies:

```bash
cd web_app
npm install
```

3. Copy the environment file:

```bash
cp .env.example .env
```

4. Start the development server:

```bash
npm run dev
```

## API Endpoints

### Perform Calculation
- **POST** `/api/v1/calculator`
- Request body:
  ```json
  {
    "operation": "add|subtract|multiply|divide|power|sqrt|evaluate",
    "values": [number, number, ...],
    "expression": "string" // Required for "evaluate" operation
  }
  ```

### Get Calculation History
- **GET** `/api/v1/calculator/history`

### Clear Calculation History
- **DELETE** `/api/v1/calculator/history`

### Get Operation Statistics
- **GET** `/api/v1/calculator/stats`

### Health Check
- **GET** `/api/v1/health`

## Running Tests

### Unit Tests

```bash
npm test
```

### Test Coverage

```bash
npm run test:coverage
```

### Integration Tests

```bash
npm test -- --testPathPattern=integration
```

### End-to-End Tests

```bash
npm run test:e2e
```

To open the Cypress test runner:

```bash
npm run test:e2e:open
```

## Project Structure

```
web_app/
├── src/                # Source code
│   ├── api/            # API controllers and routes
│   ├── config/         # Configuration files
│   ├── middleware/     # Express middleware
│   ├── services/       # Business logic
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions and classes
│   └── index.ts        # Application entry point
├── tests/              # Test files
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests with Cypress
├── .env.example        # Example environment variables
├── .env.test           # Test environment variables
├── package.json        # Dependencies and scripts
└── tsconfig.json       # TypeScript configuration
```

## Built With

- Node.js - JavaScript runtime
- TypeScript - Type-safe JavaScript
- Express - Web framework
- Jest - Testing framework
- Supertest - HTTP testing
- Cypress - End-to-end testing
- Joi - Validation library
- Winston - Logging library

## License

This project is licensed under the MIT License