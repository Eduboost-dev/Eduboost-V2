# Phase 2: Content Generation & Topic Map Approval

**Status**: Starting  
**Phase**: Content Generation & Database Seeding  
**Target Completion**: Production readiness for learner beta

---

## Overview

Phase 2 transforms validated CAPS curriculum maps into learner-ready educational content. This phase focuses on:

1. **Topic Map Human Review** - Curriculum experts validate 50 draft topic maps
2. **Topic Map Approval** - Mark maps as ready for content generation
3. **Content Generation** - LLM-based lesson creation with quality validation
4. **Database Import** - Seed lessons into learner database
5. **Quality Assurance** - Validate generated content meets pedagogical standards

---

## Prerequisites Met ✅

- **CAPS Sources**: 21/23 downloaded and extracted (91.3% coverage)
- **Topic Maps**: 50 draft maps generated and validated
- **Schema Validation**: All 51 maps pass JSON schema (1,663 topic refs)
- **Provenance Trail**: Complete tracking of all source materials
- **System Running**: Frontend, API, Database all operational
- **Documentation**: Startup guides and operational manuals complete

---

## Phase 2 Execution Plan

### STEP 1: Topic Map Review Framework

**Objective**: Establish structured review process for 50 draft topic maps

**Tasks**:
- [x] Create ../../curriculum/TOPIC_MAP_REVIEW_CHECKLIST.md with evaluation criteria
- [x] Define approval workflow (draft → review → approved → generation_ready)
- [x] Establish review roles (curriculum expert, content developer, QA)
- [x] Set up review tracking in Git
- [x] Add executable framework gate: `scripts/curriculum/check_topic_map_review_framework.py`

**Criteria for Approval**:
- Completeness: All CAPS topics from source document included
- Accuracy: Topic descriptions align with official CAPS specifications
- Hierarchy: Learning progression logical and sequenced correctly
- Scope: Grade-level and phase-appropriate scope definitions
- Coverage: No gaps in curriculum map

**Deliverable**: Review checklist and workflow documentation

**Current evidence refresh (2026-06-13)**:
- `docs/curriculum/TOPIC_MAP_REVIEW_CHECKLIST.md` contains the required checklist, status workflow, reviewer roles, tracking template, revision request template, and approval quality standards.
- `scripts/curriculum/check_topic_map_review_framework.py` verifies the review framework, topic-map inventory, registry status split, and source-manifest generation readiness.
- `.venv/bin/python scripts/curriculum/check_topic_map_review_framework.py` passed with 51 topic-map files, 50 review scopes, 1 active launch scope, and 51 generation-ready scopes.
- `.venv/bin/python -m pytest -q tests/unit/test_topic_map_review_framework.py --no-cov` passed.

---

### STEP 2: Manual Topic Map Review

**Objective**: Human validation of all 50 draft maps

**Scope**: 50 curriculum scopes across:
- Foundation Phase (Grade R, 1-3): 5 scopes
- Intermediate Phase (Grade 4-6): 20 scopes
- Senior Phase (Grade 7-9): 25 scopes

**Review Strategy**:
1. Group maps by subject area (5-6 subjects)
2. Assign to curriculum experts by domain
3. Run parallel reviews for efficiency
4. Document all feedback/revisions

**Success Criteria**:
- All 50 maps reviewed
- ≥95% pass rate (fewer than 3 maps need major revisions)
- All approval gates signed off

**Timeline**: 2-3 days with dedicated reviewers

**Deliverable**: Approved topic map manifest with signatures

---

### STEP 3: Content Generation Configuration

**Objective**: Set up lesson generation pipeline with quality gates

**Tasks**:
- [ ] Configure LLM providers (Anthropic Claude / Groq) in .env
- [ ] Implement quality validators for lesson content
- [ ] Set up batch generation parameters (concurrency, rate limits)
- [ ] Create content template specifications
- [ ] Set up logging and monitoring for generation

