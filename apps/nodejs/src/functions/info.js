const { app } = require('@azure/functions');
const { settings } = require('../shared/config');

/**
 * Application info endpoint returning runtime and configuration details.
 */
app.http('info', {
    methods: ['GET'],
    route: 'info',
    handler: async (request, context) => {
        context.log('Info endpoint requested');
        return {
            status: 200,
            jsonBody: {
                name: 'azure-functions-nodejs-guide',
                version: '1.0.0',
                node: process.version,
                environment: settings.environment,
                telemetryMode: settings.telemetryMode,
                functionApp: settings.functionAppName,
                invocationId: context.invocationId || 'local',
            },
        };
    },
});
