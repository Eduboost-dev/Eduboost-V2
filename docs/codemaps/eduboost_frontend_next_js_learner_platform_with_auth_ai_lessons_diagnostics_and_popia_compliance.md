# EduBoost Frontend: Next.js Learner Platform with Auth, AI Lessons, Diagnostics & POPIA Compliance

A Next.js 15 TypeScript frontend featuring authentication flows, AI-generated lesson delivery, adaptive diagnostics with IRT scoring, gamification, parent dashboards with POPIA data rights, offline sync capabilities, and admin content factory tooling. Key entry points: login flow [1b], lesson generation [2c], diagnostic submission [3d], offline sync [5b], and parent data export [6c].

## Trace ID: 1
**Title:** Guardian Login → Learner Selection → Dashboard Navigation

**Description:** Authentication flow: form submission through JWT token storage, parent dashboard fetch, learner context initialization, and redirect to learner dashboard

**Motivation:**
EduBoost Frontend implements a guardian-centric authentication flow where parents/guardians authenticate and then select which learner to manage. The LoginPage component handles form submission with email/password credentials, calling AuthService.loginGuardian() which POSTs to /auth/login endpoint. The JWT access token is stored in localStorage via storeAccessToken() for subsequent authenticated requests. After successful authentication, the parent dashboard is fetched via ParentService.getDashboard() to retrieve the guardian's learner list and subscription info. The first learner from the dashboard is used to initialize the learner context via setLearner(), which triggers LearnerContext effect to persist the learner to localStorage and refresh state. Finally, the user is navigated to the dashboard via router.push("/dashboard"). This flow ensures secure authentication, proper session management, and seamless transition to the learner dashboard.

**Details:**
- **Execution Flow:** LoginPage component → Form submission handler → AuthService.loginGuardian() → fetchApi POST /auth/login → storeAccessToken() → Fetch parent dashboard → ParentService.getDashboard() → GET /parents/dashboard → Initialize learner context → setLearner() call → LearnerContext effect → localStorage.setItem() → refreshState() → Navigation → router.push("/dashboard")
- **Concurrency Safety:** Form submission is per-request. Token storage is synchronous. Dashboard fetch is async. Context updates are batched. No distributed locks needed
- **Covered Objects:** Authentication, JWT token storage, parent dashboard, learner context, localStorage, navigation
- **Timeouts:** Login request: ~200-500ms. Dashboard fetch: ~200-500ms. Context update: ~10-50ms. Total: ~410-1050ms
- **Migration Path:** From simple auth to guardian flow. Migration requires: 1) Add guardian login, 2) Implement learner selection, 3) Add context management, 4) Update navigation
- **Error Handling:** Login failures return 401. Dashboard errors logged. Context errors handled gracefully. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Store tokens securely. Validate credentials. Use HTTPS. Implement token refresh. Clear tokens on logout. Validate learner access

**Trace text diagram:**
```
Guardian Login Flow
├── LoginPage component <-- page.tsx:60
│   ├── Form submission handler <-- 1a
│   │   └── AuthService.loginGuardian() <-- 1b
│   │       └── fetchApi POST /auth/login <-- services.ts:72
│   │           └── storeAccessToken() <-- 1c
│   ├── Fetch parent dashboard <-- 1d
│   │   └── ParentService.getDashboard() <-- services.ts:181
│   │       └── GET /parents/dashboard
│   └── Initialize learner context <-- 1e
│       └── setLearner() call <-- page.tsx:92
│           └── LearnerContext effect <-- LearnerContext.tsx:65
│               ├── localStorage.setItem() <-- 1f
│               └── refreshState() <-- LearnerContext.tsx:68
└── Navigation <-- 1g
    └── router.push("/dashboard") <-- page.tsx:102
```

**Location ID: 1a**
- **Title:** Login Form Submission
- **Description:** User submits email/password credentials to authenticate as guardian
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:77

**Location ID: 1b**
- **Title:** API Login Request
- **Description:** POST to /auth/login endpoint with credentials
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:72

**Location ID: 1c**
- **Title:** JWT Token Storage
- **Description:** Store access token in localStorage for subsequent authenticated requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:77

**Location ID: 1d**
- **Title:** Fetch Parent Dashboard
- **Description:** Retrieve guardian's learner list and subscription info
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:84

**Location ID: 1e**
- **Title:** Initialize Learner Context
- **Description:** Set active learner in global context from first learner in dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:92

**Location ID: 1f**
- **Title:** Persist Learner to Storage
- **Description:** Save learner profile to localStorage for session persistence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:67

**Location ID: 1g**
- **Title:** Navigate to Dashboard
- **Description:** Redirect authenticated user to learner dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:102

### AI Guide: Guardian Login Flow

**Overview:** The guardian login flow authenticates parents/guardians and initializes learner context for dashboard navigation. This trace shows authentication, token storage, and context initialization.

**Key Components:**

1. **Login Form Submission (1a):** User submits credentials. Form handler processes. Authentication request.

2. **API Login Request (1b):** POST to /auth/login. Credential validation. JWT token response.

3. **JWT Token Storage (1c):** Store in localStorage. Session persistence. Authenticated requests.

4. **Fetch Parent Dashboard (1d):** Get learner list. Subscription info. Guardian data.

5. **Initialize Learner Context (1d):** Set active learner. Global context. State management.

6. **Persist Learner to Storage (1f):** localStorage.setItem(). Session persistence. Context sync.

7. **Navigate to Dashboard (1g):** router.push(). Redirect to dashboard. Navigation.

**Best Practices:**
- Store tokens securely
- Validate credentials
- Use HTTPS
- Implement token refresh
- Clear tokens on logout
- Validate learner access
- Handle errors gracefully

**Common Issues:**
- Login failures: Check credentials
- Token storage errors: Check localStorage
- Dashboard errors: Check API
- Context errors: Check state management
- Navigation errors: Check router