**Quality Validators Required**:
```python
# Each lesson must have:
✓ lesson_title: Clear, grade-appropriate title
✓ lesson_body: Structured lesson content (min 500 chars)
✓ scope_id: Valid reference to approved topic map
✓ variant: Content variant (standard, visual, kinesthetic)
✓ teacher_notes: Pedagogical guidance for instructors
✓ parent_notes: Take-home guidance for guardians
✓ extension_prompts: Challenge activities for advanced learners
✓ estimated_duration: Time estimate (in minutes)
✓ prerequisite_topics: Required prior knowledge
```

**LLM Prompts**:
- Topic-specific lesson generation
- Multi-sensory content variants (text, visual, kinesthetic)
- Teacher guidance extraction
- Parent-friendly summaries
- Extension challenges

**Deliverable**: Configured generation environment and validators

---

### STEP 4: Content Generation Execution

**Objective**: Generate learner-ready lessons for all approved topic maps

**Scope**: 50 approved scopes × 3 variants = ~150 lessons

**Generation Process**:
1. **Batch 1**: Foundation Phase (5 scopes × 3 variants = 15 lessons)
2. **Batch 2**: Intermediate Phase (20 scopes × 3 variants = 60 lessons)
3. **Batch 3**: Senior Phase (25 scopes × 3 variants = 75 lessons)

**Execution**:
- Run with quality validation enabled
- Monitor for generation failures
- Log all generation metadata (model used, tokens, timestamps)
- Collect generation statistics

**Expected Output**:
- ~150 lesson documents
- Complete generation logs
- Quality metrics report

**Deliverable**: Generated lessons in data/generated/lessons/

---

### STEP 5: Content Quality Assurance

**Objective**: Validate generated content meets pedagogical standards

**QA Checklist**:
- [ ] Lesson content quality (pedagogically sound, engaging, accurate)
- [ ] Grade-level appropriateness (language complexity, concepts)
- [ ] Completeness (all required fields populated)
- [ ] Consistency (formatting, structure, tone)
- [ ] Accuracy (factual correctness, no hallucinations)
- [ ] Tone & Voice (appropriate for learners and educators)

**QA Process**:
1. Automated validation (schema, required fields, length checks)
2. Sample manual review (10% of generated lessons)
3. Expert review (curriculum leader spot-checks)
4. Rejection criteria: Critical accuracy errors, incomplete content

**Pass Rate Target**: ≥98% (max 3 lessons rejected)

**Deliverable**: QA report with pass/fail metrics

---

### STEP 6: Database Import

**Objective**: Seed approved lessons into learner database

**Tasks**:
- [ ] Design lesson import schema
- [ ] Create bulk import script
- [ ] Run pre-import validation
- [ ] Execute database import transaction
- [ ] Verify data integrity post-import
- [ ] Create backup checkpoint

**Pre-Import Checks**:
- All lessons pass quality validation
- Database schema ready (migrations up-to-date)
- No data conflicts with existing records
- Backup created before import

**Import Process**:
```sql
INSERT INTO lessons (scope_id, title, body, variant, ...)
  SELECT ... FROM generated_lessons
  WHERE quality_status = 'approved'
```

**Post-Import Validation**:
- Row counts match expected
- All foreign key relationships valid
- Learner queries work correctly
- Performance benchmarks acceptable

**Deliverable**: Lessons imported and verified in database

---

### STEP 7: Smoke Testing & Beta Preparation

**Objective**: Verify learner interface works with real content

**Tests**:
- [ ] Frontend loads lesson list without errors
- [ ] Lesson detail pages render correctly
- [ ] Teacher notes accessible to educators
- [ ] Parent notes accessible to parents
- [ ] Search/filter by scope works
- [ ] Performance acceptable (load time <2s)
- [ ] Mobile rendering correct
- [ ] Offline viewing possible (if enabled)

**Beta Readiness Checks**:
- [ ] All systems green (frontend, API, DB)
- [ ] Monitoring configured
- [ ] Logging enabled
- [ ] Backup procedures tested
- [ ] Rollback procedures documented

