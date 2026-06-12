# Multilingual Lesson Generation Status

**Date**: 2026-06-12  
**Status**: Verified  
**Languages Supported**: 4

---

## Supported Languages

| Language | Code | Status | Notes |
|----------|------|--------|-------|
| English | `en` | ✅ Verified | Primary language, full prompt templates |
| isiZulu | `zu` | ✅ Verified | Mathematical terms scaffolded, prompt templates exist |
| Afrikaans | `af` | ⚠️ Partial | Basic support, some prompts may lack nuance |
| isiXhosa | `xh` | ⚠️ Partial | Basic support, vocabulary coverage incomplete |

---

## Verification Results

### English (en) ✅

- **Test Date**: 2026-06-12
- **Prompt Template**: `app/modules/lessons/prompts/lesson_en.md`
- **Output Quality**: High, full lesson generation with structure
- **Fallback**: Works correctly when LLM is unavailable

### isiZulu (zu) ✅

- **Test Date**: 2026-06-12
- **Prompt Template**: `app/modules/lessons/prompts/lesson_zu.md`
- **Features**:
  - Mathematical terms in isiZulu (official vocabulary)
  - Scaffolding with English translations
  - Bilingual explanations
- **Output Quality**: Good, culturally appropriate

### Afrikaans (af) ⚠️

- **Test Date**: 2026-06-12
- **Prompt Template**: Uses English template with language prefix
- **Output Quality**: Moderate, some terms may need native speaker review
- **Known Gaps**:
  - Limited Afrikaans mathematical vocabulary
  - Some idioms may not translate well

### isiXhosa (xh) ⚠️

- **Test Date**: 2026-06-12
- **Prompt Template**: Uses English template with language prefix
- **Output Quality**: Basic, requires expansion
- **Known Gaps**:
  - Limited curriculum-aligned vocabulary
  - Less prompt engineering attention

---

## Language Detection & Routing

The system detects learner language preference via:

1. **Learner Profile**: `learner.language` field (enum)
2. **Request Override**: `language` field in lesson request
3. **Fallback**: Default to English if not specified

### Request Flow

```python
# In app/api_v2_routers/lessons.py
language = body.language or learner.language or "en"
prompt_template = load_prompt(f"lesson_{language}.md", default="lesson_en.md")
```

---

## Prompt Templates

Located in: `app/modules/lessons/prompts/`

| Template | Language | Status |
|----------|----------|--------|
| `lesson_en.md` | English | ✅ Complete |
| `lesson_zu.md` | isiZulu | ✅ Complete |
| `lesson_af.md` | Afrikaans | ⚠️ Partial |
| `lesson_xh.md` | isiXhosa | ⚠️ Partial |

---

## Known Issues

1. **Incomplete Vocabulary**: Afrikaans and isiXhosa lack full mathematical vocabularies
2. **Quality Variance**: Non-English outputs require native speaker review
3. **Fallback Handling**: When LLM output is low-quality, no graceful retry mechanism

---

## Recommendations

1. **Short-term**: Add native speaker review for Afrikaans outputs
2. **Medium-term**: Expand isiXhosa vocabulary with CAPS terminology
3. **Long-term**: Fine-tune models per language for better quality

---

## CI Smoke Test

Add to `.github/workflows/e2e.yml` to verify each language generates:

```yaml
- name: Test multilingual generation
  run: |
    for lang in en zu af xh; do
      curl -X POST http://localhost:8000/api/v2/lessons/generate \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"subject\": \"mathematics\", \"topic\": \"fractions\", \"language\": \"$lang\"}"
    done
```

---

## References

- Language enum: `app/models/__init__.py` → `Language`
- Prompt templates: `app/modules/lessons/prompts/`
- Lesson variants: `app/modules/lessons/lesson_variants.py`