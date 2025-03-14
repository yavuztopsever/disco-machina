/**
 * API route definitions
 */
import { Router } from 'express';
import { CalculatorController } from './calculatorController';

const router = Router();
const calculatorController = new CalculatorController();

// Calculator routes
router.post('/calculator', calculatorController.calculate);
router.get('/calculator/history', calculatorController.getHistory);
router.delete('/calculator/history', calculatorController.clearHistory);
router.get('/calculator/stats', calculatorController.getStats);

// Health check route
router.get('/health', (req, res) => {
  res.json({
    status: 'UP',
    timestamp: new Date(),
    version: process.env.npm_package_version || '1.0.0',
    uptime: process.uptime()
  });
});

export default router;