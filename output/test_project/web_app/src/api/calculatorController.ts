/**
 * Controller for calculator API endpoints
 */
import { Request, Response, NextFunction } from 'express';
import { CalculatorService } from '../services/calculatorService';
import { ValidationError } from '../middleware/errorHandler';
import { CalculationRequest } from '../types';
import Joi from 'joi';

export class CalculatorController {
  private calculatorService: CalculatorService;
  
  constructor() {
    this.calculatorService = new CalculatorService();
  }
  
  /**
   * Perform a calculation
   */
  public calculate = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const validationSchema = Joi.object({
        operation: Joi.string().valid('add', 'subtract', 'multiply', 'divide', 'power', 'sqrt', 'evaluate').required(),
        values: Joi.array().items(Joi.number()).when('operation', {
          is: 'evaluate',
          then: Joi.optional(),
          otherwise: Joi.required()
        }),
        expression: Joi.string().when('operation', {
          is: 'evaluate',
          then: Joi.required(),
          otherwise: Joi.optional()
        })
      });
      
      const { error, value } = validationSchema.validate(req.body);
      
      if (error) {
        const errors: Record<string, string[]> = {};
        error.details.forEach(detail => {
          const key = detail.path[0] as string;
          errors[key] = errors[key] || [];
          errors[key].push(detail.message);
        });
        
        throw new ValidationError('Invalid calculation request', errors);
      }
      
      const request = value as CalculationRequest;
      const result = this.calculatorService.performCalculation(request);
      
      res.json(this.calculatorService.createResponse(result));
    } catch (error) {
      next(error);
    }
  };
  
  /**
   * Get calculation history
   */
  public getHistory = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const history = this.calculatorService.getHistory();
      res.json(this.calculatorService.createResponse(history));
    } catch (error) {
      next(error);
    }
  };
  
  /**
   * Clear calculation history
   */
  public clearHistory = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      this.calculatorService.clearHistory();
      res.json(this.calculatorService.createResponse({ message: 'History cleared successfully' }));
    } catch (error) {
      next(error);
    }
  };
  
  /**
   * Get operation statistics
   */
  public getStats = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const stats = this.calculatorService.getStats();
      res.json(this.calculatorService.createResponse(stats));
    } catch (error) {
      next(error);
    }
  };
}