**Deliverable**: Smoke test report and beta sign-off

---

## Timeline & Milestones

| Phase | Task | Duration | Owner | Status |
|-------|------|----------|-------|--------|
| 2.1 | Review framework setup | 0.5 days | Curriculum Lead | ✅ Done with executable evidence |
| 2.2 | Manual topic map review | 2-3 days | Subject Experts | ⏳ TODO |
| 2.3 | Generation config | 0.5 days | DevOps | ⏳ TODO |
| 2.4 | Content generation | 1-2 days | LLM Pipeline | ⏳ TODO |
| 2.5 | Quality assurance | 1 day | QA Team | ⏳ TODO |
| 2.6 | Database import | 0.5 days | DBA | ⏳ TODO |
| 2.7 | Smoke testing | 0.5 days | QA Team | ⏳ TODO |
| **Total** | **Phase 2 Duration** | **6-8 days** | **Cross-functional** | **Starting** |

---

## Success Criteria

Phase 2 is complete when:

- ✅ All 50 topic maps approved by curriculum leadership
- ✅ 150 lessons generated with quality validation
- ✅ ≥98% of generated content passes QA
- ✅ All lessons imported into database
- ✅ Smoke tests passing (frontend, API, learner interface)
- ✅ Documentation complete (generation logs, QA reports)
- ✅ Beta readiness confirmed

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Topic map review delays | Medium | High | Assign dedicated reviewers, schedule reviews now |
| LLM content quality issues | Medium | High | Implement strong quality validators, sample manual review |
| Database import conflicts | Low | High | Test with staging DB, create restore point |
| Performance degradation | Low | High | Run load testing before beta, optimize queries |
| Generation timeout/failure | Medium | Medium | Implement retry logic, monitor API quota usage |

---

## Blocking Issues & Dependencies

**Blocking Issues**: None identified

**Dependencies**:
- ✅ CAPS sources acquired (Phase 1 complete)
- ✅ Topic maps validated (Phase 1 complete)
- ✅ System infrastructure running (Phase 1 complete)
- ⏳ Curriculum expert availability (external dependency)
- ⏳ LLM API credentials configured (needs setup)

---

## Next Actions (Immediate)

1. **TODAY**: Create ../../curriculum/TOPIC_MAP_REVIEW_CHECKLIST.md
2. **TODAY**: Schedule curriculum review kickoff meeting
3. **TOMORROW**: Start manual topic map reviews (parallel by subject)
4. **THIS WEEK**: Configure LLM providers and implement validators
5. **NEXT WEEK**: Execute content generation and QA

---

## Communication & Handoff

**Stakeholders**:
- Curriculum Leadership: Topic map approval authority
- Content Team: Lesson quality validators
- DevOps: Infrastructure and LLM pipeline
- QA Team: Quality assurance and beta readiness
- Product: Beta readiness gate keeper

**Status Updates**: Daily standup with phase leads

**Sign-Off Required**:
- ✍️ Curriculum lead (topic maps approved)
- ✍️ QA lead (content quality validated)
- ✍️ Product lead (beta readiness confirmed)

---

## References

- **Topic Map Inventory**: [data/caps/topic_maps/](data/caps/topic_maps/)
- **Manifest**: [data/caps/source_documents/manifest.json](data/caps/source_documents/manifest.json)
- **Data Generation TODO**: [../../todos/data_generator_todo.md](../../todos/data_generator_todo.md)
- **Startup Guide**: [../../operations/SYSTEM_STARTUP_GUIDE.md](../../operations/SYSTEM_STARTUP_GUIDE.md)
- **Startup Report**: [../../operations/SYSTEM_STARTUP_REPORT.md](../../operations/SYSTEM_STARTUP_REPORT.md)

---

**Phase 2 Status**: 🚀 **READY TO START**

Current blockers: None  
Dependencies met: ✅ All Phase 1 prerequisites complete  
Team readiness: Awaiting stakeholder handoff  

**Next milestone**: Curriculum expert review kickoff