## Trace ID: 2
**Title:** AI Lesson Generation → Job Polling → Interactive Display → XP Award

**Description:** Lesson delivery flow: subject/topic selection triggers async generation job, polls for completion, caches result, displays interactive content, and awards gamification XP on completion

**Motivation:**
EduBoost Frontend implements async AI lesson generation with job polling for optimal user experience. When a user selects subject/topic in the UI, handleGenerate() is triggered, calling LearnerService.generateLesson() which POSTs to /lessons/generate. The backend accepts the async job and returns JobAcceptedResponse with a job_id. The frontend then calls waitForJobResult() which implements a polling loop at 500ms intervals, calling GET /jobs/{job_id} to check status until complete. Once the lesson is ready, cacheLessonSnapshot() stores it in localStorage for offline access. When the user completes the lesson, LearnerService.awardXP() POSTs to /gamification/award-xp to grant 35 XP. Finally, refreshState() calls Promise.all([getMastery, getGam]) to update the context with new XP/level. This async pattern prevents blocking the UI, provides progress feedback, and enables offline access.

**Details:**
- **Execution Flow:** User selects subject/topic in UI → handleGenerate() triggered → LearnerService.generateLesson() → POST /lessons/generate → Backend accepts async job → Returns JobAcceptedResponse → waitForJobResult() → Polling loop (500ms interval) → GET /jobs/{job_id} → Check status until complete → Lesson ready, cache & display → cacheLessonSnapshot() → Store in localStorage → User completes lesson → LearnerService.awardXP() → POST /gamification/award-xp → refreshState() → Promise.all([getMastery, getGam]) → Update context with new XP/level
- **Concurrency Safety:** Job polling is per-request. Caching is synchronous. XP award is atomic. Context updates are batched. No distributed locks needed
- **Covered Objects:** AI lesson generation, job polling, offline caching, gamification XP, context updates
- **Timeouts:** Lesson generation: ~1-5s. Polling: ~500ms intervals. Caching: ~10-50ms. XP award: ~200-500ms. Context update: ~200-500ms. Total: ~1.5-6.5s
- **Migration Path:** From sync to async generation. Migration requires: 1) Implement job polling, 2) Add caching, 3) Update UI for async, 4) Add XP award
- **Error Handling:** Generation failures logged. Polling timeouts handled. Caching errors logged. XP errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate lesson content. Cache securely. Award XP server-side. Validate completion. Check quotas. Filter sensitive data

**Trace text diagram:**
```
Lesson Generation Flow (Trace 2)
├── User selects subject/topic in UI
│   └── handleGenerate() triggered <-- page.tsx:42
│       └── LearnerService.generateLesson() <-- 2a
│           ├── POST /lessons/generate <-- 2b
│           │   └── Backend accepts async job
│           │       └── Returns JobAcceptedResponse
│           └── waitForJobResult() <-- 2c
│               └── Polling loop (500ms interval) <-- client.ts:188
│                   └── GET /jobs/{job_id} <-- 2d
│                       └── Check status until complete <-- client.ts:190
└── Lesson ready, cache & display
    ├── cacheLessonSnapshot() <-- 2e
    │   └── Store in localStorage <-- offlineSync.ts:69
    ├── User completes lesson
    │   └── LearnerService.awardXP() <-- 2f
    │       └── POST /gamification/award-xp <-- services.ts:141
    └── refreshState() <-- 2g
        └── Promise.all([getMastery, getGam]) <-- 2h
            └── Update context with new XP/level <-- LearnerContext.tsx:58
```

**Location ID: 2a**
- **Title:** Request Lesson Generation
- **Description:** Submit learner_id, subject, topic, and language to lesson generation service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:53

**Location ID: 2b**
- **Title:** POST Lesson Job
- **Description:** Backend accepts job and returns job_id for async processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:122

**Location ID: 2c**
- **Title:** Poll Job Until Complete
- **Description:** Poll /jobs/{job_id} endpoint every 500ms until lesson generation completes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:126

**Location ID: 2d**
- **Title:** Check Job Status
- **Description:** Fetch current job status and result payload from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:189

**Location ID: 2e**
- **Title:** Cache Lesson for Offline
- **Description:** Store generated lesson in localStorage for offline access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:66

**Location ID: 2f**
- **Title:** Award Completion XP
- **Description:** Grant 35 XP to learner for completing the lesson
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:104

**Location ID: 2g**
- **Title:** Refresh Learner State
- **Description:** Update mastery data and gamification profile from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:112

**Location ID: 2h**
- **Title:** Fetch Updated Progress
- **Description:** Parallel fetch of mastery scores and gamification profile
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:45

### AI Guide: AI Lesson Generation

**Overview:** Async AI lesson generation with job polling provides optimal user experience with progress feedback and offline caching. This trace shows generation, polling, caching, and XP award.

**Key Components:**

1. **Request Lesson Generation (2a):** Submit generation request. Learner parameters. Service call.

2. **POST Lesson Job (2b):** Backend accepts job. Returns job_id. Async processing.

3. **Poll Job Until Complete (2c):** Polling loop. 500ms intervals. Status check.

4. **Check Job Status (2d):** Fetch job status. Result payload. Completion check.

5. **Cache Lesson for Offline (2e):** Store in localStorage. Offline access. Sync later.

6. **Award Completion XP (2f):** Grant 35 XP. Gamification update. Server-side validation.

7. **Refresh Learner State (2g):** Update context. Mastery data. Gamification profile.

8. **Fetch Updated Progress (2h):** Parallel fetch. Efficiency. Context update.

**Best Practices:**
- Use async job pattern
- Poll at reasonable intervals
- Cache for offline access
- Award XP server-side
- Update context efficiently
- Handle timeouts gracefully
- Validate lesson content

