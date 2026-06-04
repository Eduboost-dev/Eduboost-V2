# Phase 4 Ready: Expand Mathematics Grade R-7

**Date:** 2026-06-04  
**Branch:** `implementation/study-material-expansion-foundation`

## Status Update

### Completed
- ✅ Phase 0/1: Generalized scope validation and CI checks
- ✅ Phase 3: Expanded Grade 4 Mathematics from 3 to 21 CAPS refs

### Phase 4: Expand Mathematics Grade R-7

**Order of Priority:**
1. Grade 5 Mathematics (next wave)
2. Grade 6 Mathematics
3. Grade 3 Mathematics
4. Grade 2 Mathematics
5. Grade 1 Mathematics
6. Grade R Mathematics/Numeracy
7. Grade 7 Mathematics

## Current State

| Grade | Subject | CAPS Refs | Status | Content Generated |
|-------|---------|-----------|--------|-------------------|
| R | Mathematics | 0 | planned | No |
| 1 | Mathematics | 0 | planned | No |
| 2 | Mathematics | 0 | planned | No |
| 3 | Mathematics | 0 | planned | No |
| 4 | Mathematics | 21 | active | 3 refs only |
| 5 | Mathematics | 0 | planned | No |
| 6 | Mathematics | 0 | planned | No |
| 7 | Mathematics | 0 | planned | No |

## Next Steps

### Step 1: Update Scope Registry for Grade 5 Mathematics

1. Extract all CAPS refs from Grade 5 Mathematics topic map
2. Update `grade5_mathematics_en` scope in `scopes.json`
3. Create expansion manifest

### Step 2: Generate Content for Grade 5

1. Run `build_scope_content_artifacts.py` for grade5_mathematics_en
2. Validate generated content
3. Create promotion manifests

### Step 3: Repeat for Remaining Grades

Continue the pattern for Grades 3, 2, 1, R, and 7.

## Expected Content Volume

Per grade/subject/language scope:
- **Diagnostic items:** 40 items per CAPS ref × ~20 refs = ~800 items
- **Lessons:** 8 lessons per CAPS ref × ~20 refs = ~160 lessons
- **Blueprints:** 4 blueprints per CAPS ref × ~20 refs = ~80 blueprints
- **Study plans:** 1 template per CAPS ref × ~20 refs = ~20 templates

For 7 grades of Mathematics (assuming ~20 refs each):
- **Total items:** ~5,600
- **Total lessons:** ~1,120
- **Total blueprints:** ~560
- **Total study plans:** ~140

## Timeline Estimate

- **Phase 4.1 (Grade 5):** 1-2 days
- **Phase 4.2 (Grade 6):** 1-2 days
- **Phase 4.3 (Grade 3):** 1-2 days
- **Phase 4.4 (Grade 2):** 1-2 days
- **Phase 4.5 (Grade 1):** 1-2 days
- **Phase 4.6 (Grade R):** 1-2 days
- **Phase 4.7 (Grade 7):** 1-2 days

**Total Phase 4:** ~7-14 days of content generation

## Integration with Current System

All content will:
1. Follow the same schema as Grade 4 Mathematics
2. Use the same validation rules
3. Be marked as `review` status until educator approval
4. Include source document citations
5. Pass all automated quality gates

## Readiness

The infrastructure is ready:
- ✅ Scope registry supports multiple scopes
- ✅ Content generators are generalized
- ✅ Validation scripts work for any scope
- ✅ CI checks enforce governance
- ✅ Expansion manifests provide clear targets

**Ready to proceed with Phase 4.**

