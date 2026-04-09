const { app } = require('@azure/functions');

/**
 * Process queue messages with configurable delay for backlog lab.
 *
 * Logs enqueue age, dequeue count, processing duration, and instance ID
 * for KQL evidence collection.
 *
 * Set PROCESSING_DELAY_MS environment variable to inject artificial delay.
 */
app.storageQueue('queueProcessor', {
    queueName: 'work-items',
    connection: 'QueueStorage',
    handler: async (queueItem, context) => {
        const receiveUtc = new Date();
        const instanceId = (process.env.WEBSITE_INSTANCE_ID || 'unknown').substring(0, 8);

        // Parse message
        let body = {};
        let enqueuedUtcStr = '';
        let sequence = -1;
        try {
            body = typeof queueItem === 'string' ? JSON.parse(queueItem) : queueItem;
            enqueuedUtcStr = body.enqueuedUtc || '';
            sequence = body.sequence ?? -1;
        } catch {
            // Non-JSON message
        }

        // Compute message age
        let ageMs = -1;
        if (enqueuedUtcStr) {
            try {
                const enqueuedUtc = new Date(enqueuedUtcStr);
                ageMs = Math.round(receiveUtc - enqueuedUtc);
            } catch {
                ageMs = -1;
            }
        }

        // Inject configurable processing delay
        const delayMs = parseInt(process.env.PROCESSING_DELAY_MS || '0', 10);
        const start = Date.now();
        if (delayMs > 0) {
            await new Promise((resolve) => setTimeout(resolve, delayMs));
        }
        const processingMs = Date.now() - start;

        context.log(
            `QueueProcessed sequence=${sequence} ageMs=${ageMs} ` +
            `processingMs=${processingMs} instanceId=${instanceId} delayMs=${delayMs}`
        );
    },
});
