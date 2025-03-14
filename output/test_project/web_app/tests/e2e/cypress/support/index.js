// ***********************************************************
// This support file is loaded automatically before your tests
// You can add global configuration and behavior for all tests here
// ***********************************************************

// Import cypress commands
import './commands'

// Prevent uncaught exception from failing tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  return false
})

// Log test information to console for debugging
Cypress.on('test:after:run', (test, runnable) => {
  if (test.state === 'failed') {
    console.log('Test failed:', test.title)
    console.log('Error:', test.err.message)
  }
})

// Add a command to check accessibility with axe
// (Requires adding cypress-axe as a dependency)
// import 'cypress-axe'
// 
// Cypress.Commands.add('checkA11y', (context, options) => {
//   cy.checkA11y(context, options)
// })