**Common Issues:**
- Generation failures: Check backend
- Polling timeouts: Adjust intervals
- Caching errors: Check localStorage
- XP not awarded: Check service
- Context stale: Check refresh

## Trace ID: 3
**Title:** Diagnostic Assessment → IRT Scoring → Gap Analysis → Study Plan Update

**Description:** Adaptive diagnostic flow: fetch IRT-calibrated items, collect answers, submit for theta estimation, receive ranked knowledge gaps, update mastery context, and redirect to personalized study plan

**Motivation:**
EduBoost Frontend implements adaptive diagnostic assessments using IRT (Item Response Theory) for accurate ability estimation. The InteractiveDiagnostic component handles the assessment flow: handleStart() selects subject and calls DiagnosticService.getItems() which GETs /diagnostics/items to fetch IRT-calibrated items with difficulty parameters. handleAnswer() accumulates learner's selected options for each diagnostic item. On the final question, DiagnosticService.submit() POSTs to /diagnostics/submit for backend IRT theta estimation. The results display converts theta to mastery % using the formula ((theta + 3) / 6) * 100 for UI display, and shows ranked knowledge gaps. The DiagnosticPage wrapper's onComplete callback updates mastery in context and navigates to the study plan. This adaptive approach provides accurate ability measurement, personalized gap identification, and seamless transition to remediation.

**Details:**
- **Execution Flow:** InteractiveDiagnostic Component → handleStart() - subject selection → DiagnosticService.getItems() → fetchApi GET /diagnostics/items → Backend: IRT item selection → handleAnswer() - per-question flow → Accumulate answer in array → On final question: → DiagnosticService.submit() → POST /diagnostics/submit → Backend: IRT theta estimation → Results display → Convert theta to mastery % → Show ranked knowledge gaps → DiagnosticPage wrapper → onComplete callback → Update mastery in context → Navigate to study plan → LearnerContext state update
- **Concurrency Safety:** Item fetch is per-request. Answer accumulation is synchronous. Submit is atomic. Context updates are batched. No distributed locks needed
- **Covered Objects:** Adaptive diagnostics, IRT scoring, theta estimation, gap analysis, mastery conversion, study plan navigation
- **Timeouts:** Item fetch: ~200-500ms. Answer collection: ~1-5ms per item. Submit: ~500-1000ms. Theta conversion: ~1-5ms. Context update: ~200-500ms. Total: ~1-3s
- **Migration Path:** From static to adaptive diagnostics. Migration requires: 1) Implement IRT items, 2) Add adaptive selection, 3) Implement theta estimation, 4) Add gap analysis
- **Error Handling:** Item fetch errors logged. Submit errors logged. Theta conversion errors handled. Context errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate item content. Secure answer submission. Validate theta calculation. Protect learner data. Audit diagnostic results. Filter sensitive data

**Trace text diagram:**
```
Diagnostic Assessment Flow
├── InteractiveDiagnostic Component <-- InteractiveDiagnostic.tsx:15
│   ├── handleStart() - subject selection <-- InteractiveDiagnostic.tsx:43
│   │   └── DiagnosticService.getItems() <-- 3a
│   │       └── fetchApi GET /diagnostics/items <-- 3b
│   │           └── Backend: IRT item selection
│   ├── handleAnswer() - per-question flow <-- InteractiveDiagnostic.tsx:65
│   │   ├── Accumulate answer in array <-- 3c
│   │   └── On final question: <-- InteractiveDiagnostic.tsx:73
│   │       └── DiagnosticService.submit() <-- 3d
│   │           └── POST /diagnostics/submit <-- 3e
│   │               └── Backend: IRT theta estimation
│   └── Results display <-- InteractiveDiagnostic.tsx:91
│       ├── Convert theta to mastery % <-- 3f
│       └── Show ranked knowledge gaps <-- InteractiveDiagnostic.tsx:119
└── DiagnosticPage wrapper <-- page.tsx:8
    ├── onComplete callback <-- page.tsx:19
    │   ├── Update mastery in context <-- 3g
    │   └── Navigate to study plan <-- 3h
    └── LearnerContext state update
```

**Location ID: 3a**
- **Title:** Fetch Diagnostic Items
- **Description:** Retrieve adaptive assessment items for selected subject
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:52

**Location ID: 3b**
- **Title:** GET Diagnostic Items API
- **Description:** Backend returns IRT-calibrated items with difficulty parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:190

**Location ID: 3c**
- **Title:** Collect Answer
- **Description:** Accumulate learner's selected options for each diagnostic item
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:70

**Location ID: 3d**
- **Title:** Submit for IRT Scoring
- **Description:** POST answers to backend for theta estimation and gap identification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:81

**Location ID: 3e**
- **Title:** Diagnostic Submit Endpoint
- **Description:** Backend runs IRT algorithm to compute theta_after and ranked_gaps
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:207

**Location ID: 3f**
- **Title:** Convert Theta to Mastery %
- **Description:** Transform IRT theta score to 0-100 mastery percentage for UI display
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:40

**Location ID: 3g**
- **Title:** Update Mastery Context
- **Description:** Store computed mastery score in global learner context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/diagnostic/page.tsx:20

**Location ID: 3h**
- **Title:** Navigate to Study Plan
- **Description:** Redirect to personalized study plan page after diagnostic completion
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/diagnostic/page.tsx:21

### AI Guide: Diagnostic Assessment

**Overview:** Adaptive diagnostic assessments use IRT for accurate ability estimation and gap analysis. This trace shows item selection, answer collection, theta estimation, and study plan navigation.

**Key Components:**

1. **Fetch Diagnostic Items (3a):** Retrieve adaptive items. Subject selection. IRT-calibrated.

2. **GET Diagnostic Items API (3b):** Backend returns items. Difficulty parameters. Adaptive selection.

3. **Collect Answer (3d):** Accumulate answers. Per-question flow. Array storage.

