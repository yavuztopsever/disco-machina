/**
 * End-to-end tests for calculator web application
 */
describe('Calculator Web App', () => {
  beforeEach(() => {
    // Visit the calculator web app frontend
    cy.visit('/');

    // Clear history before each test
    cy.request('DELETE', '/api/v1/calculator/history');
  });

  describe('Basic Calculator Operations', () => {
    it('should perform addition correctly', () => {
      // Enter first number
      cy.get('[data-testid="first-number"]').type('5');
      
      // Select operation
      cy.get('[data-testid="operation-select"]').select('add');
      
      // Enter second number
      cy.get('[data-testid="second-number"]').type('3');
      
      // Click calculate button
      cy.get('[data-testid="calculate-button"]').click();
      
      // Check result
      cy.get('[data-testid="result"]').should('contain', '8');
      
      // Check history
      cy.get('[data-testid="history-list"]').should('contain', 'Added 5 and 3');
    });

    it('should perform subtraction correctly', () => {
      cy.get('[data-testid="first-number"]').type('10');
      cy.get('[data-testid="operation-select"]').select('subtract');
      cy.get('[data-testid="second-number"]').type('4');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '6');
      cy.get('[data-testid="history-list"]').should('contain', 'Subtracted 4 from 10');
    });

    it('should perform multiplication correctly', () => {
      cy.get('[data-testid="first-number"]').type('6');
      cy.get('[data-testid="operation-select"]').select('multiply');
      cy.get('[data-testid="second-number"]').type('7');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '42');
      cy.get('[data-testid="history-list"]').should('contain', 'Multiplied 6 by 7');
    });

    it('should perform division correctly', () => {
      cy.get('[data-testid="first-number"]').type('20');
      cy.get('[data-testid="operation-select"]').select('divide');
      cy.get('[data-testid="second-number"]').type('5');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '4');
      cy.get('[data-testid="history-list"]').should('contain', 'Divided 20 by 5');
    });
  });

  describe('Advanced Operations', () => {
    it('should calculate power correctly', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      cy.get('[data-testid="base-number"]').type('2');
      cy.get('[data-testid="exponent-number"]').type('3');
      cy.get('[data-testid="power-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '8');
      cy.get('[data-testid="history-list"]').should('contain', '2 raised to the power of 3');
    });

    it('should calculate square root correctly', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      cy.get('[data-testid="sqrt-number"]').type('16');
      cy.get('[data-testid="sqrt-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '4');
      cy.get('[data-testid="history-list"]').should('contain', 'Square root of 16');
    });

    it('should evaluate expressions correctly', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      cy.get('[data-testid="expression-input"]').type('2 + 3 * 4');
      cy.get('[data-testid="evaluate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '14');
      cy.get('[data-testid="history-list"]').should('contain', 'Evaluated 2 + 3 * 4');
    });
  });

  describe('Memory Operations', () => {
    it('should store and recall values from memory', () => {
      // Perform a calculation first
      cy.get('[data-testid="first-number"]').type('5');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      // Store result in memory
      cy.get('[data-testid="memory-store"]').click();
      
      // Clear the inputs
      cy.get('[data-testid="clear-button"]').click();
      
      // Recall from memory
      cy.get('[data-testid="memory-recall"]').click();
      
      // Check that the value is recalled to the first number field
      cy.get('[data-testid="first-number"]').should('have.value', '8');
    });

    it('should add to memory', () => {
      // Store value in memory
      cy.get('[data-testid="first-number"]').type('5');
      cy.get('[data-testid="memory-store"]').click();
      
      // Add to memory
      cy.get('[data-testid="first-number"]').clear().type('3');
      cy.get('[data-testid="memory-add"]').click();
      
      // Clear the inputs
      cy.get('[data-testid="clear-button"]').click();
      
      // Recall from memory
      cy.get('[data-testid="memory-recall"]').click();
      
      // Check that the value is correctly updated
      cy.get('[data-testid="first-number"]').should('have.value', '8');
    });

    it('should subtract from memory', () => {
      // Store value in memory
      cy.get('[data-testid="first-number"]').type('10');
      cy.get('[data-testid="memory-store"]').click();
      
      // Subtract from memory
      cy.get('[data-testid="first-number"]').clear().type('4');
      cy.get('[data-testid="memory-subtract"]').click();
      
      // Clear the inputs
      cy.get('[data-testid="clear-button"]').click();
      
      // Recall from memory
      cy.get('[data-testid="memory-recall"]').click();
      
      // Check that the value is correctly updated
      cy.get('[data-testid="first-number"]').should('have.value', '6');
    });

    it('should clear memory', () => {
      // Store value in memory
      cy.get('[data-testid="first-number"]').type('5');
      cy.get('[data-testid="memory-store"]').click();
      
      // Clear memory
      cy.get('[data-testid="memory-clear"]').click();
      
      // Clear the inputs
      cy.get('[data-testid="clear-button"]').click();
      
      // Recall from memory (should recall 0)
      cy.get('[data-testid="memory-recall"]').click();
      
      // Check that the memory was cleared
      cy.get('[data-testid="first-number"]').should('have.value', '0');
    });
  });

  describe('History', () => {
    it('should display calculation history', () => {
      // Perform several calculations
      cy.get('[data-testid="first-number"]').type('2');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="first-number"]').clear().type('4');
      cy.get('[data-testid="operation-select"]').select('multiply');
      cy.get('[data-testid="second-number"]').clear().type('5');
      cy.get('[data-testid="calculate-button"]').click();
      
      // Check history
      cy.get('[data-testid="history-tab"]').click();
      cy.get('[data-testid="history-list"]').children().should('have.length', 2);
      cy.get('[data-testid="history-list"]').should('contain', 'Added 2 and 3');
      cy.get('[data-testid="history-list"]').should('contain', 'Multiplied 4 by 5');
    });

    it('should clear history', () => {
      // Perform a calculation
      cy.get('[data-testid="first-number"]').type('2');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      // Go to history tab
      cy.get('[data-testid="history-tab"]').click();
      
      // Verify history exists
      cy.get('[data-testid="history-list"]').children().should('have.length', 1);
      
      // Clear history
      cy.get('[data-testid="clear-history-button"]').click();
      
      // Verify history is cleared
      cy.get('[data-testid="history-list"]').children().should('have.length', 0);
    });

    it('should reuse values from history', () => {
      // Perform a calculation
      cy.get('[data-testid="first-number"]').type('2');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      // Go to history tab
      cy.get('[data-testid="history-tab"]').click();
      
      // Click on the "Use result" button for the history item
      cy.get('[data-testid="use-result-button"]').first().click();
      
      // Go back to calculator tab
      cy.get('[data-testid="basic-tab"]').click();
      
      // Verify the result is inserted in the first number field
      cy.get('[data-testid="first-number"]').should('have.value', '5');
    });
  });

  describe('Error Handling', () => {
    it('should display an error for division by zero', () => {
      cy.get('[data-testid="first-number"]').type('10');
      cy.get('[data-testid="operation-select"]').select('divide');
      cy.get('[data-testid="second-number"]').type('0');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'Division by zero is not allowed');
    });

    it('should display an error for negative square root', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      cy.get('[data-testid="sqrt-number"]').type('-4');
      cy.get('[data-testid="sqrt-button"]').click();
      
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'Cannot calculate square root of a negative number');
    });

    it('should display an error for invalid expression', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      cy.get('[data-testid="expression-input"]').type('2 + + 3');
      cy.get('[data-testid="evaluate-button"]').click();
      
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'Failed to evaluate expression');
    });

    it('should require number inputs', () => {
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="first-number-error"]').should('be.visible');
      cy.get('[data-testid="second-number-error"]').should('be.visible');
    });
  });

  describe('Responsive UI', () => {
    it('should adapt to mobile viewport', () => {
      // Test mobile view
      cy.viewport('iphone-x');
      
      // Check that the layout has changed
      cy.get('[data-testid="mobile-layout"]').should('be.visible');
      cy.get('[data-testid="desktop-layout"]').should('not.be.visible');
      
      // Verify that the calculator is still usable
      cy.get('[data-testid="first-number"]').type('5');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '8');
    });

    it('should adapt to tablet viewport', () => {
      // Test tablet view
      cy.viewport('ipad-2');
      
      // Check that the layout has changed
      cy.get('[data-testid="tablet-layout"]').should('be.visible');
      
      // Verify that the calculator is still usable
      cy.get('[data-testid="first-number"]').type('5');
      cy.get('[data-testid="operation-select"]').select('add');
      cy.get('[data-testid="second-number"]').type('3');
      cy.get('[data-testid="calculate-button"]').click();
      
      cy.get('[data-testid="result"]').should('contain', '8');
    });
  });

  describe('Accessibility', () => {
    it('should navigate with keyboard', () => {
      // Focus on first input
      cy.get('[data-testid="first-number"]').focus();
      
      // Type value
      cy.focused().type('5');
      
      // Tab to operation select
      cy.focused().tab();
      
      // Select operation with keyboard (down arrow to select "add")
      cy.focused().type('{downarrow}{enter}');
      
      // Tab to second input
      cy.focused().tab();
      
      // Type value
      cy.focused().type('3');
      
      // Tab to calculate button
      cy.focused().tab();
      
      // Press enter to calculate
      cy.focused().type('{enter}');
      
      // Check result
      cy.get('[data-testid="result"]').should('contain', '8');
    });

    it('should have proper ARIA attributes', () => {
      // Check that inputs have proper labels
      cy.get('[data-testid="first-number"]').should('have.attr', 'aria-labelledby');
      cy.get('[data-testid="operation-select"]').should('have.attr', 'aria-labelledby');
      cy.get('[data-testid="second-number"]').should('have.attr', 'aria-labelledby');
      
      // Check that result has aria-live attribute
      cy.get('[data-testid="result"]').should('have.attr', 'aria-live', 'polite');
      
      // Check that error message has appropriate role and aria-live
      cy.get('[data-testid="error-message"]').should('have.attr', 'role', 'alert');
      cy.get('[data-testid="error-message"]').should('have.attr', 'aria-live', 'assertive');
    });
  });

  describe('Performance', () => {
    it('should load quickly', () => {
      // Measure time to interactive
      cy.window().then((win) => {
        const perfData = win.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        
        // Page should load in less than 3 seconds
        expect(pageLoadTime).to.be.lessThan(3000);
      });
    });

    it('should handle rapid calculations', () => {
      // Perform 10 calculations in rapid succession
      for (let i = 0; i < 10; i++) {
        cy.get('[data-testid="first-number"]').clear().type(`${i}`);
        cy.get('[data-testid="operation-select"]').select('add');
        cy.get('[data-testid="second-number"]').clear().type(`${i}`);
        cy.get('[data-testid="calculate-button"]').click();
      }
      
      // Check that all calculations are in history
      cy.get('[data-testid="history-tab"]').click();
      cy.get('[data-testid="history-list"]').children().should('have.length', 10);
    });
  });

  describe('Security', () => {
    it('should sanitize user input to prevent XSS', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      // Try to inject script via expression
      cy.get('[data-testid="expression-input"]').type('<script>alert("XSS")</script>');
      cy.get('[data-testid="evaluate-button"]').click();
      
      // Should show an error and not execute the script
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'invalid characters');
      
      // Check that the script was not inserted into the DOM
      cy.get('script').should('not.contain', 'alert("XSS")');
    });

    it('should reject attempts to use eval with malicious code', () => {
      cy.get('[data-testid="advanced-tab"]').click();
      
      // Try to pass malicious code to evaluateExpression
      cy.get('[data-testid="expression-input"]').type('console.log(document.cookie)');
      cy.get('[data-testid="evaluate-button"]').click();
      
      // Should show an error
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'invalid characters');
    });
  });
});