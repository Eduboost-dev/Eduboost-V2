# Post-deploy Smoke Checklist

Basic smoke checks to run after deploying a candidate to staging.

Run each check and record output in `docs/release/post_deploy_smoke_checklist.md` or
link the artifact into the release bundle.

Checks:

1. Deep health endpoint
   - Command: `curl -sS -f $STAGING_URL/api/v2/health/deep`
   - Expected: JSON with all monitored subsystems `ok`.

2. Login
   - Command: perform an auth flow for a test learner account and confirm JWT
     issuance and `/api/v2/me` details.

3. Lesson generation
   - Command: POST to lesson generation endpoint with a small payload and verify
     a valid lesson is returned and stored.

4. Consent grant flow
   - Command: perform consent grant and verify consent record exists and can be
     exported via POPIA export endpoints.

5. POPIA export
   - Command: Trigger the export path for a test account and verify file/record.

6. Basic UI smoke (login -> dashboard -> generate)
   - Command: run Playwright smoke script or a manual browser check.

7. Check critical headers/CORS
   - Command: verify `security` headers and `Access-Control-Allow-Origin` are set

Owners: record owner for each step next to the check when executed.