4. **Submit for IRT Scoring (3d):** POST answers. Theta estimation. Gap identification.

5. **Diagnostic Submit Endpoint (3e):** Backend IRT algorithm. Compute theta_after. Ranked gaps.

6. **Convert Theta to Mastery % (3f):** Transform theta. 0-100 mastery. UI display.

7. **Update Mastery Context (3g):** Store in context. Global state. Mastery score.

8. **Navigate to Study Plan (3h):** Redirect to plan. Personalized path. Remediation.

**Best Practices:**
- Use IRT for accuracy
- Adaptive item selection
- Secure answer submission
- Validate theta calculation
- Display mastery clearly
- Update context efficiently
- Navigate to remediation

**Common Issues:**
- Item fetch errors: Check backend
- Submit failures: Check API
- Theta conversion errors: Check formula
- Context stale: Check update
- Navigation errors: Check router

## Trace ID: 4
**Title:** API Error Handling → Token Refresh → Retry Logic → Normalized Error Display

**Description:** Resilient API client: intercepts 401 errors, attempts token refresh via refresh endpoint, retries original request with new token, normalizes error responses into ApiError objects for consistent UI handling

**Motivation:**
EduBoost Frontend implements a resilient API client with automatic token refresh and normalized error handling. The fetchApi() entrypoint executes HTTP requests with JWT token in Authorization header. On response, parseJson() parses the payload. If status is 401 and retryOnUnauthorized is true, refreshAccessToken() is called, which POSTs to /auth/refresh with httpOnly cookie to get new access token. The new token is stored via storeAccessToken(). The original request is retried with the new token (retryOnUnauthorized=false to prevent infinite loops). If the response is not OK, normalizeApiError() transforms various backend error formats into consistent ApiError structure, parsing envelope.error, FastAPI detail strings, and validation errors. This resilient pattern provides seamless token refresh, consistent error handling, and improved user experience.

**Details:**
- **Execution Flow:** fetchApi() entrypoint → fetch(url, headers + JWT) → await parseJson(response) → Error handling branch → if (status === 401 && retryOnUnauthorized) → refreshAccessToken() → POST /auth/refresh → parseJson(response) → storeAccessToken(token) → Retry: fetchApi(endpoint, retryOnUnauthorized=false) → if (!response.ok) → throw new ApiError(normalizeApiError()) → normalizeApiError() helper → Parse envelope.error → Parse FastAPI detail string → Parse validation errors → Return NormalizedApiError
- **Concurrency Safety:** Token refresh is atomic. Retry is sequential. Error normalization is stateless. No distributed locks needed
- **Covered Objects:** API error handling, token refresh, retry logic, error normalization, JWT management
- **Timeouts:** API request: ~200-500ms. Token refresh: ~200-500ms. Retry: ~200-500ms. Error normalization: ~1-5ms. Total: ~400-1505ms
- **Migration Path:** From simple fetch to resilient client. Migration requires: 1) Add token refresh, 2) Implement retry logic, 3) Normalize errors, 4) Update error handling
- **Error Handling:** 401 errors trigger refresh. Refresh failures logged. Retry failures handled. Normalized errors thrown. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Use httpOnly cookies. Validate refresh tokens. Prevent infinite retries. Normalize errors safely. Filter sensitive data. Handle token expiry

**Trace text diagram:**
```
API Request Flow with Token Refresh
├── fetchApi() entrypoint <-- client.ts:146
│   ├── fetch(url, headers + JWT) <-- 4a
│   ├── await parseJson(response) <-- client.ts:159
│   └── Error handling branch
│       ├── if (status === 401 && retryOnUnauthorized) <-- 4b
│       │   └── refreshAccessToken() <-- 4c
│       │       ├── POST /auth/refresh <-- 4d
│       │       ├── parseJson(response) <-- client.ts:136
│       │       └── storeAccessToken(token) <-- 4e
│       ├── Retry: fetchApi(endpoint, retryOnUnauthorized=false) <-- 4f
│       └── if (!response.ok) <-- client.ts:166
│           └── throw new ApiError(normalizeApiError()) <-- 4g
│
└── normalizeApiError() helper <-- client.ts:90
    ├── Parse envelope.error <-- client.ts:93
    ├── Parse FastAPI detail string <-- 4h
    ├── Parse validation errors <-- client.ts:101
    └── Return NormalizedApiError <-- client.ts:122
```

**Location ID: 4a**
- **Title:** Execute API Request
- **Description:** Send HTTP request with JWT token in Authorization header
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:158

**Location ID: 4b**
- **Title:** Detect Token Expiry
- **Description:** Intercept 401 Unauthorized responses for automatic token refresh
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:161

**Location ID: 4c**
- **Title:** Attempt Token Refresh
- **Description:** POST to /auth/refresh with httpOnly cookie to get new access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:162

**Location ID: 4d**
- **Title:** Refresh Token Request
- **Description:** Backend validates refresh token cookie and issues new access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:131

**Location ID: 4e**
- **Title:** Store New Token
- **Description:** Update localStorage with fresh access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:142

**Location ID: 4f**
- **Title:** Retry Original Request
- **Description:** Re-execute failed request with new token (retryOnUnauthorized=false)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:163

**Location ID: 4g**
- **Title:** Normalize Error Response
- **Description:** Transform various backend error formats into consistent ApiError structure
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:167

**Location ID: 4h**
- **Title:** Extract Error Message
- **Description:** Parse FastAPI validation errors and detail strings into normalized format
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:98

### AI Guide: API Error Handling

**Overview:** Resilient API client with automatic token refresh and normalized error handling provides seamless user experience. This trace shows token refresh, retry logic, and error normalization.

**Key Components:**

1. **Execute API Request (4a):** Send HTTP request. JWT in header. Authorization.

2. **Detect Token Expiry (4b):** Intercept 401. Check retry flag. Trigger refresh.

