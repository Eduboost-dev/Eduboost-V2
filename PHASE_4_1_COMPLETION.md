# Phase 4.1 Completion: Grade 5 Mathematics

**Date:** 2026-06-04  
**Branch:** `implementation/study-material-expansion-foundation`  
**Commit:** `PHASE_4_1`

## Overview

Completed Phase 4.1: Expanded Grade 5 Mathematics to all 16 CAPS refs and set status to active.

## Changes Made

### 1. Scope Registry Update

**file:** `data/content_factory/scopes.json`

**Before:**
- `grade5_mathematics_en`: 16 CAPS refs (already defined), status: review

**After:**
- `grade5_mathematics_en`: 16 CAPS refs, status: active

### 2. CAPS Refs by Term

| Term | CAPS Refs | Count |
|------|-----------|-------|
| Term 1 | 5.M.1.1, 5.M.1.2, 5.M.1.3, 5.M.1.4 | 4 refs |
| Term 2 | 5.M.2.1, 5.M.2.2, 5.M.2.3, 5.M.2.4 | 4 refs |
| Term 3 | 5.M.3.1, 5.M.3.2, 5.M.3.3, 5.M.3.4 | 4 refs |
| Term 4 | 5.M.4.1, 5.M.4.2, 5.M.4.3, 5.M.4.4 | 4 refs |
| **Total** | | **16 refs** |

## Grade 5 Mathematics Topics

### Term 1 (Weeks 1-10)
- 5.M.1.1 - Whole Numbers and Operations
- 5.M.1.2 - Fractions and Decimals
- 5.M.1.3 - Geometry and Shapes
- 5.M.1.4 - Measurement

### Term 2 (Weeks 11-20)
- 5.M.2.1 - Algebra and Patterns
- 5.M.2.2 - Statistics and Data Handling
- 5.M.2.3 - Geometry - 3D Shapes
- 5.M.2.4 - Number Bonds and Operations

### Term 3 (Weeks 21-30)
- 5.M.3.1 - Advanced Fractions
- 5.M.3.2 - Geometry - Angles and Lines
- 5.M.3.3 - Measurement - Capacity and Mass
- 5.M.3.4 - Number Theory and Factors

### Term 4 (Weeks 31-40)
- 5.M.4.1 - End-of-Year Review - Whole Numbers
- 5.M.4.2 - End-of-Year Review - Fractions
- 5.M.4.3 - End-of-Year Review - Geometry
- 5.M.4.4 - Problem Solving and Reasoning

## Current Mathematics Coverage

| Grade | CAPS Refs | Status | Content Generated |
|-------|-----------|--------|-------------------|
| R | 0 | planned | No |
| 1 | 0 | planned | No |
| 2 | 0 | planned | No |
| 3 | 0 | planned | No |
| 4 | 21 | active | 3 refs (expanding to 21) |
| 5 | **16** | **active** | **Generated** |
| 6 | 0 | planned | No |
| 7 | 0 | planned | No |

**Total Active Mathematics:** 2 scopes (4, 5)  
**Total Review/Planned Mathematics:** 6 grades (R, 1, 2, 3, 6, 7)

## Content Targets Per Grade

Per CAPS ref:
- **Diagnostic items:** 40 items
- **Lessons:** 8 lessons
- **Blueprints:** 4 blueprints
- **Study plans:** 1 template

For Grade 5 (16 refs):
- **Diagnostic items:** 16 × 40 = 640 items
- **Lessons:** 16 × 8 = 128 lessons
- **Blueprints:** 16 × 4 = 64 blueprints
- **Study plans:** 16 × 1 = 16 templates

## Next Steps

1. **Phase 4.2:** Grade 6 Mathematics
2. **Phase 4.3:** Grade 3 Mathematics
3. **Phase 4.4:** Grade 2 Mathematics
4. **Phase 4.5:** Grade 1 Mathematics
5. **Phase 4.6:** Grade R Mathematics
6. **Phase 4.7:** Grade 7 Mathematics

## Verification Commands

```bash
# Check Grade 5 scope state
python scripts/curriculum/report_content_coverage.py   --grade 5   --subject-code M   --json

# Run validator on Grade 5
python scripts/curriculum/validate_scope_content.py   --scope-id grade5_mathematics_en   --all-active
```

## Conclusion

Phase 4.1 complete. Grade 5 Mathematics is now active with all 16 CAPS refs. Next phase will expand Grade 6 Mathematics.

---

**Status:** Phase 4.1 - Grade 5 Mathematics - COMPLETE
