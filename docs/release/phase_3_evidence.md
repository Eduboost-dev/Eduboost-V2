# Phase 3 Evidence — Frontend Build and Test Health

Date: 2026-06-10

This file will collect before/after outputs and CI job snippets for Phase 3.

## To collect

- TypeScript errors before/after: `/tmp/phase3_tsc_before.txt`, `/tmp/phase3_tsc_after.txt`
- Vitest run before/after: `/tmp/phase3_vitest_before.txt`, `/tmp/phase3_vitest_after.txt`
- pnpm install verification: command and exit status
- CI job YAML snippet
- Lockfile diff and rationale (if lockfile changes are committed)

## Notes

- Implementation branch: `phase-3/frontend-build-and-test-health`
- Author: automated update by GitHub Copilot assistant

## Evidence placeholders

### TypeScript before

```
npm warn Unknown project config "shamefully-hoist". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.
npm warn Unknown project config "strict-peer-dependencies". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.
npm warn Unknown project config "auto-install-peers". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.
npm warn Unknown project config "lockfile". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.
Need to install the following packages:
tsc@2.0.4
Ok to proceed? (y) npm warn deprecated tsc@2.0.4: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

                                                                               
                This is not the tsc command you are looking for                
                                                                               

To get access to the TypeScript compiler,  tsc, from the command line either:

- Use  npm install typescript to first add TypeScript to your project  before using npx
- Use yarn to avoid accidentally running code from un-installed packages
```

### TypeScript after

```
<paste /tmp/phase3_tsc_after.txt here>
```

### Vitest before

```
<paste /tmp/phase3_vitest_before.txt here>
```

### Vitest after

```
<paste /tmp/phase3_vitest_after.txt here>
```

### pnpm install output (excerpt)

```
Lockfile is up to date, resolution step is skipped
Packages: +651
...
dependencies:
+ dexie 4.4.3
devDependencies:
+ typescript 5.4.5
Done in 1m 29.5s
FROZEN_FAILED
Lockfile is up to date, resolution step is skipped
Already up to date
Done in 2.8s
```

### dexie verification

- `dexie` was installed at `app/frontend/node_modules/dexie` (version 4.4.3). See `app/frontend/node_modules/dexie/package.json`.

> Note: I will append the full `tsc` and `vitest` "after" outputs once the local runs complete and I can capture their logs to `/tmp/phase3_tsc_after.txt` and `/tmp/phase3_vitest_after.txt`.

### CI job snippet

```yaml
# Frontend CI job
- name: Frontend Dependencies
  run: cd app/frontend && pnpm install --frozen-lockfile

- name: Frontend TypeScript
  run: cd app/frontend && npx tsc --noEmit --pretty false

- name: Frontend Tests
  run: cd app/frontend && npx vitest run --reporter=dot
```
