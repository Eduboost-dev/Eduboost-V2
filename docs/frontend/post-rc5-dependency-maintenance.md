# Frontend Post-RC5 Dependency Maintenance

Track dependency triage and decisions after RC5.

| PR | Package | Ecosystem | Classification | Result | Notes |
|---:|---|---|---|---|---|
| #34 | peft 0.19.1 | pip / ML | needs-manual-review | blocked | Local install did not complete; pandas build failed under Python 3.14 path and WSL failed before Python 3.11 smoke could complete. Import/config smoke not run. Requires ML/staging validation. |
