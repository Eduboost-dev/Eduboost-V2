# Release Hygiene Checklist

Checklist to verify repository hygiene before creating a release candidate.

- [ ] Documentation links present and reachable (no broken local references)
- [ ] Generated artifacts are committed or reproducible via Make targets
- [ ] No hard-coded secrets in repository
- [ ] Alembic migration graph is linear and reviewed
- [ ] Evidence files referenced from `sign_off_manifest.md` are present
- [ ] Branch protection and required CI checks are configured (documented)
- [ ] PRs addressing release items include evidence commands and outputs
- [ ] Release bundle index has only real links and no false closures
- [ ] Known issues file is present and non-empty for beta-scope exclusions

Owners should sign off each checkbox with name and timestamp once verified.
