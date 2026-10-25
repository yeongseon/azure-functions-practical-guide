const { test } = require('node:test');
const assert = require('node:assert/strict');
const { app } = require('@azure/functions');
const df = require('durable-functions');
const { DurableClient } = require('durable-functions/lib/src/durableClient/DurableClient');

const routes = new Map();
app.http = (name, options) => routes.set(name, options);
df.app.orchestration = () => {};
df.app.activity = () => {};

function load(enabled) {
    routes.clear();
    delete process.env.LAB_ENDPOINTS_ENABLED;
    if (enabled !== undefined) process.env.LAB_ENDPOINTS_ENABLED = enabled;
    for (const file of ['diagnostics', 'durableLab', 'exceptions', 'health']) {
        const path = require.resolve(`../src/functions/${file}`);
        delete require.cache[path];
        require(path);
    }
}

test('lab routes are absent without exact opt-in; health remains anonymous', () => {
    for (const setting of [undefined, 'false', 'TRUE', '1']) {
        load(setting);
        assert.deepEqual([...routes.keys()], ['health']);
        assert.equal(routes.get('health').authLevel, 'anonymous');
    }
});

test('enabled lab HTTP routes require function authorization', () => {
    load('true');
    for (const [name, options] of routes) {
        if (name !== 'health') assert.equal(options.authLevel, 'function');
    }
    assert.ok(routes.has('startReplayLab'));
    assert.ok(routes.has('storageProbe'));
});

test('invalid starter input cannot schedule any work', async () => {
    load('true');
    let calls = 0;
    DurableClient.prototype.startNew = async () => { calls++; return 'instance'; };
    const bodies = ['{', '[]', 'null', '"text"', ' '.repeat(4097)];
    for (const field of ['instances', 'iterations', 'continueAsNewEvery']) {
        for (const value of [-1, 1.5, true, null, '100', 5001]) {
            bodies.push(JSON.stringify({ [field]: value }));
        }
    }
    bodies.push('{"instances":0}', '{"instances":11}', '{"iterations":0}',
        '{"iterations":1e400}', '{"instances":3,"iterations":2000}');
    for (const body of bodies) {
        const response = await routes.get('startReplayLab').handler(
            { text: async () => body }, { log() {} });
        assert.ok([400, 413].includes(response.status), body);
    }
    assert.equal(calls, 0);
});

test('documented incident and recovery workloads preserve explicit zero', async () => {
    load('true');
    process.env.DurableLab__ContinueAsNewEvery = '250';
    const inputs = [];
    DurableClient.prototype.startNew = async (_, options) => {
        inputs.push(options.input); return 'instance';
    };
    for (const reset of [0, 250]) {
        const response = await routes.get('startReplayLab').handler({ text: async () =>
            JSON.stringify({ instances: 1, iterations: 2000, continueAsNewEvery: reset }) }, {
                log() {},
                options: routes.get('startReplayLab'),
                extraInputs: { get: () => ({ taskHubName: 'test',
                    creationUrls: {}, managementUrls: {}, rpcBaseUrl: 'http://localhost/' }) },
            });
        assert.equal(response.status, 202);
        assert.equal(inputs.at(-1).continueAsNewEvery, reset);
    }
    delete process.env.DurableLab__ContinueAsNewEvery;
    assert.equal(inputs.length, 2);
});

test('invalid delay is rejected before sleeping', async () => {
    load('true');
    for (const value of ['-1', '25001', '1.5', 'NaN', 'Infinity', '', '1x']) {
        const response = await routes.get('slowResponse').handler(
            { query: new URLSearchParams({ delay_ms: value }) }, { log() {} });
        assert.equal(response.status, 400);
    }
});

test('probe responses omit backend errors, listings and identity identifiers', async (t) => {
    load('true');
    const { DefaultAzureCredential } = require('@azure/identity');
    const { BlobServiceClient } = require('@azure/storage-blob');
    const dns = require('dns');
    const logs = [];
    const context = { log() {}, error: (line) => logs.push(line) };
    t.mock.method(DefaultAzureCredential.prototype, 'getToken', async () => ({
        token: 'private-token', expiresOnTimestamp: 1800000000000,
    }));
    t.mock.method(BlobServiceClient.prototype, 'listContainers', () => ({
        byPage: () => ({ next: async () => ({ value: [{ name: 'private-container' }] }) }),
    }));
    process.env.AzureWebJobsStorage__accountName = 'examplestorage';
    process.env.AzureWebJobsStorage__clientId = 'private-identity-id';
    t.after(() => {
        delete process.env.AzureWebJobsStorage__accountName;
        delete process.env.AzureWebJobsStorage__clientId;
    });
    const storage = await routes.get('storageProbe').handler({}, context);
    assert.deepEqual(Object.keys(storage.jsonBody).sort(), ['elapsedMs', 'status']);
    const identity = await routes.get('identityProbe').handler({}, context);
    assert.equal(identity.status, 200);
    assert.ok(!JSON.stringify(identity).includes('private-'));
    t.mock.method(DefaultAzureCredential.prototype, 'getToken', async () => {
        throw new Error('private-backend-detail');
    });
    t.mock.method(BlobServiceClient.prototype, 'listContainers', () => {
        throw new Error('private-backend-detail');
    });
    t.mock.method(dns, 'resolve', (_, callback) => callback(new Error('private-backend-detail')));
    delete require.cache[require.resolve('../src/functions/diagnostics')];
    require('../src/functions/diagnostics');
    for (const name of ['storageProbe', 'identityProbe', 'dnsResolve']) {
        const response = await routes.get(name).handler({ query: new URLSearchParams({ host: 'example.com' }) }, context);
        assert.equal(response.status, 502);
        assert.ok(!JSON.stringify(response).includes('private-backend-detail'));
    }
    assert.equal(logs.length, 3);
    assert.ok(logs.every(line => line.includes('private-backend-detail')));
});

test('workload boundaries and environment defaults remain bounded', () => {
    const { parseReplay, parseDelay } = require('../src/shared/labLimits');
    assert.deepEqual(parseReplay('{"instances":10,"iterations":500,"continueAsNewEvery":5000}'),
        { instances: 10, iterations: 500, continueEvery: 5000 });
    assert.equal(parseDelay('0'), 0);
    assert.equal(parseDelay('25000'), 25000);
    for (const value of ['-1', '5001', '1x', 'Infinity', '1.5']) {
        process.env.DurableLab__Iterations = value;
        assert.throws(() => parseReplay(''));
    }
    delete process.env.DurableLab__Iterations;
});