3. **Attempt Token Refresh (4c):** POST to refresh. httpOnly cookie. New token.

4. **Refresh Token Request (4d):** Backend validates. Issue new token. Cookie-based.

5. **Store New Token (4e):** Update localStorage. Fresh token. Authenticated requests.

6. **Retry Original Request (4f):** Re-execute with new token. Prevent infinite loops. Sequential retry.

7. **Normalize Error Response (4g):** Transform errors. Consistent structure. ApiError object.

8. **Extract Error Message (4h):** Parse FastAPI errors. Detail strings. Validation errors.

**Best Practices:**
- Use httpOnly cookies
- Prevent infinite retries
- Normalize errors consistently
- Handle token expiry gracefully
- Log errors with context
- Filter sensitive data
- Validate refresh tokens

**Common Issues:**
- Token refresh failures: Check backend
- Infinite retries: Check retry flag
- Normalization errors: Check parsing
- 401 loops: Check refresh logic
- Error display: Check normalization

## Trace ID: 5
**Title:** Offline Lesson Completion → Queue → Online Detection → Backend Sync

**Description:** Offline-first sync: detect offline state, queue lesson completion events to localStorage, monitor online status, flush queued events to backend when connection restored

**Motivation:**
EduBoost Frontend implements offline-first sync for lesson completions to ensure functionality without network connectivity. The Lesson Page component checks network status via navigator.onLine before attempting lesson completion sync. If offline, queueLessonSync() is called via offlineSync.queueLessonSync(), which reads the current queue from localStorage, appends the event to the array, and persists to localStorage as JSON. When the sync service detects online status via flushOfflineLessonSync(), it verifies online status, reads queued events, and POSTs to backend sync endpoint via LearnerService.syncLessonResponses() which calls fetchApi("/lessons/sync"). The backend processes queued lesson completions and awards XP. Finally, the sync service clears the localStorage queue. This offline-first pattern ensures data integrity, seamless offline experience, and automatic sync when connectivity is restored.

**Details:**
- **Execution Flow:** Lesson Page Component → Check network status → Queue offline event → offlineSync.queueLessonSync() → Read current queue → Append event to array → Persist to localStorage → Sync Service (when online) → offlineSync.flushOfflineLessonSync() → Verify online status → Read queued events → POST to backend sync endpoint → LearnerService.syncLessonResponses() → fetchApi("/lessons/sync") → Clear localStorage queue
- **Concurrency Safety:** Queue operations are atomic. Online detection is synchronous. Sync is sequential. No distributed locks needed
- **Covered Objects:** Offline sync, localStorage queue, network detection, backend sync, lesson completion
- **Timeouts:** Network check: ~1-5ms. Queue operation: ~1-5ms. Sync operation: ~200-500ms. Total: ~202-510ms
- **Migration Path:** From online-only to offline-first. Migration requires: 1) Add network detection, 2) Implement queue, 3) Add sync service, 4) Handle conflicts
- **Error Handling:** Network errors logged. Queue errors handled. Sync errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate queued events. Encrypt localStorage. Handle conflicts. Validate sync results. Filter sensitive data. Audit sync operations

**Trace text diagram:**
```
Offline Lesson Completion Flow
├── Lesson Page Component
│   ├── Check network status <-- 5a
│   └── Queue offline event <-- 5b
│       └── offlineSync.queueLessonSync() <-- offlineSync.ts:35
│           ├── Read current queue <-- offlineSync.ts:36
│           ├── Append event to array <-- 5c
│           └── Persist to localStorage <-- 5d
│
└── Sync Service (when online)
    └── offlineSync.flushOfflineLessonSync() <-- offlineSync.ts:41
        ├── Verify online status <-- 5e
        ├── Read queued events <-- offlineSync.ts:47
        ├── POST to backend sync endpoint <-- 5f
        │   └── LearnerService.syncLessonResponses() <-- 5g
        │       └── fetchApi("/lessons/sync") <-- services.ts:135
        └── Clear localStorage queue <-- 5h
```

**Location ID: 5a**
- **Title:** Detect Offline State
- **Description:** Check navigator.onLine before attempting lesson completion sync
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:91

**Location ID: 5b**
- **Title:** Queue Offline Event
- **Description:** Add lesson completion event to localStorage sync queue
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:92

**Location ID: 5c**
- **Title:** Append to Queue
- **Description:** Add event to in-memory queue array
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:36

**Location ID: 5d**
- **Title:** Persist Queue to Storage
- **Description:** Serialize queue to localStorage as JSON
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:37

**Location ID: 5e**
- **Title:** Check Online Before Flush
- **Description:** Verify network connectivity before attempting sync
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:43

**Location ID: 5f**
- **Title:** Bulk Sync to Backend
- **Description:** POST queued events to /lessons/sync endpoint
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:52

**Location ID: 5g**
- **Title:** Sync Endpoint Call
- **Description:** Backend processes queued lesson completions and awards XP
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:134

**Location ID: 5h**
- **Title:** Clear Synced Queue
- **Description:** Remove successfully synced events from localStorage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:54

### AI Guide: Offline Sync

**Overview:** Offline-first sync ensures lesson completions work without network connectivity, with automatic sync when connection is restored. This trace shows queue management and backend sync.

**Key Components:**

1. **Detect Offline State (5a):** Check navigator.onLine. Network detection. Status check.

2. **Queue Offline Event (5b):** Add to sync queue. localStorage. Event persistence.

3. **Append to Queue (5c):** In-memory array. Event append. Queue management.

4. **Persist Queue to Storage (5d):** Serialize to JSON. localStorage. Data persistence.

5. **Check Online Before Flush (5e):** Verify connectivity. Network check. Sync trigger.

6. **Bulk Sync to Backend (5f):** POST queued events. Bulk operation. Backend sync.

7. **Sync Endpoint Call (5g):** Backend processing. XP award. Completion handling.

