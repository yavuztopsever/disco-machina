// ***********************************************
// This file defines custom commands for Cypress
// ***********************************************

// Create a custom command to login if needed
Cypress.Commands.add('login', (username, password) => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/login',
    body: {
      username,
      password
    }
  }).then((response) => {
    localStorage.setItem('token', response.body.data.token)
  })
})

// Create a command to check if an element is visible in the viewport
Cypress.Commands.add('isInViewport', { prevSubject: true }, (subject) => {
  const bottom = Cypress.$(cy.state('window')).height()
  const rect = subject[0].getBoundingClientRect()
  
  expect(rect.top).to.be.lessThan(bottom)
  expect(rect.bottom).to.be.greaterThan(0)
  
  return subject
})

// Create a command to wait for API requests to complete
Cypress.Commands.add('waitForAPI', () => {
  cy.intercept('**').as('apiRequest')
  cy.wait('@apiRequest')
})

// Add a command to clear all API history
Cypress.Commands.add('clearCalculatorHistory', () => {
  cy.request('DELETE', '/api/v1/calculator/history')
})

// Add command to check for console errors
Cypress.Commands.add('noConsoleErrors', () => {
  cy.window().then((win) => {
    const errorLogs = []
    
    cy.stub(win.console, 'error').callsFake((msg) => {
      errorLogs.push(msg)
    })
    
    cy.wrap(errorLogs).should('be.empty')
  })
})

// Add command to verify API response
Cypress.Commands.add('verifyApiResponse', (response, expectedStatus = 200) => {
  expect(response.status).to.eq(expectedStatus)
  
  if (expectedStatus < 400) {
    expect(response.body).to.have.property('success', true)
    expect(response.body).to.have.property('data')
    expect(response.body).to.have.property('meta')
  } else {
    expect(response.body).to.have.property('success', false)
    expect(response.body).to.have.property('error')
  }
})

// Declare types for custom commands
// <reference types="cypress" />
// 
// declare namespace Cypress {
//   interface Chainable {
//     login(username: string, password: string): Chainable<Element>
//     isInViewport(): Chainable<Element>
//     waitForAPI(): Chainable<Element>
//     clearCalculatorHistory(): Chainable<Element>
//     noConsoleErrors(): Chainable<Element>
//     verifyApiResponse(response: any, expectedStatus?: number): Chainable<Element>
//   }
// }