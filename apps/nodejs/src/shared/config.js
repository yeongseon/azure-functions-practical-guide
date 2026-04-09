/**
 * Application settings loaded from environment variables.
 */
const settings = {
    appName: process.env.APP_NAME || 'azure-functions-nodejs-guide',
    environment: process.env.AZURE_FUNCTIONS_ENVIRONMENT || 'production',
    telemetryMode: process.env.TELEMETRY_MODE || 'basic',
    functionAppName: process.env.WEBSITE_SITE_NAME || 'local',
    logLevel: process.env.LOG_LEVEL || 'info',
};

module.exports = { settings };