8. **Clear Synced Queue (5h):** Remove synced events. Queue cleanup. localStorage update.

**Best Practices:**
- Detect network status
- Queue events reliably
- Persist to localStorage
- Sync when online
- Handle conflicts
- Validate queued events
- Clear synced events

**Common Issues:**
- Network detection errors: Check navigator API
- Queue persistence errors: Check localStorage
- Sync failures: Check backend
- Conflicts: Implement resolution
- XP not awarded: Check sync

## Trace ID: 6
**Title:** Parent Dashboard → POPIA Data Export → Privacy Request Handling

**Description:** POPIA compliance flow: load parent trust dashboard with learner progress, trigger data export request, backend generates JSON/CSV bundle, display export status and download link

**Motivation:**
EduBoost Frontend implements POPIA (Protection of Personal Information Act) compliance features for data subject rights. The ParentDashboard component mounts and performs parallel data fetch: GET /parents/{id}/dashboard returns learner progress & IRT theta, and GET /parents/{id}/export returns export bundle links. Privacy action button clicks trigger export request handler which calls DataRightsService.exportLearner() to GET /popia/data-export/{id} with format parameter, causing the backend to generate JSON/CSV bundle. The UI updates with export filename and download availability. Erasure request handler calls DataRightsService.requestErasure() to POST /popia/deletion-request with audit reason, triggering audit log + deletion queue per POPIA Section 24 (right to be forgotten). This compliance flow ensures data subject rights, audit trails, and regulatory compliance.

**Details:**
- **Execution Flow:** ParentDashboard component mount → Parallel data fetch → GET /parents/{id}/dashboard → Returns learner progress & IRT theta → GET /parents/{id}/export → Returns export bundle links → Privacy action button click → Export request handler → DataRightsService.exportLearner() → GET /popia/data-export/{id} → Backend generates JSON/CSV → Update UI with filename → Erasure request handler → DataRightsService.requestErasure() → POST /popia/deletion-request → Audit log + deletion queue
- **Concurrency Safety:** Parallel fetch is concurrent. Export generation is async. Erasure is atomic. No distributed locks needed
- **Covered Objects:** POPIA compliance, data export, data erasure, parent dashboard, audit logs, deletion queue
- **Timeouts:** Dashboard fetch: ~200-500ms. Export fetch: ~200-500ms. Export generation: ~1-5s. Erasure request: ~200-500ms. Total: ~1.6-6.5s
- **Migration Path:** From basic dashboard to POPIA compliance. Migration requires: 1) Add export endpoints, 2) Implement erasure requests, 3) Add audit logging, 4) Update UI
- **Error Handling:** Fetch errors logged. Export errors logged. Erasure errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate guardian access. Audit all requests. Secure export generation. Validate erasure requests. Filter sensitive data. Comply with POPIA

**Trace text diagram:**
```
Parent Dashboard POPIA Compliance Flow
├── ParentDashboard component mount <-- ParentDashboard.tsx:16
│   ├── Parallel data fetch <-- 6a
│   │   ├── GET /parents/{id}/dashboard <-- 6b
│   │   │   └── Returns learner progress & IRT theta
│   │   └── GET /parents/{id}/export <-- services.ts:185
│   │       └── Returns export bundle links
│   └── Privacy action button click <-- ParentDashboard.tsx:57
│       ├── Export request handler <-- ParentDashboard.tsx:60
│       │   ├── DataRightsService.exportLearner() <-- 6c
│       │   │   └── GET /popia/data-export/{id} <-- 6d
│       │   │       └── Backend generates JSON/CSV
│       │   └── Update UI with filename <-- 6e
│       └── Erasure request handler <-- ParentDashboard.tsx:67
│           ├── DataRightsService.requestErasure() <-- 6f
│           └── POST /popia/deletion-request <-- 6g
│               └── Audit log + deletion queue
```

**Location ID: 6a**
- **Title:** Load Parent Dashboard
- **Description:** Parallel fetch of trust dashboard and export bundle for guardian
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:35

**Location ID: 6b**
- **Title:** Fetch Trust Dashboard
- **Description:** GET learner progress summaries, IRT theta, knowledge gaps, and AI insights
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:183

**Location ID: 6c**
- **Title:** Request Data Export
- **Description:** Trigger POPIA-compliant data export for specific learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:61

**Location ID: 6d**
- **Title:** Data Export API Call
- **Description:** GET /popia/data-export/{learnerId} with format parameter
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:164

**Location ID: 6e**
- **Title:** Display Export Status
- **Description:** Update UI with export filename and download availability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:62

**Location ID: 6f**
- **Title:** Request Data Erasure
- **Description:** POST erasure request under POPIA Section 24 (right to be forgotten)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:67

**Location ID: 6g**
- **Title:** Erasure Request API
- **Description:** POST /popia/deletion-request/{learnerId} with audit reason
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:166

### AI Guide: POPIA Data Export

**Overview:** POPIA compliance features enable data export and erasure for data subject rights. This trace shows parent dashboard, export generation, and erasure requests.

**Key Components:**

1. **Load Parent Dashboard (6a):** Parallel fetch. Trust dashboard. Export bundle.

2. **Fetch Trust Dashboard (6b):** GET learner progress. IRT theta. Knowledge gaps.

3. **Request Data Export (6c):** Trigger export. POPIA compliance. Learner-specific.

4. **Data Export API Call (6d):** GET export endpoint. Format parameter. JSON/CSV.

5. **Display Export Status (6e):** Update UI. Filename. Download availability.

6. **Request Data Erasure (6f):** POST erasure request. POPIA Section 24. Right to be forgotten.

7. **Erasure Request API (6g):** POST deletion endpoint. Audit reason. Deletion queue.

**Best Practices:**
- Validate guardian access
- Audit all requests
- Secure export generation
- Validate erasure requests
- Comply with POPIA
- Filter sensitive data
- Provide download links

