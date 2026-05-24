# Diagnostic Item-Bank Policy Status

Generated at: `2026-05-24T20:43:58Z`
Commit: `072c0678b1090169f2dbaac61ebaef4d636856d6`

**Status:** `diagnostic-item-bank-policy-accepted`
**Policy:** `docs/architecture/diagnostic_item_bank_canonicality.yml`
**Decision:** `diagnostic_items-runtime-required`
**Canonical table:** `diagnostic_items`
**Supporting table:** `irt_items`
**Unresolved blocker:** `DIAG-SCORE-001`

## Policy markers

| Marker | Present |
|---|---:|
| `decision: diagnostic_items-runtime-required` | True |
| `canonical_item_bank: diagnostic_items` | True |
| `supporting_item_bank: irt_items` | True |
| `classification: runtime-required` | True |
| `expected_min_rows: 1` | True |
| `beta_blocking_when_empty: true` | True |
| `migration_action: seed-required` | True |
| `unresolved_blocker: DIAG-SCORE-001` | True |

## Runtime diagnostic_items references

| Path | Line | Excerpt |
|---|---:|---|
| `app/models/diagnostic_item.py` | 111 | `ORM representation of the diagnostic_items table.` |
| `app/models/diagnostic_item.py` | 117 | `__tablename__ = "diagnostic_items"` |
| `app/models/item_exposure.py` | 58 | `ForeignKey("diagnostic_items.item_id", ondelete="RESTRICT"),` |
| `app/services/curriculum/coverage.py` | 24 | `def detect_gaps(self, *, lessons: Iterable[Mapping[str, Any]], diagnostic_items: Iterable[Mapping[str, Any]]) -> list[CurriculumGap]:` |
| `app/services/curriculum/coverage.py` | 27 | `item_refs = {row.get("caps_reference") for row in diagnostic_items if row.get("caps_reference")}` |

## Blockers

- None

## No false-closure rules

- This policy does not close DIAG-SCORE-001.
- Empty `diagnostic_items` remains beta-blocking under DIAG-SCORE-001.
- This policy does not seed `diagnostic_items`.
- This policy does not prove scoring quality, item exposure correctness, or adaptive recommendation behavior.
- This policy supersedes the earlier attempted `irt_items`-canonical-only classification.
