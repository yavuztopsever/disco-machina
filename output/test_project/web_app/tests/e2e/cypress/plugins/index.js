/// <reference types="cypress" />
// ***********************************************************
// This plugins file is loaded automatically before Cypress runs
// This is where you can register custom tasks or plugins
// ***********************************************************

/**
 * @type {Cypress.PluginConfig}
 */
module.exports = (on, config) => {
  // Task to execute shell commands
  on('task', {
    log(message) {
      console.log(message)
      return null
    },
    
    // For executing database operations if needed
    // execSQL(query) {
    //   // Execute a database query (would require DB modules)
    //   return { rows: [] }
    // },
    
    // Return system info for debugging
    getSystemInfo() {
      return {
        platform: process.platform,
        arch: process.arch,
        version: process.version,
        env: process.env.NODE_ENV
      }
    }
  })

  // Environment variable overrides
  config.env = {
    ...config.env,
    apiUrl: 'http://localhost:3001/api/v1'
  }

  // Dynamically set baseUrl based on environment
  if (process.env.CYPRESS_baseUrl) {
    config.baseUrl = process.env.CYPRESS_baseUrl
  }

  return config
}