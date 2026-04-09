const { app } = require('@azure/functions');
const os = require('os');
const dns = require('dns');
const { promisify } = require('util');

const dnsResolve = promisify(dns.resolve);

/**
 * Simulate slow response with configurable delay.
 * Query parameters: delay_ms (default 3000, max 25000).
 */
app.http('slowResponse', {
    methods: ['GET'],
    route: 'diagnostics/slow-response',
    handler: async (request, context) => {
        const delayMs = Math.min(parseInt(request.query.get('delay_ms') || '3000', 10), 25000);
        context.log(`Slow response endpoint requested (delay=${delayMs}ms)`);

        const start = Date.now();
        await new Promise((resolve) => setTimeout(resolve, delayMs));
        const elapsed = Date.now() - start;

        return {
            status: 200,
            jsonBody: {
                status: 'completed',
                requestedDelayMs: delayMs,
                actualDelayMs: elapsed,
            },
        };
    },
});

/**
 * Probe storage account access via managed identity.
 */
app.http('storageProbe', {
    methods: ['GET'],
    route: 'diagnostics/storage-probe',
    handler: async (request, context) => {
        const accountName = process.env.AzureWebJobsStorage__accountName || '';
        if (!accountName) {
            return {
                status: 500,
                jsonBody: { error: 'AzureWebJobsStorage__accountName not set' },
            };
        }

        context.log(`Storage probe requested (account=${accountName})`);
        const start = Date.now();

        try {
            const { DefaultAzureCredential } = require('@azure/identity');
            const { BlobServiceClient } = require('@azure/storage-blob');

            const clientId = process.env.AzureWebJobsStorage__clientId;
            const credential = new DefaultAzureCredential(clientId ? { managedIdentityClientId: clientId } : {});
            const blobClient = new BlobServiceClient(
                `https://${accountName}.blob.core.windows.net`,
                credential
            );

            const containers = [];
            for await (const container of blobClient.listContainers()) {
                containers.push(container.name);
            }
            const elapsed = Date.now() - start;

            context.log(`Storage probe succeeded (${elapsed}ms, ${containers.length} containers)`);
            return {
                status: 200,
                jsonBody: {
                    status: 'success',
                    account: accountName,
                    containers,
                    elapsedMs: elapsed,
                },
            };
        } catch (err) {
            const elapsed = Date.now() - start;
            context.error(`Storage probe failed: ${err.message} (${elapsed}ms)`);
            return {
                status: 502,
                jsonBody: {
                    status: 'error',
                    account: accountName,
                    error: err.constructor.name,
                    message: err.message,
                    elapsedMs: elapsed,
                },
            };
        }
    },
});

/**
 * Resolve a hostname and return the result for DNS troubleshooting.
 * Query parameters: host (required).
 */
app.http('dnsResolve', {
    methods: ['GET'],
    route: 'diagnostics/dns-resolve',
    handler: async (request, context) => {
        const host = request.query.get('host') || '';
        if (!host) {
            return {
                status: 400,
                jsonBody: { error: "Missing 'host' query parameter" },
            };
        }

        context.log(`DNS resolve requested (host=${host})`);
        const start = Date.now();

        try {
            const addresses = await dnsResolve(host);
            const elapsed = Date.now() - start;

            context.log(`DNS resolve succeeded: ${host} -> ${addresses} (${elapsed}ms)`);
            return {
                status: 200,
                jsonBody: {
                    status: 'resolved',
                    host,
                    addresses,
                    elapsedMs: elapsed,
                },
            };
        } catch (err) {
            const elapsed = Date.now() - start;
            context.error(`DNS resolve failed: ${host} -> ${err.message} (${elapsed}ms)`);
            return {
                status: 502,
                jsonBody: {
                    status: 'failed',
                    host,
                    error: err.message,
                    elapsedMs: elapsed,
                },
            };
        }
    },
});

/**
 * Probe managed identity token acquisition.
 */
app.http('identityProbe', {
    methods: ['GET'],
    route: 'diagnostics/identity-probe',
    handler: async (request, context) => {
        context.log('Identity probe requested');
        const start = Date.now();

        try {
            const { DefaultAzureCredential } = require('@azure/identity');

            const clientId = process.env.AzureWebJobsStorage__clientId;
            const identityType = clientId ? 'user-assigned' : 'system-assigned';
            const credential = new DefaultAzureCredential(clientId ? { managedIdentityClientId: clientId } : {});

            const token = await credential.getToken('https://storage.azure.com/.default');
            const elapsed = Date.now() - start;

            const expiresOn = new Date(token.expiresOnTimestamp).toISOString();

            context.log(`Identity probe succeeded (type=${identityType}, elapsed=${elapsed}ms)`);
            return {
                status: 200,
                jsonBody: {
                    status: 'success',
                    identityType,
                    clientId: clientId || null,
                    tokenAcquired: true,
                    tokenExpiresOn: expiresOn,
                    elapsedMs: elapsed,
                },
            };
        } catch (err) {
            const elapsed = Date.now() - start;
            context.error(`Identity probe failed: ${err.message} (${elapsed}ms)`);
            return {
                status: 502,
                jsonBody: {
                    status: 'error',
                    error: err.constructor.name,
                    message: err.message,
                    elapsedMs: elapsed,
                },
            };
        }
    },
});
