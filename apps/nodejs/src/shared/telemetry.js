/**
 * Configure telemetry and logging for the Azure Functions application.
 *
 * Sets up Azure Monitor OpenTelemetry when APPLICATIONINSIGHTS_CONNECTION_STRING
 * is available.
 */
const { settings } = require('./config');

function configureTelemetry() {
    const connectionString = process.env.APPLICATIONINSIGHTS_CONNECTION_STRING;

    if (connectionString) {
        try {
            const { useAzureMonitor } = require('@azure/monitor-opentelemetry');
            useAzureMonitor({ azureMonitorExporterOptions: { connectionString } });
            console.log(`Azure Monitor OpenTelemetry configured (mode=${settings.telemetryMode})`);
        } catch (err) {
            console.warn(`Failed to configure Azure Monitor: ${err.message}`);
        }
    } else {
        console.log(`APPLICATIONINSIGHTS_CONNECTION_STRING not set; using basic logging (mode=${settings.telemetryMode})`);
    }
}

module.exports = { configureTelemetry };
