from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_current_user,
    get_profile_repository,
    get_question_repository,
    get_skill_repository,
    get_test_attempt_repository,
    get_test_repository,
)
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.test_attempt_repository import TestAttemptRepository
from app.repositories.test_repository import TestRepository
from app.schemas.test import (
    SubmitAttemptRequest,
    SubmitAttemptResponse,
    TestAttemptDetail,
    TestAttemptSummary,
    TestDetail,
    TestSummary,
    attempt_to_detail,
    attempt_to_summary,
    submit_response_from,
    test_to_detail,
    test_to_summary,
)
from app.services.test_service import (
    AttemptNotFoundError,
    ProfileRequiredError,
    TestNotFoundError,
    TestService,
)

router = APIRouter()


def _service(
    tests: TestRepository = Depends(get_test_repository),
    questions: QuestionRepository = Depends(get_question_repository),
    attempts: TestAttemptRepository = Depends(get_test_attempt_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
    skills: LearnerSkillRepository = Depends(get_skill_repository),
) -> TestService:
    return TestService(tests, questions, attempts, profiles, skills)


# Order matters: literal paths ("/attempts", "/attempts/{id}") must be
# registered before the wildcard "/{test_id}", or a request to /attempts
# would be matched as test_id="attempts".


@router.get("", response_model=list[TestSummary])
async def list_tests(
    current_user: dict = Depends(get_current_user),
    service: TestService = Depends(_service),
) -> list[TestSummary]:
    tests = await service.list_tests()
    return [test_to_summary(t) for t in tests]


@router.get("/attempts", response_model=list[TestAttemptSummary])
async def list_attempts(
    current_user: dict = Depends(get_current_user),
    service: TestService = Depends(_service),
) -> list[TestAttemptSummary]:
    attempts = await service.list_attempts(str(current_user["_id"]))
    return [attempt_to_summary(a) for a in attempts]


@router.get("/attempts/{attempt_id}", response_model=TestAttemptDetail)
async def get_attempt(
    attempt_id: str,
    current_user: dict = Depends(get_current_user),
    service: TestService = Depends(_service),
) -> TestAttemptDetail:
    try:
        attempt = await service.get_attempt(str(current_user["_id"]), attempt_id)
    except AttemptNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found"
        ) from exc
    return attempt_to_detail(attempt)


@router.get("/{test_id}", response_model=TestDetail)
async def get_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    service: TestService = Depends(_service),
) -> TestDetail:
    try:
        test, questions = await service.get_test_detail(test_id)
    except TestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found") from exc
    return test_to_detail(test, questions)


@router.post("/{test_id}/attempts", response_model=SubmitAttemptResponse)
async def submit_attempt(
    test_id: str,
    payload: SubmitAttemptRequest,
    current_user: dict = Depends(get_current_user),
    service: TestService = Depends(_service),
) -> SubmitAttemptResponse:
    try:
        result = await service.submit_attempt(str(current_user["_id"]), test_id, payload.answers)
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    except TestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found") from exc
    return submit_response_from(result)