**Common Issues:**
- Fetch errors: Check API
- Export failures: Check backend
- Erasure errors: Check validation
- Audit missing: Add logging
- Compliance issues: Verify POPIA

## Trace ID: 7
**Title:** App Initialization → Context Provider → localStorage Hydration → Route Guard

**Description:** Application bootstrap: root layout mounts LearnerProvider, reads persisted learner from localStorage, initializes global context, route guards check authentication state before rendering protected routes

**Motivation:**
EduBoost Frontend implements application bootstrap with context provider, localStorage hydration, and route guards for protected routes. The Root Layout (_app) mounts <LearnerProvider> wrapper which wraps the entire app in LearnerProvider for global state management. On mount, useEffect reads persisted learner from localStorage via localStorage.getItem(), JSON parses and sets learner via setLearner(), and calls refreshState() to fetch fresh state via Promise.all([...]) for mastery and gamification data. The Learner Layout (protected routes) checks if learner exists, and if not, uses <RouteGuard required="learner"> to evaluate route permission. RouteGuard checks allowed = Boolean(learner) and if not allowed, redirects via router.push("/"). The Parent Dashboard uses <RouteGuard required="parent"> with allowed = hasGuardianToken() and redirects to /login if not allowed. This bootstrap pattern ensures session persistence, protected routes, and proper authentication checks.

**Details:**
- **Execution Flow:** Root Layout (_app) → <LearnerProvider> wrapper → useEffect on mount → localStorage.getItem() → JSON.parse & setLearner() → refreshState() call → Promise.all([...]) → Learner Layout (protected routes) → if (!learner) check → <RouteGuard required="learner"> → allowed = Boolean(learner) → if (!allowed) → router.push("/") → Parent Dashboard (protected routes) → <RouteGuard required="parent"> → allowed = hasGuardianToken() → if (!allowed) → router.push("/login")
- **Concurrency Safety:** localStorage is synchronous. Context updates are batched. Route guards are deterministic. No distributed locks needed
- **Covered Objects:** App initialization, context provider, localStorage hydration, route guards, authentication checks
- **Timeouts:** localStorage read: ~1-5ms. JSON parse: ~1-5ms. Context update: ~10-50ms. State refresh: ~200-500ms. Route guard: ~1-5ms. Total: ~213-565ms
- **Migration Path:** From simple layout to guarded routes. Migration requires: 1) Add context provider, 2) Implement localStorage hydration, 3) Add route guards, 4. Update layouts
- **Error Handling:** localStorage errors handled gracefully. Parse errors logged. State refresh errors logged. Guard errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate localStorage data. Clear on logout. Check authentication. Protect routes. Validate tokens. Filter sensitive data

**Trace text diagram:**
```
Next.js App Initialization & Route Protection
├── Root Layout (_app) <-- layout.tsx:53
│   └── <LearnerProvider> wrapper <-- 7a
│       └── useEffect on mount <-- LearnerContext.tsx:30
│           ├── localStorage.getItem() <-- 7b
│           ├── JSON.parse & setLearner() <-- 7c
│           └── refreshState() call <-- 7d
│               └── Promise.all([...]) <-- LearnerContext.tsx:45
├── Learner Layout (protected routes) <-- layout.tsx:10
│   └── if (!learner) check <-- 7e
│       └── <RouteGuard required="learner"> <-- layout.tsx:21
│           ├── allowed = Boolean(learner) <-- 7f
│           └── if (!allowed) <-- RouteGuard.tsx:25
│               └── router.push("/") <-- 7g
└── Parent Dashboard (protected routes) <-- page.tsx:8
    └── <RouteGuard required="parent"> <-- page.tsx:12
        └── allowed = hasGuardianToken() <-- RouteGuard.tsx:22
            └── if (!allowed) <-- RouteGuard.tsx:25
                └── router.push("/login") <-- RouteGuard.tsx:26
```

**Location ID: 7a**
- **Title:** Mount Context Provider
- **Description:** Wrap entire app in LearnerProvider for global state management
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/layout.tsx:62

**Location ID: 7b**
- **Title:** Read Persisted Learner
- **Description:** Attempt to restore learner session from localStorage on mount
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:31

**Location ID: 7c**
- **Title:** Hydrate Learner State
- **Description:** Deserialize and set learner object in React context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:34

**Location ID: 7d**
- **Title:** Fetch Fresh State
- **Description:** Load latest mastery and gamification data from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:68

**Location ID: 7e**
- **Title:** Check Learner Session
- **Description:** Verify learner exists in context before rendering learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/layout.tsx:16

**Location ID: 7f**
- **Title:** Evaluate Route Permission
- **Description:** Check if user has required authentication for route (learner vs guardian)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:22

**Location ID: 7g**
- **Title:** Redirect Unauthorized
- **Description:** Navigate to login or home if authentication check fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:26

### AI Guide: App Initialization

**Overview:** Application bootstrap with context provider, localStorage hydration, and route guards ensures session persistence and protected routes. This trace shows initialization and authentication checks.

**Key Components:**

1. **Mount Context Provider (7a):** Wrap app in provider. Global state. Context management.

2. **Read Persisted Learner (7b):** localStorage.getItem(). Session restoration. Data persistence.

3. **Hydrate Learner State (7c):** JSON parse. setLearner(). Context update.

4. **Fetch Fresh State (7d):** refreshState() call. Promise.all(). Backend fetch.

5. **Check Learner Session (7e):** Verify learner exists. Protected routes. Authentication check.

6. **Evaluate Route Permission (7f):** Check required auth. Boolean evaluation. Permission logic.

7. **Redirect Unauthorized (7g):** router.push(). Login redirect. Access denied.

**Best Practices:**
- Use context providers
- Hydrate from localStorage
- Validate persisted data
- Protect routes with guards
- Check authentication
- Redirect appropriately
- Clear on logout

