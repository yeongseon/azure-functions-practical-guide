const { readdirSync } = require('node:fs');
const { spawnSync } = require('node:child_process');

const files = readdirSync('test').filter(name => name.endsWith('.test.js'));
if (files.length === 0) {
    console.error('No test files found');
    process.exit(1);
}
const result = spawnSync(process.execPath,
    ['--test', '--test-reporter=tap', ...files.map(name => `test/${name}`)],
    { encoding: 'utf8' });
process.stdout.write(result.stdout || '');
process.stderr.write(result.stderr || '');
if (result.error) throw result.error;
const count = /^# tests (\d+)$/m.exec(result.stdout);
const emptyFiles = files.filter(name =>
    result.stdout.includes(`# Subtest: test/${name}\n`)).length;
const unexecuted = ['skipped', 'todo', 'cancelled'].reduce((total, name) => {
    const match = new RegExp(`^# ${name} (\\d+)$`, 'm').exec(result.stdout);
    return total + Number(match?.[1] ?? 0);
}, emptyFiles);
if (!count || Number(count[1]) <= unexecuted) {
    console.error('No tests executed');
    process.exit(1);
}
process.exit(result.status ?? 1);
