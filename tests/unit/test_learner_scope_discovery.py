from unittest.mock import MagicMock
from app.services.content_learner_read_service import ContentLearnerReadService
from app.services.content_scope_registry import ContentScopeRegistry
from app.domain.content_scope import ContentScope, ContentScopeStatus

def test_list_learner_visible_scopes() -> None:
    registry = MagicMock(spec=ContentScopeRegistry)
    
    scope_active = ContentScope(
        scope_id="grade4_mathematics_en",
        grade=4,
        subject_code="math",
        subject="Mathematics",
        language="en",
        curriculum="caps",
        status=ContentScopeStatus.ACTIVE,
        phase="intermediate",
        caps_refs=["math_1"],
    )
    
    scope_review = ContentScope(
        scope_id="grade5_mathematics_en",
        grade=5,
        subject_code="math",
        subject="Mathematics",
        language="en",
        curriculum="caps",
        status=ContentScopeStatus.REVIEW,
        phase="intermediate",
        caps_refs=["math_2"],
    )
    
    registry.list_scopes.return_value = [scope_active, scope_review]
    
    service = ContentLearnerReadService(scope_registry=registry)
    
    scopes = service.list_learner_visible_scopes()
    
    assert len(scopes) == 1
    assert scopes[0]["scope_id"] == "grade4_mathematics_en"
    assert scopes[0]["grade"] == 4
    assert scopes[0]["subject_code"] == "math"
    assert scopes[0]["language"] == "en"
