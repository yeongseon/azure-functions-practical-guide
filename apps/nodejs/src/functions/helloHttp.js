const { app } = require('@azure/functions');

/**
 * Hello HTTP handler — primary endpoint used across all tutorials.
 * Route: /api/hello/{name?}
 */
app.http('helloHttp', {
    methods: ['GET'],
    route: 'hello/{name?}',
    handler: async (request, context) => {
        const name = request.params.name || request.query.get('name') || 'world';
        context.log(`Handled hello for ${name}`);
        return {
            status: 200,
            jsonBody: { message: `Hello, ${name}` },
        };
    },
});
