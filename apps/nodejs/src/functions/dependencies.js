const { app } = require('@azure/functions');

/**
 * Call an external HTTP service and return timing information.
 */
const EXTERNAL_URL = 'https://httpbin.org/get';

app.http('externalDependency', {
    methods: ['GET'],
    route: 'dependencies/external',
    handler: async (request, context) => {
        context.log(`External dependency endpoint requested (url=${EXTERNAL_URL})`);

        const startTime = Date.now();
        try {
            const response = await fetch(EXTERNAL_URL, { signal: AbortSignal.timeout(10000) });
            const elapsedMs = Date.now() - startTime;

            context.log(`External call completed (status=${response.status}, time=${elapsedMs}ms)`);

            return {
                status: 200,
                jsonBody: {
                    status: 'success',
                    statusCode: response.status,
                    responseTime: `${elapsedMs}ms`,
                    url: EXTERNAL_URL,
                },
            };
        } catch (err) {
            const elapsedMs = Date.now() - startTime;
            context.error(`External call failed (error=${err.message}, time=${elapsedMs}ms)`);

            return {
                status: 502,
                jsonBody: {
                    status: 'error',
                    statusCode: 0,
                    responseTime: `${elapsedMs}ms`,
                    url: EXTERNAL_URL,
                    error: err.message,
                },
            };
        }
    },
});
