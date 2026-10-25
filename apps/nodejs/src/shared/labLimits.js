const { app } = require('@azure/functions');

function registerLabHttp(name, options) {
    if (process.env.LAB_ENDPOINTS_ENABLED === 'true') {
        app.http(name, { ...options, authLevel: 'function' });
    }
}

class LabInputError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
    }
}

function parseDelay(raw) {
    if (!/^[0-9]{1,5}$/.test(raw) || Number(raw) > 25000) {
        throw new LabInputError('delay_ms must be an integer from 0 to 25000');
    }
    return Number(raw);
}

function parseReplay(body) {
    if (Buffer.byteLength(body, 'utf8') > 4096) {
        throw new LabInputError('Request body exceeds 4096 bytes', 413);
    }
    let payload;
    try {
        payload = body ? JSON.parse(body) : {};
    } catch (error) {
        if (!(error instanceof SyntaxError)) throw error;
        throw new LabInputError('Expected a JSON object');
    }
    if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) {
        throw new LabInputError('Expected a JSON object');
    }
    const defaultIterations = process.env.DurableLab__Iterations ?? '100';
    const defaultContinue = process.env.DurableLab__ContinueAsNewEvery ?? '0';
    if (![defaultIterations, defaultContinue].every(value => /^[0-9]{1,4}$/.test(value))) {
        throw new LabInputError('Invalid DurableLab configuration', 503);
    }
    const instances = Object.hasOwn(payload, 'instances') ? payload.instances : 1;
    const iterations = Object.hasOwn(payload, 'iterations') ? payload.iterations : Number(defaultIterations);
    const continueEvery = Object.hasOwn(payload, 'continueAsNewEvery')
        ? payload.continueAsNewEvery : Number(defaultContinue);
    for (const [name, value, lower, upper] of [
        ['instances', instances, 1, 10],
        ['iterations', iterations, 1, 5000],
        ['continueAsNewEvery', continueEvery, 0, 5000],
    ]) {
        if (!Number.isSafeInteger(value) || value < lower || value > upper) {
            throw new LabInputError(`${name} must be an integer from ${lower} to ${upper}`);
        }
    }
    if (instances * iterations > 5000) {
        throw new LabInputError('instances * iterations must not exceed 5000');
    }
    return { instances, iterations, continueEvery };
}

module.exports = { registerLabHttp, LabInputError, parseDelay, parseReplay };
