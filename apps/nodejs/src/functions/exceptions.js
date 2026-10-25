const { registerLabHttp } = require('../shared/labLimits');

/**
 * Raise and catch an error to demonstrate exception handling.
 */
registerLabHttp('testError', {
    methods: ['GET'],
    route: 'exceptions/test-error',
    handler: async (request, context) => {
        context.log('Exception test endpoint requested');

        try {
            throw new Error('Simulated error for testing');
        } catch (err) {
            context.error(`Caught simulated error: ${err.message}`);

            return {
                status: 200,
                jsonBody: {
                    error: 'Handled exception',
                    type: err.constructor.name,
                    message: err.message,
                },
            };
        }
    },
});

/**
 * Raise an unhandled exception to generate real 500 errors in Application Insights.
 */
registerLabHttp('unhandledError', {
    methods: ['GET'],
    route: 'exceptions/unhandled',
    handler: async (request, context) => {
        context.log('Unhandled exception endpoint requested');
        throw new Error('Deliberate unhandled error for KQL data collection');
    },
});
