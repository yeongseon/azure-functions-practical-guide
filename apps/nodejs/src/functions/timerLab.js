const { app } = require('@azure/functions');

/**
 * Timer trigger for missed-schedules lab.
 *
 * Schedule is controlled by TIMER_LAB_SCHEDULE app setting.
 * Default should be set to '0 * /2 * * * *' (every 2 minutes).
 *
 * Logs isPastDue, schedule status, and instance ID for KQL evidence.
 */
app.timer('timerLab', {
    schedule: '%TIMER_LAB_SCHEDULE%',
    runOnStartup: false,
    handler: async (timer, context) => {
        const utcNow = new Date().toISOString();
        const instanceId = (process.env.WEBSITE_INSTANCE_ID || 'unknown').substring(0, 8);

        const isPastDue = timer.isPastDue;
        const scheduleLast = timer.scheduleStatus?.last || '';
        const scheduleNext = timer.scheduleStatus?.next || '';
        const lastUpdated = timer.scheduleStatus?.lastUpdated || '';

        context.log(
            `TimerFired isPastDue=${isPastDue} actualUtc=${utcNow} ` +
            `scheduleLast=${scheduleLast} scheduleNext=${scheduleNext} ` +
            `lastUpdated=${lastUpdated} instanceId=${instanceId}`
        );

        if (isPastDue) {
            context.warn(
                `TimerPastDue actualUtc=${utcNow} scheduleLast=${scheduleLast} instanceId=${instanceId}`
            );
        }
    },
});
