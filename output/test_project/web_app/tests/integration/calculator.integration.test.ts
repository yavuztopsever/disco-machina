/**
 * Integration tests for Calculator API
 */
import request from 'supertest';
import app from '../../src/index';

describe('Calculator API Integration Tests', () => {
  describe('POST /api/v1/calculator', () => {
    it('should add two numbers correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'add',
          values: [2, 3]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(5);
      expect(response.body.data.operation).toBe('add');
      expect(response.body.data.operands).toEqual([2, 3]);
    });

    it('should subtract numbers correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'subtract',
          values: [5, 3]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(2);
    });

    it('should multiply numbers correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'multiply',
          values: [2, 3, 4]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(24);
    });

    it('should divide numbers correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'divide',
          values: [6, 3]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(2);
    });

    it('should calculate power correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'power',
          values: [2, 3]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(8);
    });

    it('should calculate square root correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'sqrt',
          values: [9]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(3);
    });

    it('should evaluate expression correctly', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'evaluate',
          expression: '2 + 3 * 4'
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.result).toBe(14);
    });

    it('should return 400 for invalid operation', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'invalid',
          values: [2, 3]
        });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBeDefined();
    });

    it('should return 400 when division by zero is attempted', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'divide',
          values: [5, 0]
        });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('Division by zero');
    });

    it('should return 400 when square root of negative number is attempted', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'sqrt',
          values: [-4]
        });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('negative number');
    });

    it('should return 400 for invalid request structure', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .send({
          // Missing operation field
          values: [2, 3]
        });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error.errors).toBeDefined();
    });
  });

  describe('GET /api/v1/calculator/history', () => {
    it('should return calculation history', async () => {
      // First perform a couple of calculations
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'add',
          values: [2, 3]
        });
      
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'multiply',
          values: [4, 5]
        });
      
      // Then check the history
      const response = await request(app)
        .get('/api/v1/calculator/history');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.data.length).toBeGreaterThanOrEqual(2);
      
      // The most recent calculations should be in the history
      const operations = response.body.data.map((item: any) => item.operation);
      expect(operations).toContain('add');
      expect(operations).toContain('multiply');
    });
  });

  describe('DELETE /api/v1/calculator/history', () => {
    it('should clear calculation history', async () => {
      // First perform a calculation
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'add',
          values: [2, 3]
        });
      
      // Then clear the history
      const clearResponse = await request(app)
        .delete('/api/v1/calculator/history');
      
      expect(clearResponse.status).toBe(200);
      expect(clearResponse.body.success).toBe(true);
      
      // Verify history is cleared
      const historyResponse = await request(app)
        .get('/api/v1/calculator/history');
      
      expect(historyResponse.status).toBe(200);
      expect(historyResponse.body.success).toBe(true);
      expect(historyResponse.body.data.length).toBe(0);
    });
  });

  describe('GET /api/v1/calculator/stats', () => {
    it('should return operation statistics', async () => {
      // Clear history first to start with a clean slate
      await request(app)
        .delete('/api/v1/calculator/history');
      
      // Perform a few calculations
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'add',
          values: [2, 3]
        });
      
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'add',
          values: [5, 10]
        });
      
      await request(app)
        .post('/api/v1/calculator')
        .send({
          operation: 'multiply',
          values: [4, 5]
        });
      
      // Get the stats
      const response = await request(app)
        .get('/api/v1/calculator/stats');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      
      // Check the stats for the add operation
      const addStats = response.body.data.find((stat: any) => stat.operation === 'add');
      expect(addStats).toBeDefined();
      expect(addStats.count).toBe(2);
      expect(addStats.averageOperandCount).toBe(2);
      
      // Check the stats for the multiply operation
      const multiplyStats = response.body.data.find((stat: any) => stat.operation === 'multiply');
      expect(multiplyStats).toBeDefined();
      expect(multiplyStats.count).toBe(1);
    });
  });

  describe('GET /api/v1/health', () => {
    it('should return 200 OK with health information', async () => {
      const response = await request(app)
        .get('/api/v1/health');
      
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('UP');
      expect(response.body.timestamp).toBeDefined();
      expect(response.body.uptime).toBeDefined();
    });
  });

  describe('Error handling', () => {
    it('should return 404 for non-existent routes', async () => {
      const response = await request(app)
        .get('/api/v1/non-existent');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(response.body.error.status).toBe(404);
      expect(response.body.error.message).toContain('not found');
    });
    
    it('should handle malformed JSON', async () => {
      const response = await request(app)
        .post('/api/v1/calculator')
        .set('Content-Type', 'application/json')
        .send('{malformed json');
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });
});