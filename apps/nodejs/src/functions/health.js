const { app } = require('@azure/functions');

/**
 * Health check endpoint returning application status.
 */
app.http('health', {
    methods: ['GET'],
    route: 'health',
    handler: async (request, context) => {
        context.log('Health check requested');
        return {
            status: 200,
            jsonBody: {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                version: '1.0.0',
            },
        };
    },
});
