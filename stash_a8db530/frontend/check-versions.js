
const fs = require('fs');
const path = require('path');

function getVersion(pkg) {
    try {
        const p = require.resolve(pkg + '/package.json', { paths: [process.cwd()] });
        return require(p).version;
    } catch (e) {
        return 'MISSING: ' + e.message;
    }
}

console.log('--- DEPENDENCY CHECK ---');
console.log('React:', getVersion('react'));
console.log('ReactDOM:', getVersion('react-dom'));
console.log('Next:', getVersion('next'));
console.log('Framer Motion:', getVersion('framer-motion'));

try {
    const xr = require.resolve('@react-three/xr/package.json', { paths: [process.cwd()] });
    console.log('@react-three/xr:', require(xr).version);
} catch (e) {
    console.log('@react-three/xr: NOT FOUND (GOOD)');
}

console.log('--- END CHECK ---');
