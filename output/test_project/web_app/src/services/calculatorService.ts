/**
 * Service for handling calculator operations
 */
import { Calculator, CalculationResult } from '../utils/calculator';
import { CalculationRequest, CalculationStat, ApiResponse } from '../types';
import { ApplicationError } from '../middleware/errorHandler';

export class CalculatorService {
  private calculator: Calculator;
  private operationStats: Record<string, { count: number; operands: number[][]; }>;
  
  constructor() {
    this.calculator = new Calculator();
    this.operationStats = {};
  }
  
  /**
   * Process a calculation request and track statistics
   * @param request The calculation request
   * @returns The calculation result
   */
  public performCalculation(request: CalculationRequest): CalculationResult {
    let result: CalculationResult;
    
    try {
      switch (request.operation) {
        case 'add':
          result = this.calculator.add(...request.values);
          break;
        case 'subtract':
          if (request.values.length !== 2) {
            throw new ApplicationError('Subtraction requires exactly 2 values', 400);
          }
          result = this.calculator.subtract(request.values[0], request.values[1]);
          break;
        case 'multiply':
          result = this.calculator.multiply(...request.values);
          break;
        case 'divide':
          if (request.values.length !== 2) {
            throw new ApplicationError('Division requires exactly 2 values', 400);
          }
          result = this.calculator.divide(request.values[0], request.values[1]);
          break;
        case 'power':
          if (request.values.length !== 2) {
            throw new ApplicationError('Power operation requires exactly 2 values', 400);
          }
          result = this.calculator.power(request.values[0], request.values[1]);
          break;
        case 'sqrt':
          if (request.values.length !== 1) {
            throw new ApplicationError('Square root operation requires exactly 1 value', 400);
          }
          result = this.calculator.sqrt(request.values[0]);
          break;
        case 'evaluate':
          if (!request.expression) {
            throw new ApplicationError('Expression is required for evaluation', 400);
          }
          result = this.calculator.evaluateExpression(request.expression);
          break;
        default:
          throw new ApplicationError(`Unsupported operation: ${request.operation}`, 400);
      }
      
      // Track statistics
      this.trackOperationStat(request);
      
      return result;
    } catch (error) {
      if (error instanceof ApplicationError) {
        throw error;
      }
      throw new ApplicationError(
        error instanceof Error ? error.message : 'Calculation failed',
        400
      );
    }
  }
  
  /**
   * Track operation statistics
   * @param request The calculation request
   */
  private trackOperationStat(request: CalculationRequest): void {
    const operation = request.operation;
    
    if (!this.operationStats[operation]) {
      this.operationStats[operation] = {
        count: 0,
        operands: []
      };
    }
    
    this.operationStats[operation].count += 1;
    this.operationStats[operation].operands.push(request.values);
  }
  
  /**
   * Get calculation history
   * @returns Array of past calculations
   */
  public getHistory(): CalculationResult[] {
    return this.calculator.getHistory();
  }
  
  /**
   * Clear calculation history
   */
  public clearHistory(): void {
    this.calculator.clearHistory();
  }
  
  /**
   * Get operation statistics
   * @returns Statistics for each operation
   */
  public getStats(): CalculationStat[] {
    const stats: CalculationStat[] = [];
    
    for (const [operation, data] of Object.entries(this.operationStats)) {
      // Calculate average operand count
      const totalOperandCount = data.operands.reduce((sum, operands) => sum + operands.length, 0);
      const averageOperandCount = data.count > 0 ? totalOperandCount / data.count : 0;
      
      // Find most frequent input (if any)
      let mostFrequentInput: number | undefined = undefined;
      
      if (data.operands.length > 0) {
        // Flatten all operands
        const allOperands = data.operands.flat();
        
        // Count occurrences of each operand
        const operandCounts = allOperands.reduce((counts, operand) => {
          counts[operand] = (counts[operand] || 0) + 1;
          return counts;
        }, {} as Record<number, number>);
        
        // Find the most frequent
        let maxCount = 0;
        for (const [operand, count] of Object.entries(operandCounts)) {
          if (count > maxCount) {
            maxCount = count;
            mostFrequentInput = parseFloat(operand);
          }
        }
      }
      
      stats.push({
        operation,
        count: data.count,
        averageOperandCount,
        mostFrequentInput
      });
    }
    
    return stats;
  }
  
  /**
   * Create a formatted API response
   * @param data The data to include in the response
   * @returns A formatted API response
   */
  public createResponse<T>(data: T): ApiResponse<T> {
    return {
      success: true,
      data,
      meta: {
        timestamp: new Date(),
        requestId: Math.random().toString(36).substring(2, 15)
      }
    };
  }
}