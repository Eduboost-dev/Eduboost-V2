# Frontend Route Inventory

## Purpose

This inventory records frontend route, page, and journey-related surfaces.

## Required Journey Areas

- learner onboarding
- learner dashboard
- diagnostic start and submit
- lesson generation and lesson view
- study plan or practice flow
- parent dashboard and learner progress
- consent and trust surfaces

## Discovered Surfaces

| Path | Route markers | Journey markers |
| --- | --- | --- |
| `app/frontend/.next/server/app/(auth)/login/page.js` | `Route, Routes, path:, href=, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(auth)/register/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/app/(auth)/register/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/badges/page.js` | `Route, Routes, path:` | `learner, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/dashboard/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page.js` | `Route, Routes, path:` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/lesson/page.js` | `Route, Routes, path:` | `learner, dashboard, lesson` |
| `app/frontend/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/parent/page.js` | `Route, Routes, path:, Link` | `learner, parent, progress` |
| `app/frontend/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/plan/page.js` | `Route, Routes, path:` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, Routes, path:` | `learner, parent, dashboard` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/_not-found/page.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/auth/reset-password/page.js` | `Route, Routes, path:, Link` | `learner, parent` |
| `app/frontend/.next/server/app/auth/reset-password/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/auth/verify-email/page.js` | `Route, Routes, path:, Link` | `onboarding` |
| `app/frontend/.next/server/app/auth/verify-email/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/onboarding/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/server/app/onboarding/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/parent-portal/page.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/settings/privacy/page.js` | `Route, Routes, path:` | `learner, parent, lesson` |
| `app/frontend/.next/server/app/settings/privacy/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/chunks/152.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/server/chunks/193.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/server/chunks/213.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/server/chunks/573.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/chunks/611.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/server/chunks/735.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/server/interception-route-rewrite-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/pages/_error.js` | `Route, Routes, path:, Link` | `_none_` |
| `app/frontend/.next/static/Ev0ZWNEk6TkAmI8QR6Hjw/_buildManifest.js` | `Route` | `_none_` |
| `app/frontend/.next/static/chunks/110-b6a694b2358caf7e.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/255-e881f48ae1d2333a.js` | `Route, Routes, path:, href=, Link` | `parent` |
| `app/frontend/.next/static/chunks/4bd1b696-409494caf8c83275.js` | `href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/644-903772fc124e9b53.js` | `Route, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/721-0f63de3333de4ce1.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/937-26ebe32dcb6a43aa.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/static/chunks/987-49423a66c656ed10.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/app/(auth)/login/page-fa55cc108f6133e1.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(auth)/register/page-87eab5025ee77943.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/badges/page-deb8a371ee7f8353.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/dashboard/page-e39194e186ed3e0c.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/diagnostic/page-be1ff8bee20047f4.js` | `Route` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/layout-06d951b1b4facaf3.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/(learner)/lesson/page-07d5cfa042b1f55d.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/static/chunks/app/(learner)/parent/page-85280db84f8c1a37.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/plan/page-372f9c26f163cf3a.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(parent)/parent-dashboard/page-e8f12b0072d7a06a.js` | `Route` | `learner, parent, dashboard` |
| `app/frontend/.next/static/chunks/app/auth/reset-password/page-4446babd70f05c52.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/auth/verify-email/page-2d93e84e0cd031aa.js` | `Route, Link` | `onboarding` |
| `app/frontend/.next/static/chunks/app/layout-7339cc506b777d0e.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/onboarding/page-14241f5f7eb03a60.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app/page-936aa7c633c15968.js` | `Route` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/parent-portal/page-b4d56510332a6007.js` | `Route` | `_none_` |
| `app/frontend/.next/static/chunks/app/settings/privacy/page-a31f02370646ebf8.js` | `_none_` | `learner, parent, lesson` |
| `app/frontend/.next/static/chunks/framework-1ce91eb6f9ecda85.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/main-973f463e1e1b3507.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/polyfills-42372ed130431b0a.js` | `path:, href=` | `parent` |
| `app/frontend/.next/static/chunks/webpack-8fdc395da7a0cd74.js` | `_none_` | `parent` |
| `app/frontend/.next/types/app/(learner)/badges/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(learner)/dashboard/page.ts` | `_none_` | `learner, dashboard` |
| `app/frontend/.next/types/app/(learner)/diagnostic/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/(learner)/lesson/page.ts` | `_none_` | `learner, lesson` |
| `app/frontend/.next/types/app/(learner)/parent/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/(learner)/plan/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(parent)/parent-dashboard/page.ts` | `_none_` | `parent, dashboard` |
| `app/frontend/.next/types/app/onboarding/page.ts` | `_none_` | `onboarding` |
| `app/frontend/.next/types/app/parent-portal/page.ts` | `_none_` | `parent` |
| `app/frontend/.next/types/routes.d.ts` | `Route, Routes` | `parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/types/validator.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/__tests__/BetaAndFeedback.test.tsx` | `Link` | `_none_` |
| `app/frontend/__tests__/EntryAndPortal.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, onboarding` |
| `app/frontend/__tests__/EntryScreens.test.tsx` | `_none_` | `learner, parent, onboarding` |
| `app/frontend/__tests__/FeaturePanels.test.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/InteractiveDiagnostic.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/InteractiveDiagnosticFlow.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/LegacyApiHelpers.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/__tests__/ParentDashboard.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/__tests__/RouteGuard.test.tsx` | `Route` | `learner, parent` |
| `app/frontend/__tests__/RoutingIntegration.test.tsx` | `Route, Routes` | `learner, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/__tests__/client.api.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/offlineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/services.coverage.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, consent` |
| `app/frontend/__tests__/services.smoke.test.ts` | `_none_` | `learner, lesson, diagnostic, consent` |
| `app/frontend/__tests__/setup.ts` | `_none_` | `diagnostic, progress` |
| `app/frontend/coverage/prettify.js` | `_none_` | `parent` |
| `app/frontend/coverage/sorter.js` | `_none_` | `parent` |
| `app/frontend/next-env.d.ts` | `Route, Routes` | `_none_` |
| `app/frontend/out/_next/static/XpSSIjQwjo18ZzODrsouJ/_buildManifest.js` | `Route` | `_none_` |
| `app/frontend/out/_next/static/chunks/110-cf8c53a9154f6e2b.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/out/_next/static/chunks/255-6ab3e064d17002d6.js` | `Route, Routes, path:, href=, Link` | `parent` |
| `app/frontend/out/_next/static/chunks/471-7c7751a26763e4c4.js` | `Route, path:, href=, Link` | `parent, progress` |
| `app/frontend/out/_next/static/chunks/4bd1b696-409494caf8c83275.js` | `href=, Link` | `parent, progress` |
| `app/frontend/out/_next/static/chunks/721-0f63de3333de4ce1.js` | `Link` | `_none_` |
| `app/frontend/out/_next/static/chunks/937-26ebe32dcb6a43aa.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/out/_next/static/chunks/987-49423a66c656ed10.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/out/_next/static/chunks/app/(auth)/login/page-0584797689560deb.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/out/_next/static/chunks/app/(auth)/register/page-32b1f59dfca0ef34.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/out/_next/static/chunks/app/(learner)/badges/page-23e62a2d3c5e6d48.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/out/_next/static/chunks/app/(learner)/dashboard/page-e39194e186ed3e0c.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/out/_next/static/chunks/app/(learner)/diagnostic/page-be1ff8bee20047f4.js` | `Route` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/out/_next/static/chunks/app/(learner)/layout-06d951b1b4facaf3.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/out/_next/static/chunks/app/(learner)/lesson/page-07d5cfa042b1f55d.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/out/_next/static/chunks/app/(learner)/parent/page-0ca0fd6de725e855.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/out/_next/static/chunks/app/(learner)/plan/page-4070a5e4d4d634a8.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/out/_next/static/chunks/app/(parent)/parent-dashboard/page-e8f12b0072d7a06a.js` | `Route` | `learner, parent, dashboard` |
| `app/frontend/out/_next/static/chunks/app/auth/reset-password/page-4446babd70f05c52.js` | `Route, Link` | `learner, parent` |
| `app/frontend/out/_next/static/chunks/app/auth/verify-email/page-2d93e84e0cd031aa.js` | `Route, Link` | `onboarding` |
| `app/frontend/out/_next/static/chunks/app/layout-cd93298710e9c7ea.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/out/_next/static/chunks/app/onboarding/page-14241f5f7eb03a60.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/out/_next/static/chunks/app/page-936aa7c633c15968.js` | `Route` | `learner, parent` |
| `app/frontend/out/_next/static/chunks/app/parent-portal/page-b4d56510332a6007.js` | `Route` | `_none_` |
| `app/frontend/out/_next/static/chunks/app/settings/privacy/page-a31f02370646ebf8.js` | `_none_` | `learner, parent, lesson` |
| `app/frontend/out/_next/static/chunks/framework-1ce91eb6f9ecda85.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/out/_next/static/chunks/main-b0cb6ac9689695b3.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/out/_next/static/chunks/polyfills-42372ed130431b0a.js` | `path:, href=` | `parent` |
| `app/frontend/out/_next/static/chunks/webpack-be264643d86c786e.js` | `_none_` | `parent` |
| `app/frontend/out/service-worker.js` | `_none_` | `parent, dashboard, lesson, diagnostic` |
| `app/frontend/public/service-worker.js` | `_none_` | `parent, dashboard, lesson, diagnostic` |
| `app/frontend/src/__tests__/AccessibilityContracts.test.tsx` | `Route, Link` | `learner, parent, dashboard, diagnostic, progress, consent` |
| `app/frontend/src/__tests__/ApiLayer.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/src/__tests__/DiagnosticContract.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/__tests__/LearnerJourneys.test.ts` | `_none_` | `learner, dashboard, lesson, progress` |
| `app/frontend/src/__tests__/OfflineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/app/(auth)/login/page.tsx` | `Route, href=, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/src/app/(auth)/register/page.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/app/(learner)/badges/page.tsx` | `_none_` | `learner, lesson, diagnostic, progress` |
| `app/frontend/src/app/(learner)/dashboard/page.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(learner)/diagnostic/page.tsx` | `Route` | `learner, dashboard, diagnostic` |
| `app/frontend/src/app/(learner)/layout.tsx` | `Route` | `learner, dashboard` |
| `app/frontend/src/app/(learner)/lesson/page.tsx` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/src/app/(learner)/parent/page.tsx` | `Link` | `learner, parent, progress` |
| `app/frontend/src/app/(learner)/plan/page.tsx` | `Route` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(parent)/parent-dashboard/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/admin/content-factory/page.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/app/auth/reset-password/page.tsx` | `Route, Routes, href=, Link` | `learner, parent` |
| `app/frontend/src/app/auth/verify-email/page.tsx` | `Route, Routes, href=, Link` | `onboarding` |
| `app/frontend/src/app/layout.tsx` | `_none_` | `learner` |
| `app/frontend/src/app/onboarding/page.tsx` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/src/app/page.tsx` | `Route` | `learner, parent` |
| `app/frontend/src/app/parent-portal/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/settings/privacy/page.tsx` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/components/ServiceWorkerRegistration.tsx` | `_none_` | `lesson` |
| `app/frontend/src/components/accessibility/A11y.tsx` | `href=, Link` | `_none_` |
| `app/frontend/src/components/admin/ETLAdminDashboard.tsx` | `path:` | `parent, lesson, assessment` |
| `app/frontend/src/components/admin/contentFactory/ContentFactoryLiveDashboard.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/components/admin/contentFactory/StagingProductionPreviewPanel.tsx` | `_none_` | `learner, lesson, diagnostic` |
| `app/frontend/src/components/admin/contentFactory/StagingReadinessPanel.tsx` | `href=` | `_none_` |
| `app/frontend/src/components/dashboard/course-card.tsx` | `href=, Link` | `parent, dashboard, lesson, progress` |
| `app/frontend/src/components/dashboard/metric-card.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/eduboost/BetaAndFeedback.tsx` | `href=` | `_none_` |
| `app/frontend/src/components/eduboost/EntryScreens.tsx` | `_none_` | `learner, parent, consent, onboarding` |
| `app/frontend/src/components/eduboost/ErrorBoundary.tsx` | `Route` | `dashboard` |
| `app/frontend/src/components/eduboost/FeaturePanels.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx` | `_none_` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/src/components/eduboost/InteractiveLesson.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/components/eduboost/ParentDashboard.tsx` | `href=, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/src/components/eduboost/RouteGuard.tsx` | `Route` | `learner, parent, dashboard` |
| `app/frontend/src/components/eduboost/ShellComponents.tsx` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/src/components/eduboost/api.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/components/eduboost/constants.ts` | `_none_` | `lesson` |
| `app/frontend/src/components/eduboost/styles.ts` | `_none_` | `parent, consent, onboarding` |
| `app/frontend/src/components/layout/dashboard-sidebar.tsx` | `href=, Link` | `parent, dashboard, assessment, progress` |
| `app/frontend/src/components/layout/dashboard-topbar.tsx` | `href=, Link` | `parent, dashboard, lesson` |
| `app/frontend/src/components/layout/marketing-footer.tsx` | `href=, Link` | `learner, parent` |
| `app/frontend/src/components/layout/marketing-header.tsx` | `href=, Link` | `parent` |
| `app/frontend/src/components/lessons/LessonTrustLabel.tsx` | `Link` | `parent, lesson` |
| `app/frontend/src/components/ui/badge.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui/breadcrumb.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui/button.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui/input.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui-shadcn/badge.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui-shadcn/breadcrumb.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui-shadcn/button.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui-shadcn/input.tsx` | `_none_` | `parent` |
| `app/frontend/src/context/LearnerContext.tsx` | `_none_` | `learner` |
| `app/frontend/src/lib/api/client.ts` | `_none_` | `learner, parent, consent` |
| `app/frontend/src/lib/api/contentFactory.ts` | `_none_` | `learner, lesson, diagnostic` |
| `app/frontend/src/lib/api/offlineSync.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/api/services.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/api/types.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/productionReadiness/contracts.ts` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/src/lib/utils.ts` | `_none_` | `progress` |
| `app/frontend/src/types/index.ts` | `_none_` | `parent, dashboard, lesson, assessment, progress` |

## Command

```bash
make frontend-route-inventory
```
