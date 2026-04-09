const { app } = require('@azure/functions');

/**
 * Demonstrate logging at all severity levels.
 */
app.http('logLevels', {
    methods: ['GET'],
    route: 'requests/log-levels',
    handler: async (request, context) => {
        context.log('Log levels endpoint requested');

        const levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

        context.trace('Debug level log message');
        context.log('Info level log message');
        context.warn('Warning level log message');
        context.error('Error level log message');

        return {
            status: 200,
            jsonBody: {
                message: 'Logged at all levels',
                levels,
            },
        };
    },
});
