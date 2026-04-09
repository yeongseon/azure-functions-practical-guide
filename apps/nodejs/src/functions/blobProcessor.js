const { app, output } = require('@azure/functions');

const blobOutput = output.storageBlob({
    path: 'processed/{name}',
    connection: 'AzureWebJobsStorage',
});

/**
 * Triggered when a blob is uploaded to the 'uploads' container.
 *
 * Uses the Event Grid-based blob trigger (source: EventGrid) which is
 * required for Flex Consumption and recommended for all plans. The standard
 * polling blob trigger is NOT supported on Flex Consumption.
 *
 * Reads the blob content, transforms it (uppercase), and writes the result
 * to the 'processed' container under the same name.
 */
app.storageBlob('blobProcessor', {
    path: 'uploads/{name}',
    connection: 'AzureWebJobsStorage',
    source: 'EventGrid',
    return: blobOutput,
    handler: async (blob, context) => {
        context.log(`Processing blob: name=${context.triggerMetadata.name}, size=${blob.length} bytes`);

        // Transform: uppercase the content
        const content = Buffer.isBuffer(blob) ? blob : Buffer.from(blob);
        const transformed = content.toString('utf-8').toUpperCase();

        context.log(`Written to processed/${context.triggerMetadata.name}`);
        return Buffer.from(transformed);
    },
});
