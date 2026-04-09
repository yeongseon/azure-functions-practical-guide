const { app } = require('@azure/functions');

/**
 * Runs every 5 minutes to perform scheduled maintenance tasks.
 *
 * Common use cases:
 * - Clean up expired cache entries
 * - Generate periodic reports
 * - Ping downstream health endpoints
 *
 * Set runOnStartup to true temporarily for local testing, but always
 * revert to false before deploying to production on the Consumption plan.
 */
app.timer('scheduledCleanup', {
    schedule: '0 */5 * * * *',
    runOnStartup: false,
    handler: async (timer, context) => {
        const utcTimestamp = new Date().toISOString();

        if (timer.isPastDue) {
            context.warn(`Timer trigger is past due: ${utcTimestamp}`);
        }

        context.log(`Scheduled cleanup fired at ${utcTimestamp}`);
    },
});