**Common Issues:**
- localStorage errors: Check storage
- Parse errors: Validate JSON
- Context stale: Check refresh
- Guard failures: Check logic
- Redirect loops: Check conditions

## Trace ID: 8
**Title:** Study Plan Generation → Job Polling → Schedule Normalization → Weekly View Render

**Description:** Personalized study plan flow: trigger async plan generation with gap_ratio parameter, poll job status, normalize schedule structure, render weekly calendar with gap-fill and grade-level activities

**Motivation:**
EduBoost Frontend implements personalized study plan generation with async job processing and schedule normalization. The plan page component mount triggers fetchPlan() callback which calls LearnerService.getStudyPlan() to POST /study-plans/generate with gap_ratio=0.4 for knowledge gap prioritization. The backend accepts the async job and waitForJobResult() polls /jobs/{job_id} until the plan is ready. The normalizeStudyPlan() function unifies days/schedule fields to handle backend variations in schedule field naming. The weekly calendar rendering extracts the schedule object, maps over days (Mon-Sun), gets items for each day, and renders study item cards with onClick handler to navigate to lesson with pre-filled subject and topic. The week_focus and grade info are displayed. This personalized approach provides adaptive scheduling, gap prioritization, and seamless lesson navigation.

**Details:**
- **Execution Flow:** Plan page component mount → fetchPlan() callback → LearnerService.getStudyPlan() → POST /study-plans/generate → Backend accepts job (gap_ratio=0.4) → waitForJobResult() polling → Poll /jobs/{job_id} until complete → normalizeStudyPlan() → Unify days/schedule fields → Render weekly calendar → Extract schedule object → Map over days (Mon-Sun) → Get items for each day → Render study item cards → onClick handler → router.push(lessonHref) → Display week_focus & grade info
- **Concurrency Safety:** Job polling is per-request. Normalization is stateless. Rendering is synchronous. No distributed locks needed
- **Covered Objects:** Study plan generation, job polling, schedule normalization, weekly calendar, gap prioritization
- **Timeouts:** Plan generation: ~1-3s. Polling: ~500ms intervals. Normalization: ~1-5ms. Rendering: ~10-50ms. Total: ~1.5-3.5s
- **Migration Path:** From static to personalized plans. Migration requires: 1) Implement job polling, 2) Add normalization, 3. Render calendar, 4) Add navigation
- **Error Handling:** Generation failures logged. Polling timeouts handled. Normalization errors logged. Rendering errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate plan data. Normalize safely. Render securely. Validate navigation. Filter sensitive data. Audit plan generation

**Trace text diagram:**
```
Study Plan Page Load
├── Plan page component mount
│   └── fetchPlan() callback <-- 8a
│       └── LearnerService.getStudyPlan()
│           ├── POST /study-plans/generate <-- 8b
│           │   └── Backend accepts job (gap_ratio=0.4) <-- services.ts:114
│           ├── waitForJobResult() polling <-- 8c
│           │   └── Poll /jobs/{job_id} until complete <-- client.ts:189
│           └── normalizeStudyPlan() <-- 8d
│               └── Unify days/schedule fields <-- services.ts:47
└── Render weekly calendar
    ├── Extract schedule object <-- 8e
    ├── Map over days (Mon-Sun) <-- page.tsx:142
    │   └── Get items for each day <-- 8f
    │       └── Render study item cards <-- page.tsx:165
    │           └── onClick handler <-- 8g
    │               └── router.push(lessonHref)
    └── Display week_focus & grade info <-- page.tsx:114
```

**Location ID: 8a**
- **Title:** Request Study Plan
- **Description:** Trigger study plan generation for learner based on diagnostic results
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:49

**Location ID: 8b**
- **Title:** POST Study Plan Job
- **Description:** Backend accepts async job with gap_ratio=0.4 for knowledge gap prioritization
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:112

**Location ID: 8c**
- **Title:** Poll Until Plan Ready
- **Description:** Wait for backend to compute personalized weekly schedule
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:116

**Location ID: 8d**
- **Title:** Normalize Schedule Format
- **Description:** Handle backend variations in schedule field naming (days vs schedule)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:45

**Location ID: 8e**
- **Title:** Extract Weekly Schedule
- **Description:** Get day-to-day activity mapping from normalized plan response
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:81

**Location ID: 8f**
- **Title:** Get Day Activities
- **Description:** Retrieve list of study items for each day of the week
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:143

**Location ID: 8g**
- **Title:** Navigate to Lesson
- **Description:** Click study item to start lesson with pre-filled subject and topic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:197

### AI Guide: Study Plan Generation

**Overview:** Personalized study plan generation with async job processing and schedule normalization provides adaptive scheduling. This trace shows generation, polling, normalization, and calendar rendering.

**Key Components:**

1. **Request Study Plan (8a):** Trigger generation. Diagnostic-based. Gap prioritization.

2. **POST Study Plan Job (8b):** Backend accepts job. gap_ratio=0.4. Async processing.

3. **Poll Until Plan Ready (8c):** Poll job status. Wait for completion. Ready check.

4. **Normalize Schedule Format (8d):** Unify fields. Handle variations. days vs schedule.

5. **Extract Weekly Schedule (8e):** Get schedule object. Day mapping. Activity data.

6. **Get Day Activities (8f):** Retrieve items. Per-day list. Study items.

7. **Navigate to Lesson (8g):** Click handler. router.push(). Pre-filled params.

**Best Practices:**
- Use async job pattern
- Poll at reasonable intervals
- Normalize schedule data
- Render calendar clearly
- Validate plan data
- Handle variations gracefully
- Provide clear navigation

**Common Issues:**
- Generation failures: Check backend
- Polling timeouts: Adjust intervals
- Normalization errors: Check fields
- Rendering errors: Check data
- Navigation errors: Check router
