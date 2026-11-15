# Astra-Health verification report

Verification performed in the build environment on the generated application source.

| Area | Result | Notes |
|---|---|---|
| Python syntax compilation | PASS | `python -m compileall -q app ml_engine` |
| Backend API tests | PASS | 9 tests passed, including auth, dataset import, 17-domain model status, input template, inference, probability-vector checks, persisted prediction history and missing-input rejection |
| Model loading | PASS | 17 champion domains; 5 fold pipelines per domain; 85 runtime artifacts loaded |
| ML inference | PASS | 17 domain outputs returned from a submitted integrated-dataset row |
| Probability vector integrity | PASS | All tested domain class-probability vectors summed to 1 within floating-point tolerance |
| Frontend JavaScript/JSX syntax | PASS | TypeScript transpiler parsed all 13 `.js`/`.jsx` source files without syntax diagnostics |
| Vite production build | NOT VERIFIED | The uploaded `node_modules` contained Windows-only native Rollup binaries. A clean `npm ci` was attempted, but package installation timed out in this environment. This is an environment/dependency-fetch limitation, not a passing build result. Run `npm install` then `npm run build` on the target machine. |

These checks establish software-level integration in the inspection environment. They do not validate clinical accuracy, calibration, real-world astronaut generalization, security for deployment or mission operational suitability.
