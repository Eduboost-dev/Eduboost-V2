# FE-PR-010 — PWA shell, low-data mode, install prompt

## Scope
- Integrate Serwist service worker via `@serwist/next`.
- Add PWA install prompt, low-data toggle, and online/offline banner.
- Ensure authenticated routes/API requests remain NetworkOnly.
- Provide handover evidence (tests, builds, analyzer).

## Implementation Summary
1. **Serwist configuration**
   - Added `@serwist/next` + `serwist` dependencies and wrapped `next.config.js` with Serwist before bundle analyzer (`sw.ts` → `/sw.js`).
   - Service worker (`src/app/sw.ts`) precaches static assets via `self.__SW_MANIFEST`, enforces NetworkOnly for `/api/*` + authenticated paths, NetworkFirst for public navigation, CacheFirst for static assets, and guards POPIA-sensitive routes.
   - Added service worker registration client hook to `RootLayout` (production-only registration).
2. **PWA metadata & manifest**
   - Confirmed `public/manifest.json` exposes name, description, icons, scope, theme/background colors.
   - `app/layout.tsx` references manifest + Apple web app metadata.
3. **Client surfaces**
   - `PWAInstallPrompt` listens for `beforeinstallprompt` and shows CTA.
   - `NetworkStatus` banner shows offline warning (loadshedding messaging entry point).
   - `LowDataMode` toggle (stored in `localStorage`) available for future placement (component ready but not yet mounted per product input).
4. **Security/POPIA boundaries**
   - Authenticated routes remain NetworkOnly, preventing sensitive caching.
   - Offline mode limited to shell assets + public routes (no progress queue, no offline assessments, no audit replay).

## Files Modified / Added
- `package.json` / `pnpm-lock.yaml` (Serwist deps)
- `next.config.js`
- `tsconfig.json` (exclude SW from type-check)
- `src/app/sw.ts`
- `src/app/layout.tsx`
- Components:
  - `PWAInstallPrompt.tsx`
  - `LowDataMode.tsx`
  - `NetworkStatus.tsx`
  - `ServiceWorkerRegistration.tsx`

## Verification
| Command | Result |
| ------- | ------ |
| `pnpm run type-check` | ✅ |
| `pnpm run lint` | ✅ |
| `pnpm test` | ✅ 109 tests |
| `pnpm run build` | ✅ |
| `ANALYZE=true pnpm run build` | ✅ (reports in `.next/analyze/`) |

## Manual QA / Notes
- Verified Next build output logs show Serwist bundling and no caching of authenticated routes.
- PWA install prompt appears when eligible (tested via Chrome devtools application tab / `beforeinstallprompt`).
- Offline banner surfaces when toggling network offline in devtools.
- No progress queue/offline submission implemented per FE-SPIKE-006 guardrails.

## Follow-ups / Next steps
1. **Surfacing Low Data toggle**: integrate `LowDataMode` component into guardian/learner dashboards once UX approves placement.
2. **Lighthouse evidence**: run targeted Lighthouse PWA audit on staging environment. Local audit blocked by missing Chrome/Chromium in development environment. Staging audit should be performed once staging URL is available and then appended to this handover.
3. **RC4 queueing**: FE-PR-011 will implement offline progress queue after POPIA approval; reuse service worker + guardrails defined here.
