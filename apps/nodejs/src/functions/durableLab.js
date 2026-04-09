const df = require('durable-functions');
const { app } = require('@azure/functions');

/**
 * HTTP starter for the replay storm lab orchestrator.
 */
app.http('startReplayLab', {
    methods: ['POST'],
    route: 'durable/start-replay-lab',
    extraInputs: [df.input.durableClient()],
    handler: async (request, context) => {
        const client = df.getClient(context);
        const iterations = parseInt(process.env.DurableLab__Iterations || '100', 10);
        const continueAsNewEvery = parseInt(process.env.DurableLab__ContinueAsNewEvery || '0', 10);

        let payload = {};
        try {
            const body = await request.text();
            payload = body ? JSON.parse(body) : {};
        } catch {
            payload = {};
        }

        const instancesRequested = payload.instances || 1;
        const overrideIterations = payload.iterations || iterations;
        const overrideContinue = payload.continueAsNewEvery || continueAsNewEvery;

        const instanceIds = [];
        for (let i = 0; i < instancesRequested; i++) {
            const inputData = {
                iterations: overrideIterations,
                continueAsNewEvery: overrideContinue,
                batchIndex: 0,
                instanceIndex: i,
            };
            const instanceId = await client.startNew('replayStormOrchestrator', { input: inputData });
            instanceIds.push(instanceId);
            context.log(
                `Started replayStormOrchestrator instance ${instanceId} ` +
                `(${i + 1}/${instancesRequested}), iterations=${overrideIterations}, ` +
                `continueEvery=${overrideContinue}`
            );
        }

        return {
            status: 202,
            jsonBody: { started: instanceIds.length, instanceIds },
        };
    },
});

/**
 * Orchestrator that calls an activity N times to build history.
 * If continueAsNewEvery > 0, resets history periodically.
 */
df.app.orchestration('replayStormOrchestrator', function* (context) {
    const input = context.df.getInput();
    const totalIterations = input.iterations || 100;
    const continueEvery = input.continueAsNewEvery || 0;
    const batchIndex = input.batchIndex || 0;
    const instanceIndex = input.instanceIndex || 0;

    const completedSoFar = continueEvery > 0 ? batchIndex * continueEvery : 0;
    const remaining = totalIterations - completedSoFar;
    const iterationsThisBatch = continueEvery > 0
        ? Math.min(continueEvery, remaining)
        : remaining;

    const results = [];

    for (let i = 0; i < iterationsThisBatch; i++) {
        const globalIndex = completedSoFar + i;
        const result = yield context.df.callActivity('replayLabActivity', {
            index: globalIndex,
            instanceIndex,
        });
        results.push(result);
    }

    const totalCompleted = completedSoFar + iterationsThisBatch;

    if (continueEvery > 0 && totalCompleted < totalIterations) {
        if (!context.df.isReplaying) {
            context.log(
                `ContinueAsNew at iteration ${totalCompleted}/${totalIterations}, ` +
                `batch=${batchIndex}, resetting history`
            );
        }
        context.df.continueAsNew({
            iterations: totalIterations,
            continueAsNewEvery: continueEvery,
            batchIndex: batchIndex + 1,
            instanceIndex,
        });
        return;
    }

    if (!context.df.isReplaying) {
        context.log(
            `Orchestration complete: instance=${instanceIndex} total=${totalIterations} batches=${batchIndex + 1}`
        );
    }

    return {
        totalIterations,
        batches: batchIndex + 1,
        finalBatchResults: results.length,
    };
});

/**
 * Simple activity that simulates work and returns timing info.
 */
df.app.activity('replayLabActivity', {
    handler: (payload) => {
        const index = payload.index || 0;
        const instanceIndex = payload.instanceIndex || 0;

        const start = Date.now();
        // Simulate light work (5-15ms)
        let total = 0;
        for (let j = 0; j < 1000; j++) {
            total += j * j;
        }
        const elapsedMs = Date.now() - start;

        return {
            index,
            instanceIndex,
            elapsedMs,
        };
    },
});

/**
 * Check the status of a replay storm orchestration instance.
 */
app.http('checkReplayStatus', {
    methods: ['GET'],
    route: 'durable/status/{instanceId}',
    extraInputs: [df.input.durableClient()],
    handler: async (request, context) => {
        const client = df.getClient(context);
        const instanceId = request.params.instanceId;
        const status = await client.getStatus(instanceId);

        if (!status) {
            return {
                status: 404,
                jsonBody: { error: 'Instance not found' },
            };
        }

        return {
            status: 200,
            jsonBody: {
                instanceId: status.instanceId,
                runtimeStatus: status.runtimeStatus,
                createdTime: status.createdTime,
                lastUpdatedTime: status.lastUpdatedTime,
                output: status.output,
            },
        };
    },
});
