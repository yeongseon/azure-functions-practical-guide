const { app } = require('@azure/functions');

/**
 * Event Hub checkpoint lag lab.
 *
 * Demonstrates checkpoint lag accumulation when processing throughput
 * drops below ingestion throughput due to artificial processing delay.
 *
 * Configuration via app settings:
 * - EventHubLab__ArtificialDelayMs: artificial delay per batch (default: 0)
 * - EventHubLab__LogCheckpointDelta: log per-batch checkpoint info (default: true)
 */
app.eventHub('eventhubLagProcessor', {
    eventHubName: 'eh-lab-stream',
    connection: 'EventHubConnection',
    consumerGroup: 'cg-lab',
    cardinality: 'many',
    dataType: 'string',
    handler: async (events, context) => {
        const delayMs = parseInt(process.env.EventHubLab__ArtificialDelayMs || '0', 10);
        const logCheckpoint = (process.env.EventHubLab__LogCheckpointDelta || 'true').toLowerCase() === 'true';

        const batchStart = Date.now();
        const batchSize = events.length;
        const partitionIds = new Set();
        const sequenceNumbers = [];
        const enqueueTimes = [];

        for (let i = 0; i < batchSize; i++) {
            const event = events[i];
            const metadata = context.triggerMetadata?.partitionContext;
            if (metadata?.partitionId) {
                partitionIds.add(metadata.partitionId);
            }
            if (context.triggerMetadata?.sequenceNumberArray?.[i] !== undefined) {
                sequenceNumbers.push(context.triggerMetadata.sequenceNumberArray[i]);
            }
            if (context.triggerMetadata?.enqueuedTimeUtcArray?.[i]) {
                enqueueTimes.push(new Date(context.triggerMetadata.enqueuedTimeUtcArray[i]));
            }
        }

        // Apply artificial delay
        if (delayMs > 0) {
            await new Promise((resolve) => setTimeout(resolve, delayMs));
        }

        const elapsedMs = Date.now() - batchStart;
        const partitionId = partitionIds.size === 1
            ? [...partitionIds][0]
            : [...partitionIds].sort().join(',');

        if (logCheckpoint && sequenceNumbers.length > 0) {
            const minSeq = Math.min(...sequenceNumbers);
            const maxSeq = Math.max(...sequenceNumbers);

            let backlogAgeSec = 0;
            if (enqueueTimes.length > 0) {
                const now = new Date();
                const oldest = new Date(Math.min(...enqueueTimes.map((t) => t.getTime())));
                backlogAgeSec = Math.max(0, (now - oldest) / 1000);
            }

            context.log(
                `CheckpointDelta partition=${partitionId} batchSize=${batchSize} ` +
                `seqRange=[${minSeq}-${maxSeq}] backlogAgeSec=${backlogAgeSec.toFixed(1)} ` +
                `processingMs=${elapsedMs.toFixed(1)} delayMs=${delayMs}`
            );
        }

        if (batchSize > 0 && (batchSize >= 50 || elapsedMs > 1000)) {
            context.log(
                `Batch completed: partition=${partitionId} size=${batchSize} ` +
                `elapsed=${Math.round(elapsedMs)}ms delay=${delayMs}ms`
            );
        }
    },
});
